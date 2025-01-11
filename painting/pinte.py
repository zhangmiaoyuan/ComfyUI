import json
import random
import os
#This is an example that uses the websockets api and the SaveImageWebsocket node to get images directly without
#them being saved to disk

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse

from PIL import Image
import io

# 设置服务器地址和客户端ID
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

# 定义向服务器发送提示的函数
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())



# 定义从服务器下载图像数据的函数
def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()


# 定义获取历史记录的函数
def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())


# 定义通过WebSocket接收消息并下载图像的函数
def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
            # bytesIO = BytesIO(out[8:])
            # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images[node_id] = images_output

    return output_images

#
# workflow = r"./workflow/YingJIN_LORA.json"
# with open (workflow, "r",encoding="utf-8")as f:
#     prompt = f.read()
#     prompt = json.loads(prompt)
#
# #set the text prompt for our positive CLIPTextEncode
# prompt["6"]["inputs"]["text"] = "A close-up view of a banana in its natural state, highlighting its elongated shape, yellow color indicating ripeness, and smooth texture. The perspective is from an upward angle, emphasizing the top part of the banana including the stem."
#
# seed_number = random.randint(1, 999999999)
# #set the seed for our KSampler node
# prompt["25"]["inputs"]["noise_seed"] = seed_number
#
# # 创建一个WebSocket连接到服务器
# ws = websocket.WebSocket()
# ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
# # 调用get_images()函数来获取图像
# images = get_images(ws, prompt)
# # print(images)
# # image = Image.open(io.BytesIO(images))
# # image.show()
#
# id_images=uuid.uuid4()
#
# for node_id in images:
#     for image_data in images[node_id]:
#         image = Image.open(io.BytesIO(image_data))
#         image_home = f"./output/"
#         if not os.path.exists(image_home):
#             os.makedirs(image_home)
#         image.save(f"{image_home}/output_{seed_number}.png")



































