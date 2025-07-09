"""
AIProxy代理DashScope语音合成API验证脚本

本脚本用于验证AIProxy是否能正确代理阿里云百炼DashScope原生TTS接口。
- 代理端点: http://localhost:8001/api/v1/services/aigc/text-to-speech/synthesis
- 请求方式: POST
- 认证方式: Bearer <代理Key>
- 预期: 返回音频二进制流，保存为output.wav

使用方法:
1. 确保AIProxy和OpenResty已启动，并已配置好API Key映射
2. python test/integration/test_dashscope_proxy_tts.py
"""

import requests
import json
import os

PROXY_URL = "http://localhost:8001/api/v1/services/aigc/text-to-speech/synthesis"
PROXY_KEY = "sk-bailian-tester-001"  # 你的代理Key
OUTPUT_FILE = "output.wav"

def test_dashscope_tts_proxy():
    """测试通过AIProxy代理访问DashScope TTS API"""
    
    print("开始测试AIProxy代理DashScope TTS API...")
    print(f"代理端点: {PROXY_URL}")
    print(f"使用代理Key: {PROXY_KEY}")
    
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {PROXY_KEY}",
        "Content-Type": "application/json"
    }
    
    # 构建请求体（按照DashScope原生API格式）
    request_data = {
        "model": "cosyvoice-v1",
        "input": {
            "text": "你好，这是通过AIProxy代理访问的DashScope语音合成测试。"
        },
        "parameters": {
            "voice": "longxiaochun",
            "format": "wav"
        }
    }
    
    print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    
    try:
        # 发送POST请求
        print("发送请求...")
        response = requests.post(PROXY_URL, headers=headers, json=request_data, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            print(f"响应内容类型: {content_type}")
            
            if 'audio' in content_type or 'octet-stream' in content_type:
                # 保存音频文件
                with open(OUTPUT_FILE, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                print(f"成功生成音频文件: {OUTPUT_FILE}")
                print(f"文件大小: {file_size} 字节")
                
                if file_size > 0:
                    print("✓ 测试成功：AIProxy正确代理了DashScope TTS API")
                    return True
                else:
                    print("✗ 测试失败：音频文件为空")
                    return False
            else:
                # 可能是JSON响应，打印内容
                try:
                    response_json = response.json()
                    print(f"JSON响应: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
                except:
                    print(f"响应内容: {response.text}")
                
                print("✗ 测试失败：未收到音频数据")
                return False
        
        elif response.status_code == 404:
            print("✗ 测试失败：404错误 - AIProxy可能未配置此端点")
            print("建议检查channels_config.json中是否配置了DashScope TTS端点")
            return False
        
        elif response.status_code == 401:
            print("✗ 测试失败：401错误 - API Key无效或未配置")
            print("建议检查api_keys.json中的API Key配置")
            return False
        
        else:
            print(f"✗ 测试失败：HTTP {response.status_code}")
            try:
                error_info = response.json()
                print(f"错误信息: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误信息: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("✗ 测试失败：连接错误 - 请确保AIProxy服务已启动")
        print("运行 ./start.sh 启动服务")
        return False
    
    except requests.exceptions.Timeout:
        print("✗ 测试失败：请求超时")
        return False
    
    except Exception as e:
        print(f"✗ 测试失败：未知错误 - {str(e)}")
        return False

def cleanup():
    """清理测试文件"""
    if os.path.exists(OUTPUT_FILE):
        try:
            os.remove(OUTPUT_FILE)
            print(f"已清理测试文件: {OUTPUT_FILE}")
        except:
            pass

if __name__ == "__main__":
    print("=" * 60)
    print("AIProxy DashScope TTS API 代理测试")
    print("=" * 60)
    
    try:
        success = test_dashscope_tts_proxy()
        
        print("\n" + "=" * 60)
        if success:
            print("测试结果: 成功 ✓")
            print("AIProxy正确代理了DashScope TTS API")
        else:
            print("测试结果: 失败 ✗")
            print("AIProxy未能正确代理DashScope TTS API")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        cleanup()
    except Exception as e:
        print(f"\n测试异常: {e}")
        cleanup() 