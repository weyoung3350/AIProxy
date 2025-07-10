#!/usr/bin/env python3
"""
测试通过hosts文件重定向DashScope连接到AIProxy
"""

import os
import sys
import time
import requests
import subprocess
import tempfile
from dashscope.audio.asr import Recognition

def test_hosts_redirect():
    """测试通过hosts文件重定向的连接"""
    print("=" * 60)
    print("🔍 测试hosts文件重定向DashScope连接")
    print("=" * 60)
    
    # 检查hosts文件配置
    try:
        with open('/etc/hosts', 'r') as f:
            hosts_content = f.read()
            if '10.10.5.176 dashscope.aliyuncs.com' in hosts_content:
                print("✅ hosts文件配置正确")
            else:
                print("❌ hosts文件未配置或配置错误")
                print("请添加: 10.10.5.176 dashscope.aliyuncs.com")
                return
    except Exception as e:
        print(f"❌ 无法读取hosts文件: {e}")
        return
    
    # 测试域名解析
    print("\n🔍 测试域名解析...")
    try:
        import socket
        ip = socket.gethostbyname('dashscope.aliyuncs.com')
        print(f"✅ dashscope.aliyuncs.com 解析到: {ip}")
        if ip != '10.10.5.176':
            print(f"⚠️  解析结果不是预期的 10.10.5.176")
    except Exception as e:
        print(f"❌ 域名解析失败: {e}")
        return
    
    # 测试HTTP连接
    print("\n🔍 测试HTTP连接...")
    try:
        response = requests.get('http://dashscope.aliyuncs.com/stats', timeout=5)
        if response.status_code == 200:
            print("✅ HTTP连接成功")
            stats = response.json()
            print(f"   服务: {stats.get('service', 'unknown')}")
            print(f"   版本: {stats.get('version', 'unknown')}")
        else:
            print(f"❌ HTTP连接失败: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTP连接错误: {e}")
    
    # 测试HTTPS连接（预期会失败）
    print("\n🔍 测试HTTPS连接...")
    try:
        response = requests.get('https://dashscope.aliyuncs.com/stats', timeout=5, verify=False)
        if response.status_code == 200:
            print("✅ HTTPS连接成功")
        else:
            print(f"❌ HTTPS连接失败: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTPS连接错误: {e}")
        print("   这是预期的，因为AIProxy可能没有配置SSL证书")
    
    # 创建测试音频文件
    print("\n🔍 创建测试音频文件...")
    test_audio_file = "/tmp/test_audio_hosts.mp3"
    try:
        subprocess.run([
            'say', '-v', 'Ting-Ting', '-r', '200', 
            '你好，这是hosts重定向测试', 
            '-o', test_audio_file, '--data-format=mp3'
        ], check=True)
        print(f"✅ 测试音频文件创建成功: {test_audio_file}")
    except Exception as e:
        print(f"❌ 创建测试音频文件失败: {e}")
        # 尝试使用aiff格式
        try:
            test_audio_file = "/tmp/test_audio_hosts.aiff"
            subprocess.run([
                'say', '-v', 'Ting-Ting', '-r', '200', 
                '你好，这是hosts重定向测试', 
                '-o', test_audio_file
            ], check=True)
            print(f"✅ 测试音频文件创建成功（AIFF格式）: {test_audio_file}")
        except Exception as e2:
            print(f"❌ 创建测试音频文件失败（AIFF格式）: {e2}")
            return
    
    # 测试DashScope SDK连接
    print("\n🔍 测试DashScope SDK连接...")
    
    # 设置API Key
    proxy_key = "sk-bailian-tester-001"
    os.environ['DASHSCOPE_API_KEY'] = proxy_key
    
    try:
        import dashscope
        dashscope.api_key = proxy_key
        
        print(f"🔑 使用代理密钥: {proxy_key}")
        print(f"📁 使用音频文件: {test_audio_file}")
        
        # 创建Recognition实例
        audio_format = 'mp3' if test_audio_file.endswith('.mp3') else 'wav'
        recognition = Recognition(
            model='paraformer-realtime-v2',
            format=audio_format,
            sample_rate=16000,
            language_hints=['zh', 'en'],
            callback=None
        )
        
        print("🔗 正在调用识别服务...")
        
        # 同步调用识别
        result = recognition.call(test_audio_file)
        
        # 处理结果
        if result.status_code == 200:
            print("✅ 识别成功")
            sentence = result.get_sentence()
            if hasattr(sentence, 'text'):
                print(f"📝 识别结果: {sentence.text}")
            else:
                print(f"📝 识别结果: {sentence}")
        else:
            print(f"❌ 识别失败: {result.status_code} - {result.message}")
            
    except Exception as e:
        print(f"❌ DashScope SDK测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理测试文件
    try:
        os.remove(test_audio_file)
        print(f"🧹 清理测试文件: {test_audio_file}")
    except:
        pass
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_hosts_redirect() 