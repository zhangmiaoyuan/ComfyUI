# 导入需要的库
import gradio as gr  # 用于创建Web界面
import subprocess   # 用于执行命令
import threading    # 用于创建线程
import queue       # 用于在线程间传递数据
import time        # 用于添加延时
from flask import Blueprint
import socket
import os

# 创建Flask蓝图
run_batch_bp = Blueprint('run_batch', __name__)

# 创建一个全局变量来控制进程
class CommandRunner:
    def __init__(self):
        self.process = None        # 存储运行的进程
        self.is_running = False    # 控制运行状态
        self.gradio_port = None    # 存储Gradio服务器端口
        self.demo = None          # 存储Gradio界面实例

# 创建全局的运行器实例
runner = CommandRunner()

def find_free_port(start_port=7860, max_port=7960):
    """查找可用端口"""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('', port))
                return port
            except OSError:
                continue
    raise OSError("No free ports available")

def run_command():
    """
    运行Python命令并实时显示输出
    这个函数会执行 .\python\python.exe -s main.py --windows-standalone-build
    并将输出实时显示在界面上
    """
    try:
        # 设置运行状态
        runner.is_running = True
        
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSSTDIO'] = '0'  # 禁用旧的Windows控制台IO
        
        # 创建一个进程来运行命令
        runner.process = subprocess.Popen(
            ['.\\python\\python.exe', '-s', 'main.py', '--windows-standalone-build'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 将错误输出重定向到标准输出
            text=True,
            encoding='utf-8',  # 明确指定编码为UTF-8
            errors='replace',  # 使用替换字符处理无法解码的字符
            env=env,  # 使用修改后的环境变量
            universal_newlines=True  # 使用通用换行符处理输出
        )
        
        # 创建一个队列来存储命令的输出
        output_queue = queue.Queue()
        
        def read_output():
            """
            这个函数会不断读取命令的输出
            并将每一行输出放入队列中
            """
            try:
                # 持续读取输出，直到进程停止
                while runner.is_running and runner.process:
                    line = runner.process.stdout.readline()
                    if line:
                        # 过滤进度条更新，只保留完整的进度信息
                        if line.startswith('\r'):
                            # 检查是否是完整的进度信息
                            if line.strip().endswith('it/s]'):
                                output_queue.put(line.strip())
                        else:
                            output_queue.put(line.strip())
                    elif runner.process.poll() is not None:  # 如果进程已结束
                        break
                    time.sleep(0.1)  # 添加小延迟，避免CPU过度使用
            except Exception as e:
                output_queue.put(f"Error reading output: {str(e)}")
            finally:
                # 确保进程已经终止
                if runner.process:
                    try:
                        runner.process.stdout.close()
                    except:
                        pass
        
        # 创建一个线程来读取输出
        output_thread = threading.Thread(target=read_output)
        output_thread.daemon = True
        output_thread.start()
        
        # 用于存储所有的输出行
        all_output = []
        last_progress = None
        
        # 只要程序在运行，就继续读取输出
        while runner.is_running and (output_thread.is_alive() or not output_queue.empty()):
            try:
                # 尝试从队列中获取一行输出
                line = output_queue.get_nowait()
                
                # 处理进度条信息
                if line.strip().endswith('it/s]'):
                    # 更新最后的进度信息
                    last_progress = line
                    # 如果输出中已经有进度信息，就更新它
                    if all_output and all_output[-1].strip().endswith('it/s]'):
                        all_output[-1] = line
                    else:
                        all_output.append(line)
                else:
                    all_output.append(line)
                
                # 将当前所有的输出组合成字符串，并返回给界面显示
                yield "\n".join(all_output)
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                all_output.append(f"Error processing output: {str(e)}")
                yield "\n".join(all_output)
        
        # 获取剩余的输出
        while not output_queue.empty():
            try:
                line = output_queue.get_nowait()
                all_output.append(line)
            except:
                pass
        
        # 如果是被手动停止的
        if not runner.is_running:
            all_output.append("命令已停止执行")
        
        # 返回最终的完整输出
        yield "\n".join(all_output)
        
    except Exception as e:
        yield f"运行出错: {str(e)}"
    finally:
        runner.is_running = False
        if runner.process:
            try:
                runner.process.terminate()
                runner.process = None
            except:
                pass

def stop_command():
    """
    停止正在运行的命令
    """
    try:
        if runner.process and runner.is_running:
            runner.is_running = False
            runner.process.terminate()
            runner.process.wait(timeout=5)  # 等待进程终止
            runner.process = None
            return "命令已停止执行"
    except Exception as e:
        return f"停止命令时出错: {str(e)}"
    return "没有正在运行的命令"

# 自定义CSS样式
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    background-color: #ffffff !important;
}

