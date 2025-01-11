from flask import Blueprint, render_template, request, jsonify
import requests
import os
import sys
import logging
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('register', __name__)

def get_system_info():
    """获取系统信息的函数，包含多种备选方案"""
    try:
        import os
        import uuid
        
        # 定义唯一标识符文件路径
        device_id_file = 'device_id.txt'
        
        # 检查是否存在唯一标识符文件
        if os.path.exists(device_id_file):
            with open(device_id_file, 'r') as f:
                device_id = f.read().strip()  # 读取已存在的唯一标识符
                logger.info(f"Using existing device ID: {device_id}")
                return device_id
        
        # 生成设备的唯一标识符
        device_id = str(uuid.uuid1())  # 或者使用 uuid.uuid4() 生成随机 UUID
        logger.info(f"Generated new device ID: {device_id}")
        
        # 保存唯一标识符到文件
        with open(device_id_file, 'w', encoding='utf-8') as f:
            f.write(device_id)
        
        return device_id
    except Exception as e:
        logger.error(f"Error parsing system info: {e}")
        return None

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # 检查是否已经注册
            device_id_file = 'device_id.txt'
            if os.path.exists(device_id_file):
                # 检查文件内容
                with open(device_id_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # 如果文件有内容
                        return jsonify({
                            'success': False,
                            'message': '您已经注册过了，无法重复注册。'
                        })
                    else:  # 如果文件为空，删除文件
                        os.remove(device_id_file)
                        logger.info("Removed empty device_id.txt file")

            # 生成新的设备标识符
            device_id = str(uuid.uuid1())
            logger.info(f"Generated new device ID: {device_id}")

            # 获取表单数据
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': '注册数据无效'
                })
            
            # 转发注册请求到后端服务
            response = requests.post(
                'https://www.gcaizhubao.cn/gcai/register',
                # 'http://127.0.0.1:8888/gcai/login',
                json=data
            )
            result = response.json()
            
            # 如果注册成功，保存设备码
            if result.get('success'):
                with open(device_id_file, 'w', encoding='utf-8') as f:
                    f.write(device_id)
                logger.info(f"Saved new device ID: {device_id}")
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return jsonify({
                'success': False,
                'message': '注册服务暂时不可用，请稍后重试'
            })

    return render_template('register.html')

@bp.route('/register/get_mac', methods=['GET'])
def get_mac():
    try:
        # 获取系统标识
        system_id = get_system_info()
        logger.info(f"Retrieved system ID: {system_id}")
        
        if not system_id:
            return jsonify({
                'success': False,
                'message': '无法获取设备标识'
            })

        return jsonify({
            'success': True,
            'mac_addresses': [system_id]
        })
    except Exception as e:
        logger.error(f"Error in get_mac route: {e}")
        return jsonify({
            'success': False,
            'message': f'获取设备标识失败：{str(e)}'
        })
