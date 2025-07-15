#!/usr/bin/env python3
"""
CosyVoice语音合成SDK测试
基于官方DashScope Python SDK实现
官方文档：https://help.aliyun.com/document_detail/2712523.html
"""

import os
import sys
import time
import unittest
import subprocess
from http import HTTPStatus
import platform

class CosyVoiceClient:
    """封装的CosyVoice调用客户端"""
    
    def __init__(self, dashscope):
        self.dashscope = dashscope

    def synthesize(self, text):
        """语音合成"""
        print(f"🔗 正在调用语音合成服务...")
        from dashscope.audio.tts_v2 import SpeechSynthesizer
        speech_synthesizer = SpeechSynthesizer(model='cosyvoice-v2',
                                               voice='longhua_v2',
                                               callback=None)
        audio = speech_synthesizer.call(text)
        return {
            'audio': audio,
            'request_id': speech_synthesizer.get_last_request_id(),
            'first_package_delay': speech_synthesizer.get_first_package_delay()
        }


class TestCosyVoiceSDK(unittest.TestCase):
    """CosyVoice语音合成SDK测试类"""

    @unittest.skip("skip")
    def test_cosyvoice_synthesis_direct(self):
        test_text = "我是通过官方接口生成的哦"
        test_audio_file = "test_cosyvoice_direct_result.mp3"
        print("🔧 设置官方直连环境变量...")
        os.environ["DASHSCOPE_HTTP_BASE_URL"] = "https://dashscope.aliyuncs.com/api/v1"
        os.environ["DASHSCOPE_WEBSOCKET_BASE_URL"] = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
        import dashscope
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        from dashscope.audio.tts_v2 import SpeechSynthesizer
        print(f"✅ HTTP Base URL: {os.environ.get('DASHSCOPE_HTTP_BASE_URL')}")
        print(f"✅ WebSocket Base URL: {os.environ.get('DASHSCOPE_WEBSOCKET_BASE_URL')}")

        # 创建客户端实例
        try:
            self.client = CosyVoiceClient(dashscope)
        except ValueError as e:
            self.skipTest(f"配置错误: {e}")
        try:
            # 调用语音合成
            result = self.client.synthesize(test_text)
            self.check_result_audio(result, test_audio_file)

        except Exception as e:
            print(f"❌ 测试异常: {e}")

    def test_cosyvoice_synthesis_proxy(self):
        test_text = "我是通过代理服务转发生成的哦"
        test_audio_file = "test_cosyvoice_proxy_result.mp3"

        print("🔧 设置代理环境变量...")
        os.environ["DASHSCOPE_HTTP_BASE_URL"] = "https://aiproxy.bwton.cn/api/v1"
        os.environ["DASHSCOPE_WEBSOCKET_BASE_URL"] = "wss://aiproxy.bwton.cn/api-ws/v1/inference"
        import dashscope
        dashscope.api_key = os.getenv("AIPROXY_API_KEY")
        from dashscope.audio.tts_v2 import SpeechSynthesizer
        print(f"✅ HTTP Base URL: {os.environ.get('DASHSCOPE_HTTP_BASE_URL')}")
        print(f"✅ WebSocket Base URL: {os.environ.get('DASHSCOPE_WEBSOCKET_BASE_URL')}")

        # 创建客户端实例
        try:
            self.client = CosyVoiceClient(dashscope)
        except ValueError as e:
            self.skipTest(f"配置错误: {e}")
        try:
            # 调用语音合成
            result = self.client.synthesize(test_text)
            self.check_result_audio(result, test_audio_file)

        except Exception as e:
            print(f"❌ 测试异常: {e}")

    def check_result_audio(self, result, test_audio_file):
        # 检查返回结果
        if result['audio'] and len(result['audio']) > 0:
            print(f"✅ 语音合成成功")
            
            # 保存音频文件
            with open(test_audio_file, 'wb') as f:
                f.write(result['audio'])

            print(f"💾 音频文件保存到: {test_audio_file}")
            print(f"📊 音频文件大小: {len(result['audio'])} 字节")
            print(f"📊 请求ID: {result['request_id']}")
            print(f"⏱️ 首包延迟: {result['first_package_delay']}ms")

            #播放音频
            self.playsound(test_audio_file)

            # 验证文件生成
            self.assertTrue(os.path.exists(test_audio_file))
            self.assertGreater(os.path.getsize(test_audio_file), 0)

            print(f"🎉 模式语音合成测试成功！")
        else:
            print("⚠️ 收到空的音频数据")

    def playsound(self, audio_file):
        """播放音频文件"""
        if not os.path.exists(audio_file):
            print(f"音频文件不存在: {audio_file}")
            return False
            
        print(f"准备播放音频文件: {audio_file}")
        
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", audio_file])
                print("音频播放完成")
            elif system == "Linux":
                # 尝试不同的Linux音频播放器
                players = ["mpg123", "mplayer", "vlc", "paplay"]
                for player in players:
                    try:
                        subprocess.run([player, audio_file], check=True)
                        print("音频播放完成")
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                print("未找到可用的音频播放器")
                return False
            elif system == "Windows":
                os.startfile(audio_file)
                print("已使用默认播放器打开音频文件")
            else:
                print(f"不支持的操作系统: {system}")
                return False
                
            return True
            
        except Exception as e:
            print(f"播放音频时出错: {e}")
            return False

    def tearDown(self):
        """测试后的清理工作"""
        # 保留主测试文件，清理其他测试文件
        pass


if __name__ == '__main__':
    print("🚀 CosyVoice SDK测试启动")
    print("=" * 60)
    unittest.main()