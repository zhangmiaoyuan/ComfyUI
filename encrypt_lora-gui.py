import os
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import tkinter as tk
from tkinter import filedialog, messagebox

def generate_key(password: str, salt: bytes = None) -> bytes:
    """从密码生成加密密钥"""
    if salt is None:
        salt = b'gcai_salt_2024'  # 固定salt值
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(input_file: str, output_file: str, password: str):
    """加密文件"""
    key = generate_key(password)
    f = Fernet(key)
    
    with open(input_file, 'rb') as file:
        file_data = file.read()
    
    encrypted_data = f.encrypt(file_data)
    
    with open(output_file, 'wb') as file:
        file.write(encrypted_data)

def process_path(path: str, password: str):
    """处理路径（可以是文件或文件夹）"""
    if os.path.isfile(path):
        # 如果是文件，检查是否是需要加密的文件类型
        if (path.endswith('.safetensors') or path.endswith('.json')) and not path.endswith('.encrypted'):
            output_file = path + '.encrypted'
            try:
                encrypt_file(path, output_file, password)
                print(f"已加密: {path} -> {output_file}")
                return 1
            except Exception as e:
                print(f"加密失败 {path}: {str(e)}")
                return 0
        return 0
    elif os.path.isdir(path):
        # 如果是文件夹，递归处理
        count = 0
        for root, _, files in os.walk(path):
            for file in files:
                if (file.endswith('.safetensors') or file.endswith('.json')) and not file.endswith('.encrypted'):
                    full_path = os.path.join(root, file)
                    try:
                        output_file = full_path + '.encrypted'
                        encrypt_file(full_path, output_file, password)
                        print(f"已加密: {full_path} -> {output_file}")
                        count += 1
                    except Exception as e:
                        print(f"加密失败 {full_path}: {str(e)}")
        return count
    return 0

def create_gui():
    """创建GUI界面"""
    window = tk.Tk()
    window.title("光彩AI Lora加密工具")
    window.geometry("600x400")
    
    # 添加说明文本
    instruction_text = """
    使用说明：
    1. 选择要加密的文件或文件夹
    2. 支持的文件类型：.safetensors 和 .json
    3. 输入加密密码
    4. 点击"开始加密"按钮
    
    注意：加密后的文件将添加.encrypted后缀
    """
    instruction_label = tk.Label(window, text=instruction_text, justify=tk.LEFT)
    instruction_label.pack(pady=10)
    
    # 文件选择框架
    file_frame = tk.Frame(window)
    file_frame.pack(pady=10)
    
    path_var = tk.StringVar()
    path_entry = tk.Entry(file_frame, textvariable=path_var, width=50)
    path_entry.pack(side=tk.LEFT, padx=5)
    
    def select_path():
        path = filedialog.askdirectory() or filedialog.askopenfilename(
            filetypes=[
                ("支持的文件", "*.safetensors;*.json"),
                ("Safetensors文件", "*.safetensors"),
                ("JSON文件", "*.json"),
                ("所有文件zhang2024", "*.*")
            ]
        )
        if path:
            path_var.set(path)
    
    select_button = tk.Button(file_frame, text="选择文件/文件夹", command=select_path)
    select_button.pack(side=tk.LEFT)
    
    # 密码输入框架
    password_frame = tk.Frame(window)
    password_frame.pack(pady=10)
    
    tk.Label(password_frame, text="加密密码：").pack(side=tk.LEFT)
    password_var = tk.StringVar()
    password_entry = tk.Entry(password_frame, textvariable=password_var, show="*")
    password_entry.pack(side=tk.LEFT)
    
    def start_encrypt():
        path = path_var.get()
        password = password_var.get()
        
        if not path or not password:
            messagebox.showerror("错误", "请选择文件/文件夹并输入密码")
            return
        
        try:
            count = process_path(path, password)
            if count > 0:
                messagebox.showinfo("成功", f"加密完成！共加密 {count} 个文件")
            else:
                messagebox.showwarning("提示", "没有找到需要加密的文件")
        except Exception as e:
            messagebox.showerror("错误", f"加密过程中出错：{str(e)}")
    
    # 开始加密按钮
    encrypt_button = tk.Button(window, text="开始加密", command=start_encrypt)
    encrypt_button.pack(pady=10)
    
    window.mainloop()

def main():
    if len(sys.argv) > 1:
        # 命令行模式
        path = sys.argv[1]
        if not os.path.exists(path):
            print(f"错误: 路径不存在: {path}")
            sys.exit(1)
            
        password = "zhang2024"  # 固定密码
        count = process_path(path, password)
        
        if count > 0:
            print(f"成功加密 {count} 个文件")
        else:
            print("没有找到需要加密的文件")
    else:
        # GUI模式
        create_gui()

if __name__ == "__main__":
    main()
