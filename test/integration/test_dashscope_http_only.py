#!/usr/bin/env python3
"""
强制DashScope SDK使用HTTP连接测试
"""

import os
import sys
import subprocess
import tempfile
import ssl
import certifi

def test_http_only_dashscope():
    """强制使用HTTP连接测试DashScope"""
    print("=" * 60)
    print("🔍 强制DashScope SDK使用HTTP连接测试")
    print("=" * 60)
    
    # 创建测试音频文件
    print("🔍 创建测试音频文件...")
    test_audio_file = "/tmp/test_audio_http.aiff"
    try:
        subprocess.run([
            'say', '-v', 'Ting-Ting', '-r', '200', 
            '你好，这是HTTP连接测试', 
            '-o', test_audio_file
        ], check=True)
        print(f"✅ 测试音频文件创建成功: {test_audio_file}")
    except Exception as e:
        print(f"❌ 创建测试音频文件失败: {e}")
        return
    
    # 设置环境变量强制使用HTTP
    print("\n🔍 设置环境变量...")
    
    # 保存原始环境变量
    original_ssl_verify = os.environ.get('PYTHONHTTPSVERIFY')
    original_no_proxy = os.environ.get('NO_PROXY')
    
    try:
        # 禁用SSL验证
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        
        # 设置代理密钥
        proxy_key = "sk-bailian-tester-001"
        os.environ['DASHSCOPE_API_KEY'] = proxy_key
        
        print(f"🔑 使用代理密钥: {proxy_key}")
        print(f"📁 使用音频文件: {test_audio_file}")
        
        # 尝试修改DashScope的默认URL
        import dashscope
        from dashscope.audio.asr import Recognition
        
        # 设置API Key
        dashscope.api_key = proxy_key
        
        # 尝试设置HTTP基础URL
        if hasattr(dashscope, 'base_http_api_url'):
            dashscope.base_http_api_url = "http://10.10.5.176"
            print(f"✅ 设置HTTP基础URL: http://10.10.5.176")
        
        # 尝试设置WebSocket URL
        if hasattr(dashscope, 'base_websocket_api_url'):
            dashscope.base_websocket_api_url = "ws://10.10.5.176"
            print(f"✅ 设置WebSocket URL: ws://10.10.5.176")
        
        # 创建Recognition实例
        recognition = Recognition(
            model='paraformer-realtime-v2',
            format='wav',  # AIFF也被当作WAV处理
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
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 恢复原始环境变量
        if original_ssl_verify is not None:
            os.environ['PYTHONHTTPSVERIFY'] = original_ssl_verify
        else:
            os.environ.pop('PYTHONHTTPSVERIFY', None)
        
        if original_no_proxy is not None:
            os.environ['NO_PROXY'] = original_no_proxy
        else:
            os.environ.pop('NO_PROXY', None)
        
        # 清理测试文件
        try:
            os.remove(test_audio_file)
            print(f"🧹 清理测试文件: {test_audio_file}")
        except:
            pass
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_http_only_dashscope() 