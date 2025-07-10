#!/usr/bin/env python3
"""
直接使用IP地址测试AIProxy的DashScope代理功能
"""

import os
import requests
import subprocess
import tempfile
import json

def test_direct_ip_proxy():
    """直接使用IP地址测试AIProxy代理功能"""
    print("=" * 60)
    print("🔍 直接使用IP地址测试AIProxy代理功能")
    print("=" * 60)
    
    # AIProxy服务器地址
    proxy_host = "10.10.5.176"
    proxy_port = 80
    
    # 测试代理服务器连接
    print(f"🔍 测试代理服务器连接: {proxy_host}:{proxy_port}")
    try:
        response = requests.get(f"http://{proxy_host}:{proxy_port}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 代理服务器连接成功")
            print(f"   服务: {stats.get('service', 'unknown')}")
            print(f"   版本: {stats.get('version', 'unknown')}")
            print(f"   API Keys数量: {stats.get('api_keys_count', 0)}")
        else:
            print(f"❌ 代理服务器连接失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 代理服务器连接错误: {e}")
        return
    
    # 测试不同的代理密钥
    proxy_keys = ["sk-bailian-tester-001", "sk-bailian-tester-002"]
    
    for proxy_key in proxy_keys:
        print(f"\n🔑 测试代理密钥: {proxy_key}")
        
        # 测试通过代理调用OpenAI兼容API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {proxy_key}"
        }
        
        data = {
            "model": "qwen-plus",
            "messages": [
                {"role": "user", "content": "Hello, test message"}
            ]
        }
        
        try:
            response = requests.post(
                f"http://{proxy_host}:{proxy_port}/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"✅ 代理API调用成功: {content[:50]}...")
            else:
                print(f"❌ 代理API调用失败: {response.status_code}")
                print(f"   错误信息: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ 代理API调用错误: {e}")
    
    print("\n" + "=" * 60)
    print("📝 测试结论:")
    print("1. 如果上述测试成功，说明AIProxy基本功能正常")
    print("2. DashScope SDK可能需要HTTPS连接，而AIProxy只提供HTTP")
    print("3. 建议配置AIProxy的HTTPS支持，或者使用其他方法")
    print("=" * 60)

if __name__ == "__main__":
    test_direct_ip_proxy() 