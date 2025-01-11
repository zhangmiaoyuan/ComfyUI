from flask import Blueprint, request, jsonify, current_app, send_file
import os
import base64
from PIL import Image
import io
import json
import random
import websocket
import urllib.request
import urllib.parse
import time
import logging
from openai import OpenAI
from utils.ollama_translator import translate_to_english

# 设置日志级别为ERROR，只输出错误信息
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

bracelet_bp = Blueprint('bracelet01', __name__,url_prefix='/bracelet01')

def get_images(ws, prompt):
    try:
        ws.settimeout(10)
        
        # 记录生成开始时间
        generation_start_time = time.time()
        
        # 发送提示到ComfyUI服务器
        p = {"prompt": prompt, "client_id": "test-client"}
        data = json.dumps(p).encode('utf-8')
        result = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)).read()
        prompt_id = json.loads(result)['prompt_id']
        
        # 等待图片生成完成
        execution_start = time.time()
        last_progress = time.time()
        
        while True:
            if time.time() - execution_start > 300:  # 5分钟超时
                raise TimeoutError("Image generation timeout")
            
            if time.time() - last_progress > 30:  # 30秒无进度则认为完成
                break
            
            try:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message.get('type') == 'executing':
                        data = message['data']
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            break
                        last_progress = time.time()
                    elif message.get('type') in ['progress', 'executed']:
                        last_progress = time.time()
            except websocket.WebSocketTimeoutException:
                continue
        
        time.sleep(1)  # 等待文件写入，减少等待时间
        
        # 获取生成的图片
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(root_dir, 'output')
        batch_size = int(prompt.get('70', {}).get('inputs', {}).get('batch_size', 1))
        
        all_images = []
        if os.path.exists(output_dir):
            # 获取所有图片文件及其创建时间
            files_with_time = []
            for filename in os.listdir(output_dir):
                if filename.endswith('.png'):
                    file_path = os.path.join(output_dir, filename)
                    # 获取文件的创建时间
                    creation_time = os.path.getctime(file_path)
                    # 只添加在生成开始后创建的文件
                    if creation_time > generation_start_time:
                        files_with_time.append((filename, creation_time))
            
            # 按创建时间排序，获取最新的文件
            files_with_time.sort(key=lambda x: x[1], reverse=True)
            all_images = [f[0] for f in files_with_time[:batch_size]]
        
        return all_images
    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        raise

def generate_image(model_name, prompt_text, batch_size):
    ws = None
    try:
        # 将中文提示词翻译成英文
        english_prompt = translate_to_english(prompt_text)
        logger.info(f"English prompt: {english_prompt}")
        # print(english_prompt)
        
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        workflow_path = os.path.join(root_dir, 'workflow/001-bracelet', model_name)
        
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")
            
        with open(workflow_path, "r", encoding="utf-8") as f:
            prompt = json.loads(f.read())

        prompt["6"]["inputs"]["text"] = english_prompt
        prompt["25"]["inputs"]["noise_seed"] = random.randint(1, 999999999)
        prompt["70"]["inputs"]["batch_size"] = batch_size
        
        ws = websocket.WebSocket()
        ws.settimeout(900)
        ws.connect("ws://127.0.0.1:8188/ws?clientId=test-client")
        
        images = get_images(ws, prompt)
        return {'images': images}
    except Exception as e:
        logger.error(f"Image creation error: {str(e)}")
        raise
    finally:
        if ws:
            try:
                ws.close()
            except:
                pass

def generate_text_prompt(text):
    client = OpenAI(
        api_key="sk-e7d24a7b681442afb14455ef37f0f7c5",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {'role': 'system', 'content': 'You are a writer who can freely expand and depict a beautiful picture based on the given sentences.'},
            {'role': 'user', 'content': f'根据{text}，自动描绘一张有细节的画面，最后翻译成英文'}
        ]
    )
    return completion.choices[0].message.content

def summarize_and_format(final_prompt):
    client = OpenAI(
        api_key="sk-e7d24a7b681442afb14455ef37f0f7c5",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': f'According to the content description of {final_prompt},simplify the expression statement and do not delete the detailed description of the object.The example is as follows:he design is charming and kid-friendly, perfect for those who appreciate playful jewelry accessories..Theme: The bead reflects oriental design with influences from Japanese or Chinese art, characterized by its symmetrical and geometric patterns.Direction of View: It is viewed from above,providing a clear top-down perspective that highlights its intricate details.Shape: At the center is a heart shape, symbolizing love or passion, surrounded by complex geometric designs.Color: The bead has contrasting colors; the outer frame is dark (black or dark grey), while the central heart-shaped gemstone is pink, creating a striking contrast.Material: It appears to be made from metal, possibly gold with its golden hue, and includes darker elements that might be iron or steel with a blackened finish.Size: The bead is compact in size, making it suitable for various jewelry designs without being too large.Texture: While generally smooth, there are some raised and engraved details giving the bead a textured appearance.Other Observations: There are no inscriptions or additional gemstones except for the central pink stone, suggesting that this bead is intended to be a standout piece on its own.Translate all the above into both Chinese and English. First, display all the English, and then display the Chinese.'}
        ]
    )
    return completion.choices[0].message.content

def encode_image(image_data):
    return base64.b64encode(image_data).decode("utf-8")

def image_to_text(image_data):
    base64_image = encode_image(image_data)
    client = OpenAI(
        api_key="sk-e7d24a7b681442afb14455ef37f0f7c5",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    completion = client.chat.completions.create(
        model="qwen-vl-max-latest",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                    {"type": "text", "text": "What is the theme of this , which direction of view, shape, color, material, size, texture, etc?"},
                ],
            }
        ],
    )
    return summarize_and_format(completion.choices[0].message.content)

@bracelet_bp.route('/api/generate-text', methods=['POST'])
def generate_text():
    try:
        data = request.get_json()
        text = data.get('text')
        if not text:
            return jsonify({'error': '请提供文本'}), 400
        
        result = generate_text_prompt(text)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bracelet_bp.route('/api/image-to-text', methods=['POST'])
def process_image_to_text():
    try:
        if 'image' not in request.files:
            return jsonify({'error': '请上传图片'}), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        result = image_to_text(image_data)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bracelet_bp.route('/api/create-image', methods=['POST'])
def process_image_creation():
    try:
        data = request.json
        model_name = data.get('model')
        prompt_text = data.get('prompt')
        batch_size = int(data.get('batch', 1))
        
        if not model_name or not prompt_text:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        image_paths = generate_image(model_name, prompt_text, batch_size)
        return jsonify({'images': image_paths['images']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bracelet_bp.route('/api/get-models', methods=['GET'])
def get_models():
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_folder = os.path.join(root_dir, 'workflow/001-bracelet')
        
        if not os.path.exists(models_folder):
            logger.error(f"Models folder not found: {models_folder}")
            return jsonify({'error': 'Models folder not found'}), 404
            
        files = [f for f in os.listdir(models_folder) if f.endswith('.json')]
        return jsonify({'models': files})
    except Exception as e:
        logger.error(f"Error in get_models endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bracelet_bp.route('/output/<path:filename>')
def serve_image(filename):
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(root_dir, 'output', filename)
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404
        return send_file(image_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 404
