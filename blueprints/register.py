from flask import Blueprint, render_template, request, jsonify
import requests
import os
import sys
import logging
import uuid
import platform
import socket

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('register', __name__)

def get_system_info(save_to_file=False):
    """获取系统信息的函数，包含多种备选方案"""
    try:
        import os
        import uuid
        import platform
        import socket
        
        # 定义唯一标识符文件路径
        device_id_file = 'device_id.txt'
        
        # 获取主机名
        hostname = socket.gethostname()
        # 获取操作系统信息
        os_info = platform.system() + " " + platform.release()
        # 生成设备的唯一标识符，使用主机名和操作系统信息
        device_id = f"{hostname}-{os_info}"
        logger.info(f"Generated new device ID: {device_id}")
        
        # 只有在明确要求保存时才保存到文件
        if save_to_file:
            with open(device_id_file, 'w', encoding='utf-8') as f:
                f.write(device_id)
            logger.info(f"Saved device ID to file: {device_id}")
        
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

            # 获取表单数据
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': '注册数据无效'
                })
            
            # 转发注册请求到后端服务
            response = requests.post(
                'https://www.baiyaoyao.cn/gcai/register',
                # 'http://127.0.0.1:8888/gcai/register',
                json=data
            )
            result = response.json()
            
            # 如果注册成功，生成并保存设备码
            if result.get('success'):
                device_id = get_system_info(save_to_file=True)  # 生成并保存device_id
                logger.info(f"Registration successful, saved device ID: {device_id}")
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return jsonify({
                'success': False,
                'message': '注册服务暂时不可用，请稍后重试'
            })

    return render_template('register.html')

@bp.route('/get_mac', methods=['GET'])
def get_mac():
    try:
        device_id = get_system_info(save_to_file=True)  # 使用相同的设备标识符生成函数
        if device_id:
            return jsonify({
                'success': True,
                'mac_addresses': [device_id]  # 返回设备标识符
            })
        else:
            return jsonify({
                'success': False,
                'message': '无法获取设备标识符'
            })
    except Exception as e:
        logger.error(f"Error getting device ID: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })