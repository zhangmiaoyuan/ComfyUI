from flask import Blueprint, request, jsonify, current_app, Response, render_template, session
import logging
from openai import OpenAI
import os
import json

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建蓝图
chatbox_bp = Blueprint('chatbox08', __name__, url_prefix='/chatbox08')

# 配置API客户端
client = OpenAI(
    api_key="sk-e7d24a7b681442afb14455ef37f0f7c5",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

@chatbox_bp.route('/')
def chatbox():
    if 'conversations' not in session:
        session['conversations'] = [{'id': '1', 'title': '新对话', 'messages': []}]
    return render_template('008-chatbox/index.html')

def generate_stream_response(messages, model="deepseek-r1"):
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=30000
        )

        thinking_buffer = ""
        answer_buffer = ""

        for chunk in stream:
            if not getattr(chunk, 'choices', None):
                continue

            delta = chunk.choices[0].delta
            
            # 处理思考过程和回答内容
            if getattr(delta, 'reasoning_content', None):
                content = delta.reasoning_content
                thinking_buffer += content
                # 立即发送思考过程
                yield f"data: {json.dumps({'type': 'thinking', 'content': content})}\n\n"
            elif getattr(delta, 'content', None):
                content = delta.content
                answer_buffer += content
                # 立即发送回答内容
                yield f"data: {json.dumps({'type': 'answer', 'content': content})}\n\n"
        
        # 在流结束时发送完整的思考过程和回答
        yield f"data: {json.dumps({'type': 'complete', 'thinking': thinking_buffer, 'answer': answer_buffer})}\n\n"
                
    except Exception as e:
        logger.error(f"Stream API error: {str(e)}")
        error_content = {
            "type": "error",
            "content": f"抱歉，调用API时出错：{str(e)}"
        }
        yield f"data: {json.dumps(error_content)}\n\n"

@chatbox_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'deepseek-r1')
        conversation_id = data.get('conversation_id', '1')
        
        if not message:
            return jsonify({"error": "消息不能为空"}), 400

        # 获取当前对话的消息历史
        conversations = session.get('conversations', [])
        current_conv = next((c for c in conversations if c['id'] == conversation_id), None)
        
        if not current_conv:
            current_conv = {'id': conversation_id, 'title': f'新对话 {conversation_id}', 'messages': []}
            conversations.append(current_conv)

        # 添加用户消息到历史
        current_conv['messages'].append({'role': 'user', 'content': message})
        session['conversations'] = conversations
            
        def generate():
            response_stream = generate_stream_response(current_conv['messages'], model)
            for response in response_stream:
                if 'type": "complete"' in response:
                    # 解析完整响应并保存到会话历史
                    data = json.loads(response.split('data: ')[1])
                    current_conv['messages'].append({
                        'role': 'assistant',
                        'content': data['answer'],
                        'thinking': data['thinking']
                    })
                    session['conversations'] = conversations
                yield response

        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@chatbox_bp.route('/conversations', methods=['GET', 'POST', 'DELETE'])
def manage_conversations():
    if request.method == 'GET':
        return jsonify({'conversations': session.get('conversations', [])})
        
    elif request.method == 'POST':
        conversations = session.get('conversations', [])
        new_id = str(len(conversations) + 1)
        new_conversation = {
            'id': new_id,
            'title': f'新对话 {new_id}',
            'messages': []
        }
        conversations.append(new_conversation)
        session['conversations'] = conversations
        return jsonify({'conversation': new_conversation})
        
    elif request.method == 'DELETE':
        conversation_id = request.args.get('id')
        conversations = session.get('conversations', [])
        conversations = [c for c in conversations if c['id'] != conversation_id]
        if not conversations:  # 如果删除后没有对话了，创建一个新的
            conversations = [{'id': '1', 'title': '新对话', 'messages': []}]
        session['conversations'] = conversations
        return jsonify({'success': True})

@chatbox_bp.route('/clear', methods=['POST'])
def clear_history():
    conversation_id = request.json.get('conversation_id', '1')
    conversations = session.get('conversations', [])
    current_conv = next((c for c in conversations if c['id'] == conversation_id), None)
    if current_conv:
        current_conv['messages'] = []
        session['conversations'] = conversations
    return jsonify({'success': True})

@chatbox_bp.route('/export', methods=['POST'])
def export_conversation():
    try:
        conversation_id = request.json.get('conversation_id', '1')
        conversations = session.get('conversations', [])
        current_conv = next((c for c in conversations if c['id'] == conversation_id), None)
        
        if not current_conv:
            return jsonify({"error": "对话不存在"}), 404

        # 生成HTML内容
        html_content = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title>GCAI对话记录</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }',
            '.message { margin: 10px 0; padding: 10px; border-radius: 5px; white-space: pre-wrap; }',
            '.user-message { background-color: #e3f2fd; margin-left: 20%; }',
            '.assistant-message { background-color: #f5f5f5; margin-right: 20%; }',
            '.thinking-message { background-color: #fff3e0; border-left: 4px solid #ffb74d; font-style: italic; margin-bottom: 10px; }',
            '.system-message { text-align: center; color: #666; }',
            'pre { background-color: #282c34; color: #abb2bf; padding: 1em; border-radius: 4px; overflow-x: auto; }',
            'code { font-family: Consolas, Monaco, monospace; }',
            '.message-group { margin: 20px 0; }',
            '</style>',
            '</head>',
            '<body>',
            f'<h1>对话记录 - {current_conv["title"]}</h1>',
            '<div class="chat-container">'
        ]

        # 添加消息内容
        for msg in current_conv['messages']:
            role = msg['role']
            content = msg.get('content', '')
            thinking = msg.get('thinking', '')

            if role == 'user':
                html_content.append('<div class="message-group">')
                html_content.append(f'<div class="message user-message">{content}</div>')
                html_content.append('</div>')
            elif role == 'assistant':
                html_content.append('<div class="message-group">')
                if thinking:
                    html_content.append(f'<div class="thinking-message">思考过程：{thinking}</div>')
                html_content.append(f'<div class="message assistant-message">{content}</div>')
                html_content.append('</div>')

        html_content.extend(['</div>', '</body>', '</html>'])
        html_text = '\n'.join(html_content)

        # 生成响应
        response = Response(html_text, 
                          mimetype='text/html',
                          headers={
                              'Content-Disposition': f'attachment; filename=conversation_{conversation_id}.html'
                          })
        return response

    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({"error": str(e)}), 500