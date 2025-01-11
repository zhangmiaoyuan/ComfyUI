from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, send_file
from blueprints.bracelets03 import bracelets_bp
from blueprints.necklace04 import necklace_bp
from blueprints.bracelet01 import bracelet_bp
from blueprints.Earrings02 import Earrings_bp
from blueprints.ring05 import ring_bp
from blueprints.headwear07 import headwear_bp
from blueprints.gift06 import gift_bp
from blueprints.run_batch import run_batch_bp, runner
from blueprints.register import bp as register_bp
import os
from functools import wraps
from flask_cors import CORS, cross_origin
import requests
from datetime import timedelta
from lora_decrypt_manager import LoraDecryptManager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 Lora 解密管理器
lora_manager = LoraDecryptManager()

# 获取环境变量，默认为开发环境
ENV = os.getenv('FLASK_ENV', 'development')

app = Flask(__name__)
# 配置 CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
app.secret_key = 'zhang20241208'

# 配置 session，使其在浏览器关闭时失效
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=600)  # 设置会话超时时间为30分钟

# 添加output目录的静态文件路由
@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_file(os.path.join(app.root_path, 'output', filename))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# 注册所有蓝图
app.register_blueprint(bracelets_bp)
app.register_blueprint(necklace_bp)
app.register_blueprint(bracelet_bp)
app.register_blueprint(Earrings_bp)
app.register_blueprint(headwear_bp)
app.register_blueprint(ring_bp)
app.register_blueprint(gift_bp)
app.register_blueprint(run_batch_bp, url_prefix='/run_batch')
app.register_blueprint(register_bp)

# 配置上传文件路径
app.config['UPLOAD_FOLDER'] = 'output'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    # 如果是从其他页面跳转来的（非刷新），则清除会话
    if request.referrer is None or 'login' not in request.referrer:
        session.clear()
    return render_template('login.html')

def get_device_id():
    """获取设备码的函数"""
    try:
        # 使用相对路径，与 register.py 保持一致
        device_id_file = 'device_id.txt'
        if os.path.exists(device_id_file):
            with open(device_id_file, 'r', encoding='utf-8') as f:
                device_id = f.read().strip()
                if device_id:
                    logging.info(f"Using device ID: {device_id}")
                    return device_id
                logging.warning("Device ID file is empty")
        else:
            logging.warning("Device ID file not found")
        return None
    except Exception as e:
        logging.error(f"Error reading device ID: {e}")
        return None

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # 获取设备码
    device_id = get_device_id()
    if not device_id:
        return jsonify({
            'success': False,
            'need_register': True,
            'message': '未检测到设备码，请先完成注册。'
        })
    
    try:
        # 发送登录请求到后端服务
        response = requests.post(
            'https://www.baiyaoyao.cn/gcai/login',
            # 'http://127.0.0.1:8888/gcai/login',
            data={
                'username': username,
                'password': password,
                'mac_address': device_id
            }
        )
        data = response.json()
        
        if data.get('code') == 200:
            # 登录成功，保存会话信息
            session['logged_in'] = True
            session['user_id'] = data.get('user_id')
            session['username'] = username
            session['mac_address'] = device_id
            
            return jsonify({
                'success': True,
                'logged_in': True,
                'redirect_url': url_for('manage')
            })
        else:
            return jsonify({
                'success': False,
                'message': data.get('message', '登录失败，请检查用户名和密码')
            })
            
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': '登录服务暂时不可用，请稍后重试'
        })

@app.route('/manage')
@login_required
def manage():
    # 如果gradio还没有启动，先启动它
    if runner.gradio_port is None:
        runner.gradio_port = runner.find_free_port(7861, 7960)
        runner.demo = runner.create_gradio_interface()
        runner.demo.launch(
            server_name="127.0.0.1",
            server_port=runner.gradio_port,
            share=False,
            prevent_thread_lock=True
        )
        print(f"Gradio server running on port: {runner.gradio_port}")
    
    return render_template('manage.html', gradio_port=runner.gradio_port)

@app.route('/check_login')
def check_login():
    return jsonify({
        'logged_in': session.get('logged_in', False),
        'username': session.get('username', None)
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# 所有模板路由都需要登录
@app.route('/templates/001-bracelet/')
@login_required
def bracelet():
    return render_template('001-bracelet/index.html')

@app.route('/templates/002-Earrings/')
@login_required
def earrings():
    return render_template('002-Earrings/index.html')

@app.route('/templates/003-bracelets/')
@login_required
def bracelets():
    return render_template('003-bracelets/index.html')

@app.route('/templates/004-necklace/')
@login_required
def necklace():
    return render_template('004-necklace/index.html')

@app.route('/templates/005-ring/')
@login_required
def ring():
    return render_template('005-ring/index.html')

@app.route('/templates/006-gift/')
@login_required
def gift():
    return render_template('006-gift/index.html')

@app.route('/templates/007-headwear/')
@login_required
def headwear():
    return render_template('007-headwear/index.html')

# 添加before_request处理器来拦截所有请求
@app.before_request
def check_login_status():
    # 记录当前请求的路径
    logger.info(f"Accessing path: {request.path}")
    logger.info(f"Request endpoint: {request.endpoint}")
    
    # 不需要登录就能访问的路由列表
    public_endpoints = ['login_page', 'login', 'static', 'check_login', 'logout', 'shutdown']
    
    # 检查是否是注册相关的路由
    if request.path.startswith('/gcai/register') or request.path.startswith('/gcai/get_mac'):
        logger.info("Allowing access to registration endpoint")
        return None
        
    # 如果当前路由不是公开路由，且用户未登录，则重定向到登录页面
    if (request.endpoint not in public_endpoints and 
        not session.get('logged_in')):
        logger.info("Redirecting to login page")
        return redirect(url_for('login_page'))

@app.route('/shutdown', methods=['GET', 'OPTIONS'])
def shutdown():
    """处理服务器关闭请求，此端点不需要认证"""
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    print("Received shutdown request")
    errors = []
    
    try:
        # 首先执行清理
        try:
            lora_manager.cleanup()
        except Exception as e:
            errors.append(f"Lora cleanup error: {str(e)}")
            print(f"Error during lora cleanup: {e}")
        
        # 停止 run_batch 进程
        try:
            from blueprints.run_batch import runner, stop_command
            if runner.is_running:
                result = stop_command()
                print(f"Run batch stop result: {result}")
        except Exception as e:
            errors.append(f"Run batch stop error: {str(e)}")
            print(f"Error stopping run_batch: {e}")
            
        print("Cleanup completed, shutting down server...")
        
        # 关闭服务器
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        
        # 如果有错误但服务器关闭功能可用，仍然继续关闭
        if errors:
            func()
            return jsonify({
                "status": "partial_success",
                "message": "Server is shutting down with some errors",
                "errors": errors
            }), 207  # 207 Multi-Status
            
        func()
        return jsonify({"status": "success", "message": "Server is shutting down..."})
    except Exception as e:
        errors.append(str(e))
        print(f"Critical error during shutdown: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to shutdown server",
            "errors": errors
        }), 500

if __name__ == '__main__':
    # 启动后台解密线程
    lora_manager.start_decrypt()
    
    # 在生产环境中使用 0.0.0.0
    host = '0.0.0.0' if ENV == 'production' else '127.0.0.1'
    
    # 使用 werkzeug 的服务器
    from werkzeug.serving import run_simple
    
    # 启动 Flask 应用
    run_simple(
        host,
        5000,
        app,
        use_reloader=False,
        use_debugger=ENV == 'development',
        threaded=True
    )
