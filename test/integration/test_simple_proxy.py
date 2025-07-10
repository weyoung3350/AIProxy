#!/usr/bin/env python3
"""
简单的AIProxy代理测试脚本
测试远程AIProxy服务器的基本功能
"""

import requests
import json
import os

def test_remote_proxy():
    """测试远程AIProxy服务器"""
    print("=" * 60)
    print("🔍 测试远程AIProxy服务器")
    print("=" * 60)
    
    # 远程服务器地址
    proxy_url = "http://10.10.5.176"
    
    # 测试stats页面
    print(f"📊 测试stats页面: {proxy_url}/stats")
    try:
        response = requests.get(f"{proxy_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats页面正常: {stats.get('service', 'unknown')} v{stats.get('version', 'unknown')}")
            print(f"   API Keys数量: {stats.get('api_keys_count', 0)}")
            print(f"   总请求数: {stats.get('total_requests', 0)}")
        else:
            print(f"❌ Stats页面异常: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats页面错误: {e}")
    
    # 测试API代理
    print(f"\n🔗 测试API代理: {proxy_url}/chat/completions")
    
    # 测试不同的代理密钥
    proxy_keys = [
        "sk-bailian-tester-001",
        "sk-bailian-tester-002", 
        "sk-bailian-tester-003"
    ]
    
    for proxy_key in proxy_keys:
        print(f"\n🔑 测试代理密钥: {proxy_key}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {proxy_key}"
        }
        
        data = {
            "model": "qwen-plus",
            "messages": [
                {"role": "user", "content": "Hello, this is a test"}
            ]
        }
        
        try:
            response = requests.post(
                f"{proxy_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"✅ 代理成功: {content[:50]}...")
            else:
                print(f"❌ 代理失败: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ 代理错误: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_remote_proxy() 