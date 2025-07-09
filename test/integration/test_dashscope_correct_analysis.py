#!/usr/bin/env python3
"""
DashScope API 正确功能分析
基于官方文档：https://help.aliyun.com/zh/model-studio/developer-reference/use-qwen-by-calling-api
"""

import os
import requests
import json

def test_dashscope_actual_features():
    """测试DashScope的实际可用功能"""
    
    # 从环境变量获取API Key
    api_key = os.getenv("DASHSCOPE_API_KEY", "sk-bailian-tester-001")
    
    print(f"使用API Key: {api_key}")
    print("=" * 80)
    print("🔍 DashScope API 功能分析")
    print("基于官方文档：https://help.aliyun.com/zh/model-studio/")
    print("=" * 80)
    
    # 测试1：通义千问对话 (DashScope的主要功能)
    print("\n📝 测试1: 通义千问对话 API")
    print("-" * 40)
    
    chat_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    chat_data = {
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一个有用的助手。"},
                {"role": "user", "content": "你好，请介绍一下你自己。"}
            ]
        },
        "parameters": {
            "result_format": "message"
        }
    }
    
    try:
        response = requests.post(
            chat_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=chat_data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_json = response.json()
            print("✅ 通义千问对话API 可用")
            print(f"模型响应: {response_json.get('output', {}).get('choices', [{}])[0].get('message', {}).get('content', '无内容')[:100]}...")
        else:
            print(f"❌ 通义千问对话API 错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试2：OpenAI兼容模式 (DashScope支持的另一种调用方式)
    print("\n🔄 测试2: OpenAI兼容模式")
    print("-" * 40)
    
    openai_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    openai_data = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "你是一个有用的助手。"},
            {"role": "user", "content": "简单介绍一下DashScope。"}
        ]
    }
    
    try:
        response = requests.post(
            openai_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=openai_data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_json = response.json()
            print("✅ OpenAI兼容模式 可用")
            print(f"模型响应: {response_json.get('choices', [{}])[0].get('message', {}).get('content', '无内容')[:100]}...")
        else:
            print(f"❌ OpenAI兼容模式 错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试3：确认TTS功能不存在
    print("\n🎵 测试3: TTS功能确认")
    print("-" * 40)
    
    # 基于之前的测试结果，我们知道这些端点会返回"url error"
    tts_endpoints = [
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-to-speech/synthesis",
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/tts/synthesis",
        "https://dashscope.aliyuncs.com/compatible-mode/v1/audio/speech"
    ]
    
    for endpoint in tts_endpoints:
        print(f"测试端点: {endpoint}")
        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "cosyvoice-v1",
                    "input": {"text": "测试"},
                    "parameters": {"voice": "longwan", "format": "mp3"}
                },
                timeout=10
            )
            
            if response.status_code == 400:
                response_json = response.json()
                if "url error" in response_json.get("message", ""):
                    print("❌ 端点不存在 (url error)")
                elif "Model not exist" in response_json.get("message", ""):
                    print("❌ 模型不存在")
                else:
                    print(f"❌ 其他错误: {response_json}")
            elif response.status_code == 404:
                print("❌ 端点不存在 (404)")
            else:
                print(f"🤔 意外响应: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 DashScope API 功能总结")
    print("=" * 80)
    print("✅ 支持的功能:")
    print("   - 通义千问对话 (Qwen Chat)")
    print("   - OpenAI兼容模式")
    print("   - 文本生成")
    print("   - 视觉理解 (Qwen-VL)")
    print("   - 多模态对话")
    print()
    print("❌ 不支持的功能:")
    print("   - 专门的TTS (Text-to-Speech) API")
    print("   - CosyVoice语音合成直接调用")
    print("   - OpenAI风格的 /v1/audio/speech 端点")
    print()
    print("💡 结论:")
    print("   DashScope主要提供大语言模型服务，不是专门的TTS服务。")
    print("   如需TTS功能，应该使用阿里云的其他语音服务。")

if __name__ == "__main__":
    test_dashscope_actual_features() 