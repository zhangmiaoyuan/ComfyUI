import requests
import json
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 读取data.txt中的翻译对
def load_translation_pairs():
    """从data.txt加载中英文翻译对"""
    translation_pairs = {}
    data_path = os.path.join(os.path.dirname(__file__), 'data.txt')
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(0, len(lines), 2):
                if i+1 < len(lines):
                    chinese = lines[i].strip()
                    english = lines[i+1].strip()
                    translation_pairs[chinese] = english
    except Exception as e:
        logging.error(f"Error loading translation pairs: {str(e)}")
    
    return translation_pairs

# 预加载翻译对
translation_pairs = load_translation_pairs()

def translate_to_english(chinese_text):
    """
    将中文文本翻译成英文，第一个词使用data.txt中的翻译，剩下的内容使用Ollama API
    
    Args:
        chinese_text (str): 中文文本
        
    Returns:
        str: 翻译后的英文文本
    """
    words = chinese_text.split("。")
    if not words:
        return ""
    
    # 翻译第一个词
    first_word = words[0]
    if first_word in translation_pairs:
        translated_first_word = translation_pairs[first_word]
    else:
        translated_first_word = _translate_with_ollama(first_word)
    
    # 翻译剩余部分
    remaining_text = ' '.join(words[1:])
    if remaining_text:
        translated_remaining = _translate_with_ollama(remaining_text)
    else:
        translated_remaining = ""
    
    # 合并翻译结果
    return f"{translated_first_word} {translated_remaining}".strip()

def _translate_with_ollama(chinese_text):
    try:
        # Ollama API endpoint
        url = "http://113.89.86.117:11434/api/generate"
        # url = "http://192.168.1.4:11434/api/generate"
        
        # 构建翻译提示
        prompt = f"Translate the following Chinese text to English. Only return the translation, no explanations: {chinese_text}"
        
        # API请求数据
        data = {
            "model": "qwen2.5:14b",  
            "prompt": prompt,
            "stream": False
        }
        
        # 发送POST请求
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            # 提取翻译结果
            translation = result.get('response', '').strip()
            return translation
        else:
            raise Exception(f"Translation failed with status code: {response.status_code}")
            
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        return chinese_text  # 如果翻译失败，返回原始文本
