#!/usr/bin/env python3
"""
DashScope TTS API 修正测试
基于搜索到的官方文档信息，使用正确的DashScope API格式
"""

import os
import requests
import json

def test_dashscope_tts_api_corrected():
    """测试DashScope TTS API的正确格式"""
    
    # 从环境变量获取API Key，如果没有则使用测试Key
    api_key = os.getenv("DASHSCOPE_API_KEY", "sk-bailian-tester-001")
    
    print(f"使用API Key: {api_key}")
    print("=" * 60)
    
    # 测试文本
    test_text = "你好，这是一个语音合成测试。"
    
    # 基于搜索结果，DashScope使用不同的API结构
    test_cases = [
        {
            "name": "DashScope TTS API - 修正端点 (基于文档结构)",
            "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-to-speech/synthesis",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "data": {
                "model": "cosyvoice-v1",
                "input": {
                    "text": test_text
                },
                "parameters": {
                    "voice": "longwan",
                    "format": "mp3"
                }
            }
        },
        {
            "name": "DashScope TTS API - 修正端点 v2",
            "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-to-speech/synthesis",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "data": {
                "model": "cosyvoice-v2",
                "input": {
                    "text": test_text
                },
                "parameters": {
                    "voice": "longwan",
                    "format": "mp3",
                    "sample_rate": 22050
                }
            }
        },
        {
            "name": "DashScope TTS API - 可能的替代端点",
            "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/tts/synthesis",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "data": {
                "model": "cosyvoice-v2",
                "input": {
                    "text": test_text
                },
                "parameters": {
                    "voice": "longwan",
                    "format": "mp3"
                }
            }
        },
        {
            "name": "DashScope TTS API - 长文本语音合成",
            "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-to-speech/long-synthesis",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "data": {
                "model": "cosyvoice-longtext-v1",
                "input": {
                    "text": test_text
                },
                "parameters": {
                    "voice": "longwan",
                    "format": "mp3"
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"URL: {test_case['url']}")
        print(f"模型: {test_case['data']['model']}")
        
        try:
            response = requests.post(
                test_case["url"],
                headers=test_case["headers"],
                json=test_case["data"],
                timeout=30
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            # 尝试解析JSON响应
            try:
                response_json = response.json()
                print(f"响应内容: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print(f"响应内容 (非JSON): {response.text[:500]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
        
        print("❌ 请求参数错误" if response.status_code == 400 else "")
        print("-" * 60)

if __name__ == "__main__":
    print("DashScope TTS API 修正测试")
    print("基于官方文档信息，测试正确的API格式")
    print("=" * 60)
    test_dashscope_tts_api_corrected() 