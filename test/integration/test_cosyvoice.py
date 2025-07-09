"""
CosyVoice语音合成API测试
测试通过AIProxy代理访问阿里云百炼(DashScope)的CosyVoice语音合成服务

使用方法:
1. 确保OpenResty服务已启动: ./start.sh
2. 确保配置文件中有有效的API密钥
3. 运行测试: python test/integration/test_cosyvoice.py

预期结果:
- 如果API密钥有效: 生成output.wav音频文件
- 如果API密钥无效: 显示401错误信息

注意: 此测试使用OpenAI兼容的API接口，通过AIProxy代理访问CosyVoice服务
"""

import os
import requests
import json

base_url = "http://localhost:8001"

def test_cosyvoice_via_proxy():
    """通过AIProxy代理测试CosyVoice语音合成"""
    proxy_key = "sk-bailian-tester-001"
    
    # 构建请求数据
    request_data = {
        "model": "cosyvoice-v1",
        "input": "你的模型名称是什么，能做什么？",
        "voice": "longxiaochun",
        "response_format": "wav"
    }
    
    headers = {
        "Authorization": f"Bearer {proxy_key}",
        "Content-Type": "application/json"
    }
    
    print("🔄 开始测试CosyVoice语音合成...")
    print(f"代理服务地址: {base_url}")
    print(f"使用API密钥: {proxy_key}")
    print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    
    try:
        # 发送请求到代理服务
        response = requests.post(
            f"{base_url}/v1/audio/speech",
            headers=headers,
            json=request_data,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            if 'audio' in content_type or 'octet-stream' in content_type:
                # 保存音频文件
                with open('output.wav', 'wb') as f:
                    f.write(response.content)
                print("✅ 语音合成成功，已保存到 output.wav")
                print(f"音频文件大小: {len(response.content)} 字节")
                return True
            else:
                print("❌ 响应不是音频数据")
                print(f"响应内容类型: {content_type}")
                print(f"响应内容: {response.text[:500]}")
                return False
        else:
            print(f"❌ 语音合成失败 - 状态码: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误响应: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 测试执行出错: {str(e)}")
        return False

def test_cosyvoice_different_voices():
    """测试不同的音色"""
    voices = ["longxiaochun", "longyuan", "longwan", "longtong"]
    proxy_key = "sk-bailian-tester-001"
    
    print("\n🔄 测试不同音色...")
    
    for voice in voices:
        print(f"\n测试音色: {voice}")
        
        request_data = {
            "model": "cosyvoice-v1",
            "input": f"这是{voice}音色的测试",
            "voice": voice,
            "response_format": "wav"
        }
        
        headers = {
            "Authorization": f"Bearer {proxy_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{base_url}/v1/audio/speech",
                headers=headers,
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                filename = f"output_{voice}.wav"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ {voice} 音色测试成功，保存为 {filename}")
            else:
                print(f"❌ {voice} 音色测试失败 - 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {voice} 音色测试出错: {str(e)}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("CosyVoice语音合成API代理测试")
    print("=" * 60)
    
    # 基础功能测试
    success = test_cosyvoice_via_proxy()
    
    if success:
        # 如果基础测试成功，进行扩展测试
        test_cosyvoice_different_voices()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()