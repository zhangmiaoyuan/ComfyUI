import os
import atexit
import threading
from encrypt_lora import generate_key
from cryptography.fernet import Fernet
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import queue

class LoraDecryptManager:
    def __init__(self):
        self.decrypted_files = []
        self._lock = Lock()  # 用于线程安全的文件列表访问
        self.password = "zhang2024"
        # 使用相对路径
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.lora_path = os.path.join(self.base_path, "models", "loras")
        self.workflow_path = os.path.join(self.base_path, "workflow")
        self._decrypt_thread = None  # 存储解密线程
        self._file_queue = queue.Queue()  # 用于存储待处理的文件
        self._executor = ThreadPoolExecutor(max_workers=2)  # 增加线程数到2
        atexit.register(self.cleanup)

    def decrypt_file(self, args) -> bool:
        """解密单个文件"""
        input_file, output_file = args
        try:
            key = generate_key(self.password)
            f = Fernet(key)
            
            with open(input_file, 'rb') as file:
                file_data = file.read()
            
            decrypted_data = f.decrypt(file_data)
            
            with open(output_file, 'wb') as file:
                file.write(decrypted_data)
            
            # 线程安全地添加到解密文件列表
            with self._lock:
                self.decrypted_files.append(output_file)
            
            print(f"成功解密: {os.path.basename(input_file)}")
            return True
        except Exception as e:
            print(f"解密失败 {input_file}: {str(e)}")
            return False

    def collect_files(self, directory, file_type=None):
        """收集需要处理的文件"""
        for root, _, files in os.walk(directory):
            for file in files:
                is_target = False
                if file_type == 'lora' and file.endswith('.safetensors.encrypted'):
                    is_target = True
                elif file_type == 'workflow' and file.endswith('.json.encrypted'):
                    is_target = True
                
                if is_target:
                    input_file = os.path.join(root, file)
                    output_file = input_file.replace('.encrypted', '')
                    self._file_queue.put((input_file, output_file))

    def process_files(self):
        """处理队列中的文件"""
        futures = []
        while True:
            try:
                # 非阻塞方式获取文件
                args = self._file_queue.get_nowait()
                future = self._executor.submit(self.decrypt_file, args)
                futures.append(future)
            except queue.Empty:
                break

        # 等待所有任务完成
        for future in futures:
            future.result()

    def _decrypt_all_loras_thread(self):
        """在后台线程中执行解密操作"""
        total_files_before = len(self.decrypted_files)

        # 快速收集所有需要处理的文件
        if os.path.exists(self.workflow_path):
            print(f"开始扫描并解密Workflow文件夹: {self.workflow_path}")
            self.collect_files(self.workflow_path, 'workflow')
        if os.path.exists(self.lora_path):
            print(f"开始扫描并解密Lora文件夹: {self.lora_path}")
            self.collect_files(self.lora_path, 'lora')
        


        # 处理所有文件
        self.process_files()

        total_processed = len(self.decrypted_files) - total_files_before
        print(f"解密完成，共处理 {total_processed} 个文件")

    def start_decrypt(self):
        """启动后台解密线程"""
        if self._decrypt_thread is None or not self._decrypt_thread.is_alive():
            self._decrypt_thread = threading.Thread(
                target=self._decrypt_all_loras_thread,
                daemon=True  # 设置为守护线程，这样主程序退出时线程会自动结束
            )
            self._decrypt_thread.start()
            print("后台解密线程已启动")

    def cleanup(self):
        """清理所有解密的文件"""
        if not self.decrypted_files:
            return
            
        print(f"开始清理 {len(self.decrypted_files)} 个解密文件...")
        for file in self.decrypted_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"已删除解密文件: {file}")
            except Exception as e:
                print(f"删除文件失败 {file}: {str(e)}")
        
        # 清理完成后清空列表
        self.decrypted_files.clear()
        
        # 关闭线程池
        self._executor.shutdown(wait=False)