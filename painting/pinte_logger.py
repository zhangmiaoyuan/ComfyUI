import json
import random
import os
import websocket
import uuid
import json
import urllib.request
import urllib.parse
import logging
from PIL import Image
import io
import time

# 配置日志
logging.basicConfig(level=logging.INFO)  # 将默认日志级别改为INFO
logger = logging.getLogger(__name__)

# 设置服务器地址和客户端ID
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    try:
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        url = f"http://{server_address}/prompt"
        logger.info(f"Sending prompt to {url}")
        logger.debug(f"Prompt data: {p}")
        
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        logger.info(f"Prompt queued successfully, prompt_id: {result.get('prompt_id')}")
        return result
    except Exception as e:
        logger.error(f"Error in queue_prompt: {str(e)}")
        raise

def get_image(filename, subfolder, folder_type):
    try:
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        url = f"http://{server_address}/view?{url_values}"
        logger.info(f"Requesting image from {url}")
        
        with urllib.request.urlopen(url) as response:
            image_data = response.read()
            logger.info(f"Successfully downloaded image: {filename}")
            return image_data
    except Exception as e:
        logger.error(f"Error in get_image: {str(e)}")
        raise

def get_history(prompt_id):
    try:
        url = f"http://{server_address}/history/{prompt_id}"
        logger.info(f"Requesting history from {url}")
        
        with urllib.request.urlopen(url) as response:
            history = json.loads(response.read())
            logger.info(f"Successfully retrieved history for prompt_id: {prompt_id}")
            return history
    except Exception as e:
        logger.error(f"Error in get_history: {str(e)}")
        raise

def get_images(ws, prompt):
    try:
        # 设置WebSocket超时
        ws.settimeout(10)  # 10秒超时
        
        # 发送提示并获取prompt_id
        logger.info("Queueing prompt...")
        result = queue_prompt(prompt)
        prompt_id = result['prompt_id']
        logger.info(f"Prompt queued with ID: {prompt_id}")
        
        output_images = {}
        logger.info("Waiting for execution completion...")
        
        # 等待执行完成
        execution_start = time.time()
        timeout = 300  # 5分钟总超时
        last_progress = time.time()
        progress_timeout = 30  # 30秒无进度则认为完成
        
        while True:
            try:
                if time.time() - execution_start > timeout:
                    raise TimeoutError("Execution timeout after 5 minutes")
                
                if time.time() - last_progress > progress_timeout:
                    logger.info("No progress for 30 seconds, assuming completion")
                    break
                
                try:
                    out = ws.recv()
                except websocket.WebSocketTimeoutException:
                    continue
                
                if isinstance(out, str):
                    message = json.loads(out)
                    msg_type = message.get('type', '')
                    logger.debug(f"Received message type: {msg_type}")
                    
                    if msg_type == 'executing':
                        data = message['data']
                        logger.debug(f"Executing data: {data}")
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            logger.info("Execution completed")
                            break
                        last_progress = time.time()
                    elif msg_type in ['progress', 'executed', 'status']:
                        logger.info(f"{msg_type.capitalize()} update: {message.get('data', {})}")
                        last_progress = time.time()
                    elif msg_type == 'crystools.monitor':
                        # 忽略监控消息
                        continue
                else:
                    logger.debug("Received binary data (preview)")
                    continue
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to decode message: {e}")
                continue
            except Exception as e:
                logger.error(f"Error while receiving WebSocket message: {str(e)}")
                raise

        logger.info("Waiting 5 seconds for files to be written...")
        time.sleep(5)  # 等待文件写入完成
        
        # 获取执行历史
        logger.info(f"Retrieving history for prompt {prompt_id}")
        history = get_history(prompt_id)[prompt_id]
        logger.debug(f"History data: {history}")

        # 处理输出图像
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(root_dir, 'output')
        
        # 直接从output目录获取最新的图片
        all_images = []
        if os.path.exists(output_dir):
            for filename in sorted(os.listdir(output_dir), reverse=True):
                if filename.endswith('.png'):
                    all_images.append(filename)
                    if len(all_images) >= int(prompt.get('70', {}).get('inputs', {}).get('batch_size', 1)):
                        break
        
        if not all_images:
            logger.warning("No images were found in output directory!")
        else:
            logger.info(f"Found {len(all_images)} images: {all_images}")
            
        return all_images
        
    except Exception as e:
        logger.error(f"Error in get_images: {str(e)}")
        raise
