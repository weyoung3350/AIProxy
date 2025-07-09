#!/usr/bin/env python3
"""
简单的测试服务器
用于测试和调试OpenResty代理功能
"""

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        if path == '/health':
            self.send_health_response()
        elif path == '/echo':
            self.send_echo_response(query)
        elif path == '/models':
            self.send_models_response()
        elif path == '/v1/models':
            self.send_models_response()
        else:
            self.send_404_response()
    
    def do_POST(self):
        """处理POST请求"""
        path = urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(post_data.decode('utf-8'))
        except:
            request_data = {}
        
        if path == '/v1/chat/completions':
            self.send_chat_completion_response(request_data)
        elif path == '/compatible-mode/v1/chat/completions':
            self.send_chat_completion_response(request_data)
        else:
            self.send_404_response()
    
    def send_health_response(self):
        """发送健康检查响应"""
        response = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "server": "test-server"
        }
        self.send_json_response(200, response)
    
    def send_echo_response(self, query):
        """发送回显响应"""
        response = {
            "method": "GET",
            "path": self.path,
            "headers": dict(self.headers),
            "query": query,
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(200, response)
    
    def send_models_response(self):
        """发送模型列表响应"""
        response = {
            "object": "list",
            "data": [
                {
                    "id": "qwen-plus",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "alibaba"
                },
                {
                    "id": "qwen-turbo",
                    "object": "model", 
                    "created": int(time.time()),
                    "owned_by": "alibaba"
                }
            ]
        }
        self.send_json_response(200, response)
    
    def send_chat_completion_response(self, request_data):
        """发送聊天完成响应"""
        messages = request_data.get('messages', [])
        model = request_data.get('model', 'qwen-plus')
        
        # 模拟响应内容
        if messages:
            last_message = messages[-1].get('content', '')
            response_text = f"这是一个模拟的AI响应。您的请求已通过OpenResty代理成功到达测试服务器。"
        else:
            response_text = "Hello! 这是一个测试响应。"
        
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        self.send_json_response(200, response)
    
    def send_404_response(self):
        """发送404响应"""
        response = {
            "error": {
                "message": "Not Found",
                "type": "invalid_request_error",
                "code": "not_found"
            }
        }
        self.send_json_response(404, response)
    
    def send_json_response(self, status_code, data):
        """发送JSON响应"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def run_server(port=8080):
    """运行测试服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestHandler)
    print(f"测试服务器启动在端口 {port}")
    print(f"健康检查: http://localhost:{port}/health")
    print(f"模型列表: http://localhost:{port}/v1/models")
    print(f"聊天接口: http://localhost:{port}/v1/chat/completions")
    print("按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.server_close()

if __name__ == '__main__':
    run_server() 