.main-header {
    color: #6c5ce7 !important;
    font-size: 1.5rem !important;
    font-weight: 500 !important;
    margin-bottom: 1.5rem !important;
    text-align: left !important;
    border-bottom: none !important;
}

.btn-primary {
    background-color: #ff7730 !important;
    border: none !important;
    color: white !important;
    padding: 0.5rem 2rem !important;
    border-radius: 5px !important;
    transition: all 0.3s ease !important;
    font-weight: 500 !important;
}

.btn-primary:hover {
    background-color: #ff5500 !important;
    transform: translateY(-2px) !important;
}

.btn-stop {
    background-color: #ff4757 !important;
    border: none !important;
    color: white !important;
    padding: 0.5rem 2rem !important;
    border-radius: 5px !important;
    transition: all 0.3s ease !important;
    font-weight: 500 !important;
}

.btn-stop:hover {
    background-color: #ff1f1f !important;
    transform: translateY(-2px) !important;
}

.output-box {
    border: none !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
    background-color: #f8f9fa !important;
    font-family: monospace !important;
    padding: 1rem !important;
}

.output-box:focus {
    box-shadow: 0 5px 20px rgba(0,0,0,0.15) !important;
}
"""

# 创建Gradio界面
def create_gradio_interface():
    with gr.Blocks(css=custom_css) as demo:
        # 添加标题
        gr.Markdown("# Python命令执行器", elem_classes=["main-header"])
        
        with gr.Row():
            # 创建一个列，包含按钮和输出
            with gr.Column(scale=1):
                # 创建按钮行
                with gr.Row():
                    run_button = gr.Button("运行命令", elem_classes=["btn-primary"])
                    stop_button = gr.Button("停止运行", elem_classes=["btn-stop"])
                
                # 创建输出文本框
                output_text = gr.Textbox(
                    label="运行输出",
                    placeholder="点击运行按钮执行命令...",
                    lines=15,
                    elem_classes=["output-box"]
                )
        
        # 当点击运行按钮时，执行run_command函数
        run_button.click(
            fn=run_command,
            outputs=output_text
        )
        
        # 当点击停止按钮时，执行stop_command函数
        stop_button.click(
            fn=stop_command,
            outputs=output_text
        )
    
    return demo

# 创建并启动Gradio界面
demo = create_gradio_interface()

try:
    # 尝试在更大的端口范围内查找可用端口
    runner.gradio_port = find_free_port(7861, 7961)  # 扩大端口范围
    demo.launch(
        server_name="127.0.0.1",
        server_port=runner.gradio_port,
        share=True,  # 关闭分享功能，避免不必要的外部访问
        prevent_thread_lock=True,
        show_error=True,  # 显示详细错误信息
        quiet=True  # 减少不必要的日志输出
    )
    print(f"Gradio server running on port: {runner.gradio_port}")
except OSError as e:
    print(f"Error starting Gradio server: {e}")
    # 如果指定端口范围都失败，尝试让系统自动分配端口
    demo.launch(
        server_name="127.0.0.1",
        server_port=None,  # 让系统自动分配可用端口
        share=True,
        prevent_thread_lock=True,
        show_error=True,
        quiet=True
    )
    print(f"Gradio server running on automatically assigned port")

@run_batch_bp.route('/')
def index():
    """返回Gradio界面URL"""
    port = runner.gradio_port or "自动分配的端口"
    return f'Gradio is running at: <a href="http://127.0.0.1:{port}">http://127.0.0.1:{port}</a>'
