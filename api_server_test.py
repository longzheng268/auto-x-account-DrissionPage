# -*- coding: utf-8 -*-
"""
API交互式测试服务端 - 智能版
功能：
1. 监听注册状态，智能提示输入
2. 自动根据进度询问邮箱或验证码
3. 支持手动干预
"""
import time
import logging
import threading
import queue
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局数据队列
data_queue = {
    'email_response': queue.Queue(maxsize=1),
    'captcha_response': queue.Queue(maxsize=1),
    'code_response': queue.Queue(maxsize=1),
    # 新增：输入请求队列（用于通知主线程需要用户输入）
    'input_request': queue.Queue()
}

class InteractiveHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except:
            request_data = {}

        # 4. 状态上报 (最关键的逻辑)
        if self.path == '/api/status/report':
            status = request_data.get('status')
            message = request_data.get('message')
            print(f"\n📊 [状态上报] {status}: {message}")
            
            # 智能触发：根据状态通知主线程准备数据
            if status == 'need_email':
                print("⚡ 检测到需要邮箱，请求用户输入...")
                data_queue['input_request'].put('email')
                
            elif status == 'need_email_code':
                print("⚡ 检测到需要验证码，请求用户输入...")
                data_queue['input_request'].put('code')
                
            self._send_response({'received': True})

        # 1. 邮箱请求
        elif self.path == '/api/email/request':
            print(f"📡 [收到请求] run_register 请求邮箱...")
            try:
                # 等待主线程准备好数据
                if data_queue['email_response'].empty():
                    print("⏳ 等待用户输入邮箱...")
                    
                response_data = data_queue['email_response'].get(timeout=300) # 等待5分钟
                print(f"✅ 发送邮箱: {response_data['email']}")
                self._send_response(response_data)
            except queue.Empty:
                self._send_response({'error': 'Timeout'}, 500)

        # 2. 验证码请求
        elif self.path == '/api/email/code':
            email = request_data.get('email', 'N/A')
            print(f"📡 [收到请求] run_register 请求验证码...")
            try:
                if data_queue['code_response'].empty():
                    print("⏳ 等待用户输入验证码...")
                    
                response_data = data_queue['code_response'].get(timeout=300)
                print(f"✅ 发送验证码: {response_data['code']}")
                self._send_response(response_data)
            except queue.Empty:
                self._send_response({'error': 'Timeout'}, 500)

        # 3. 验证方式请求
        elif self.path == '/api/captcha/request':
            print(f"📡 [收到请求] run_register 请求验证方式")
            try:
                if data_queue['captcha_response'].empty():
                    response_data = {'method': 'manual', 'status': 'pending'}
                else:
                    response_data = data_queue['captcha_response'].get()
                self._send_response(response_data)
            except:
                self._send_response({'method': 'manual', 'status': 'pending'})

        else:
            self._send_response({'error': 'Not Found'}, 404)

def run_server():
    server = HTTPServer(('', 8989), InteractiveHandler)
    server.serve_forever()

def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("=" * 60)
    print("🤖 智能API交互终端")
    print("1. 启动 run_register.py")
    print("2. 这里会自动监听到 'need_email' 状态，并提示你输入")
    print("3. 当需要验证码时，也会自动提示")
    print("=" * 60)
    
    # 预设验证方式为手动
    data_queue['captcha_response'].put({'method': 'manual', 'status': 'pending'})
    
    while True:
        try:
            # 等待输入请求
            request_type = data_queue['input_request'].get()
            
            if request_type == 'email':
                print("\n" + "="*40)
                print("📧 请提供一个注册邮箱")
                print("="*40)
                email = input("请输入邮箱: ").strip()
                password = input("请输入密码: ").strip()
                
                data_queue['email_response'].put({
                    'email': email,
                    'password': password
                })
                print("✅ 邮箱数据已就绪，正在发送给客户端...")
                
            elif request_type == 'code':
                print("\n" + "="*40)
                print("🔑 请查看邮箱并输入验证码")
                print("="*40)
                code = input("请输入6位验证码: ").strip()
                
                data_queue['code_response'].put({'code': code})
                print("✅ 验证码已就绪，正在发送给客户端...")
                
        except KeyboardInterrupt:
            break
            
    print("\n程序已退出")

if __name__ == '__main__':
    main()
