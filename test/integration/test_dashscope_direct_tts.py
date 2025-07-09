#!/usr/bin/env python3
"""
DashScope TTS API 直接调用测试
基于官方文档：https://help.aliyun.com/zh/dashscope/developer-reference/speech-understanding-and-synthesis
"""

import os
import requests
import json

def test_dashscope_tts_api():
    """测试DashScope TTS API的多个端点"""
    
    # 从环境变量获取API Key，如果没有则使用测试Key
    api_key = os.getenv("DASHSCOPE_API_KEY", "sk-bailian-tester-001")
    
    print(f"使用API Key: {api_key}")
    print("=" * 60)
    
    # 测试文本
    test_text = "你好，这是一个语音合成测试。"
    
    # 基于官方文档的正确端点和请求格式
    test_cases = [
        {
            "name": "DashScope TTS API - 正确端点",
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
                    "format": "mp3",
                    "sample_rate": 22050,
                    "volume": 50,
                    "speech_rate": 1.0,
                    "pitch_rate": 1.0
                }
            }
        },
        {
            "name": "DashScope TTS API - CosyVoice-v2",
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
            "name": "DashScope 长文本TTS API",
            "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-to-speech/synthesis",
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
        print(f"\n{i}. 测试: {test_case['name']}")
        print(f"   端点: {test_case['url']}")
        print(f"   请求数据: {json.dumps(test_case['data'], ensure_ascii=False, indent=2)}")
        
        try:
            response = requests.request(
                method=test_case['method'],
                url=test_case['url'],
                headers=test_case['headers'],
                json=test_case['data'],
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            print(f"   响应头: {dict(response.headers)}")
            
            # 尝试解析JSON响应
            try:
                response_json = response.json()
                print(f"   响应内容: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            except:
                print(f"   响应内容 (原始): {response.text[:500]}...")
            
            if response.status_code == 200:
                print("   ✅ 请求成功")
            elif response.status_code == 401:
                print("   ❌ 认证失败 (API Key无效)")
            elif response.status_code == 400:
                print("   ❌ 请求参数错误")
            elif response.status_code == 404:
                print("   ❌ 端点不存在")
            elif response.status_code == 429:
                print("   ⚠️ 请求频率限制")
            else:
                print(f"   ❓ 其他错误: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 请求异常: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    print("DashScope TTS API 直接调用测试")
    print("基于官方文档的正确API格式")
    print()
    
    # 检查环境变量
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️ 警告: 未设置 DASHSCOPE_API_KEY 环境变量")
        print("   将使用测试API Key，可能会返回401错误")
        print("   请设置真实的API Key: export DASHSCOPE_API_KEY=your_real_key")
        print()
    else:
        print(f"✅ 检测到API Key: {api_key[:10]}...")
        print()
    
    test_dashscope_tts_api() 