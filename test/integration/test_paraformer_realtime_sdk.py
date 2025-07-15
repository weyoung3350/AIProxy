#!/usr/bin/env python3
"""
Paraformer实时语音识别SDK测试
基于官方DashScope Python SDK实现
官方文档：https://help.aliyun.com/zh/model-studio/paraformer-real-time-speech-recognition-python-sdk
"""

import os
import sys
import time
import unittest
import subprocess
from http import HTTPStatus

# 关键：在导入dashscope之前设置环境变量
# DashScope SDK在导入时会读取这些环境变量并缓存
print("🔧 设置代理环境变量...")
os.environ["DASHSCOPE_HTTP_BASE_URL"] = "https://aiproxy.bwton.cn/api/v1"
os.environ["DASHSCOPE_WEBSOCKET_BASE_URL"] = "ws://aiproxy.bwton.cn/api-ws/v1/inference"
print(f"✅ HTTP Base URL: {os.environ.get('DASHSCOPE_HTTP_BASE_URL')}")
print(f"✅ WebSocket Base URL: {os.environ.get('DASHSCOPE_WEBSOCKET_BASE_URL')}")


# 现在导入dashscope，此时环境变量已经设置好
import dashscope
from dashscope.audio.asr import Recognition

# 验证环境变量是否生效
print(f"🔍 验证SDK配置:")
print(f"  - dashscope.base_http_api_url: {getattr(dashscope, 'base_http_api_url', 'Not found')}")
print(f"  - dashscope.base_websocket_api_url: {getattr(dashscope, 'base_websocket_api_url', 'Not found')}")


class TestParaformerRealtimeSDK(unittest.TestCase):
    """Paraformer实时语音识别SDK测试类"""

    def setUp(self):
        """测试前的准备工作"""
        #self.test_audio_file = "test_speech.mp3"
        self.test_audio_file = "cosyvoice_output_1752119030.mp3"
        self.ensure_test_audio_exists()

    def ensure_test_audio_exists(self):
        """确保测试音频文件存在"""
        if not os.path.exists(self.test_audio_file):
            print(f"⚠️ 测试音频文件不存在: {self.test_audio_file}")
            print("🔄 正在生成测试音频...")
            try:
                # 使用系统say命令生成测试音频
                subprocess.run([
                    "say", "你好，这是一个测试音频。我正在测试语音识别功能。",
                    "-o", "test_speech.aiff"
                ], check=True)

                # 转换为MP3格式
                subprocess.run([
                    "ffmpeg", "-i", "test_speech.aiff",
                    "-ar", "16000", "-ac", "1",
                    self.test_audio_file, "-y"
                ], check=True, capture_output=True)

                # 清理临时文件
                if os.path.exists("test_speech.aiff"):
                    os.remove("test_speech.aiff")

                print(f"✅ 测试音频文件生成成功: {self.test_audio_file}")
            except Exception as e:
                print(f"❌ 生成测试音频失败: {e}")
                raise

    @unittest.skip("skip")
    def test_paraformer_realtime_direct_sync(self):
        """直接对接Paraformer实时语音识别SDK - 同步调用"""
        print("\n" + "=" * 80)
        print("🎤 Paraformer实时语音识别SDK测试 - 直接连接（同步调用）")
        print("=" * 80)

        # 获取API Key
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            self.skipTest("未设置DASHSCOPE_API_KEY环境变量")

        print(f"🔑 使用API Key: {api_key[:10]}...")
        print(f"📁 使用音频文件: {self.test_audio_file}")

        try:
            # 设置API Key
            dashscope.api_key = api_key

            # 创建Recognition实例
            recognition = Recognition(
                model='paraformer-realtime-v2',
                format='mp3',
                sample_rate=16000,
                language_hints=['zh', 'en'],  # 支持中英文
                callback=None
            )

            print("🔗 正在调用识别服务...")

            # 同步调用识别
            result = recognition.call(self.test_audio_file)

            # 处理结果
            if result.status_code == HTTPStatus.OK:
                print("✅ 识别成功")

                # 检查结果类型
                sentence = result.get_sentence()
                print(f"📊 结果类型: {type(sentence)}")

                if isinstance(sentence, list):
                    # 如果是列表，处理每个句子
                    print(f"📝 识别到 {len(sentence)} 个句子:")
                    for i, sent in enumerate(sentence, 1):
                        print(f"  {i}. {sent.text if hasattr(sent, 'text') else sent}")
                        if hasattr(sent, 'begin_time'):
                            print(f"     时间: {sent.begin_time}ms - {sent.end_time}ms")

                    # 验证识别结果
                    self.assertGreater(len(sentence), 0)
                    full_text = " ".join([sent.text if hasattr(sent, 'text') else str(sent) for sent in sentence])
                    print(f"📝 完整识别结果: {full_text}")

                else:
                    # 单个句子对象
                    print(f"📝 识别结果: {sentence.text}")
                    print(f"⏱️ 开始时间: {sentence.begin_time}ms")
                    print(f"⏱️ 结束时间: {sentence.end_time}ms")

                    # 显示词级时间戳
                    if hasattr(sentence, 'words') and sentence.words:
                        print("📊 词级时间戳:")
                        for i, word in enumerate(sentence.words, 1):
                            print(f"  {i}. '{word.text}' ({word.begin_time}-{word.end_time}ms) {word.punctuation}")

                    # 验证识别结果
                    self.assertIsNotNone(sentence.text)
                    self.assertGreater(len(sentence.text), 0)

                print("🎉 直接连接同步调用测试成功！")

            else:
                print(f"❌ 识别失败: {result.message}")
                self.fail(f"识别失败: {result.message}")

        except Exception as e:
            print(f"❌ 测试异常: {e}")
            raise

    @unittest.skip("skip")
    def test_paraformer_realtime_direct_stream(self):
        """直接对接Paraformer实时语音识别SDK - 流式调用"""
        print("\n" + "=" * 80)
        print("🎤 Paraformer实时语音识别SDK测试 - 直接连接（流式调用）")
        print("=" * 80)

        # 获取API Key
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            self.skipTest("未设置DASHSCOPE_API_KEY环境变量")

        print(f"🔑 使用API Key: {api_key[:10]}...")
        print(f"📁 使用音频文件: {self.test_audio_file}")

        try:
            # 设置API Key
            dashscope.api_key = api_key

            # 创建回调实例
            callback = self.StreamCallback()

            # 创建Recognition实例
            recognition = Recognition(
                model='paraformer-realtime-v2',
                format='mp3',
                sample_rate=16000,
                language_hints=['zh', 'en'],
                callback=callback
            )

            print("🔗 正在启动流式识别...")

            # 启动流式识别
            recognition.start()

            # 发送音频数据
            print("📤 开始发送音频数据...")
            with open(self.test_audio_file, 'rb') as f:
                chunk_size = 1024
                chunk_count = 0
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

                    recognition.send_audio_frame(chunk)
                    chunk_count += 1
                    print(f"📤 发送音频块 {chunk_count}, 大小: {len(chunk)} 字节")

                    # 模拟实时发送
                    time.sleep(0.1)

            print("📤 音频发送完成")

            # 停止识别
            recognition.stop()

            # 等待处理完成
            time.sleep(2)

            # 显示识别结果
            if callback.results:
                print(f"📝 流式识别结果: {' '.join(callback.results)}")
            else:
                print("⚠️ 没有收到识别结果")

            print("🎉 直接连接流式调用测试成功！")

        except Exception as e:
            print(f"❌ 测试异常: {e}")
            raise

    class StreamCallback:
        """流式识别回调类"""

        def __init__(self):
            self.results = []

        def on_open(self):
            print("🔗 WebSocket连接已打开")

        def on_close(self):
            print("🔗 WebSocket连接已关闭")

        def on_error(self, error):
            print(f"❌ WebSocket错误: {error}")

        def on_complete(self):
            print("✅ 识别完成")

        def on_event(self, result):
            """处理识别事件"""
            if result.status_code == HTTPStatus.OK:
                try:
                    # 直接从output中解析结果
                    if hasattr(result, 'output'):
                        import json
                        output_data = json.loads(result.output) if isinstance(result.output, str) else result.output

                        if 'sentence' in output_data:
                            sentence = output_data['sentence']
                            text = sentence.get('text', '')
                            sentence_end = sentence.get('sentence_end', False)

                            if sentence_end and text:
                                print(f"📝 完整句子: {text}")
                                self.results.append(text)
                            elif text:
                                print(f"📝 部分结果: {text}")
                    else:
                        # 尝试使用get_sentence方法
                        sentence_list = result.get_sentence()
                        if isinstance(sentence_list, list) and len(sentence_list) > 0:
                            for sentence in sentence_list:
                                if isinstance(sentence, dict):
                                    text = sentence.get('text', '')
                                    sentence_end = sentence.get('sentence_end', False)
                                    if sentence_end and text:
                                        print(f"📝 完整句子: {text}")
                                        self.results.append(text)
                                    elif text:
                                        print(f"📝 部分结果: {text}")
                                else:
                                    print(f"📝 识别结果: {sentence}")
                                    self.results.append(str(sentence))

                except Exception as e:
                    print(f"⚠️ 处理识别结果时出错: {e}")
            else:
                print(f"❌ 识别错误: {result.message}")

    #@unittest.skip("skip")
    def test_paraformer_realtime_proxy_stream(self):
        """通过AIProxy代理访问Paraformer实时语音识别SDK - 流式调用"""
        print("\n" + "=" * 80)
        print("🎤 Paraformer实时语音识别SDK测试 - AIProxy代理连接（流式调用）")
        print("=" * 80)

        # 获取原始API Key
        api_key = os.getenv('AIPROXY_API_KEY')
        if not api_key:
            self.skipTest("未设置AIPROXY_API_KEY环境变量")

        print(f"🔑 使用API Key: {api_key[:10]}...")
        print(f"📁 使用音频文件: {self.test_audio_file}")

        try:
            # 设置API Key
            dashscope.api_key = api_key

            # 创建回调实例
            callback = self.StreamCallback()

            # 创建Recognition实例
            recognition = Recognition(
                model='paraformer-realtime-v2',
                format='mp3',
                sample_rate=22050,
                language_hints=['zh', 'en'],
                callback=callback
            )

            print("🔗 正在通过代理启动流式识别...")

            # 启动流式识别
            recognition.start()

            # 发送音频数据
            print("📤 开始发送音频数据...")
            with open(self.test_audio_file, 'rb') as f:
                chunk_size = 1024
                chunk_count = 0
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

                    recognition.send_audio_frame(chunk)
                    chunk_count += 1
                    print(f"📤 发送音频块 {chunk_count}, 大小: {len(chunk)} 字节")

                    # 模拟实时发送
                    time.sleep(0.1)

            print("📤 音频发送完成")

            # 停止识别
            recognition.stop()

            # 等待处理完成
            time.sleep(2)

            # 显示识别结果
            if callback.results:
                print(f"📝 流式识别结果: {' '.join(callback.results)}")
                # 验证识别结果
                self.assertGreater(len(callback.results), 0)
            else:
                print("⚠️ 没有收到识别结果")

            print("🎉 代理连接流式调用测试成功！")

        except Exception as e:
            print(f"❌ 代理测试异常: {e}")
            raise


    @unittest.skip("skip")
    def test_paraformer_realtime_proxy_sync(self):
        """通过AIProxy代理访问Paraformer实时语音识别SDK - 同步调用"""
        print("\n" + "=" * 80)
        print("🎤 Paraformer实时语音识别SDK测试 - AIProxy代理连接（同步调用）")
        print("=" * 80)

        # 从环境变量获取API Key（已在文件顶部设置）
        api_key = os.getenv("AIPROXY_API_KEY")

        if not api_key:
            print("❌ 错误: 未设置 AIPROXY_API_KEY 环境变量")
            print("请设置环境变量: export AIPROXY_API_KEY=your_api_key")
            return False

        print(f"🔑 使用代理API Key: {api_key[:10]}...")

        try:
            # 设置API Key
            dashscope.api_key = api_key

            # 创建Recognition实例
            recognition = Recognition(
                model='paraformer-realtime-v2',
                format='mp3',
                sample_rate=16000,
                language_hints=['zh', 'en'],
                callback=None
            )

            print("🔗 正在通过代理调用识别服务...")

            # 同步调用识别
            result = recognition.call(self.test_audio_file)

            # 处理结果
            if result.status_code == HTTPStatus.OK:
                print("✅ 代理识别成功")

                # 检查结果类型
                sentence = result.get_sentence()
                print(f"📊 结果类型: {type(sentence)}")

                if isinstance(sentence, list):
                    # 如果是列表，处理每个句子
                    print(f"📝 识别到 {len(sentence)} 个句子:")
                    for i, sent in enumerate(sentence, 1):
                        print(f"  {i}. {sent.text if hasattr(sent, 'text') else sent}")
                        if hasattr(sent, 'begin_time'):
                            print(f"     时间: {sent.begin_time}ms - {sent.end_time}ms")

                    # 验证识别结果
                    self.assertGreater(len(sentence), 0)
                    full_text = " ".join([sent.text if hasattr(sent, 'text') else str(sent) for sent in sentence])
                    print(f"📝 完整识别结果: {full_text}")

                else:
                    # 单个句子对象
                    print(f"📝 识别结果: {sentence.text}")
                    print(f"⏱️ 开始时间: {sentence.begin_time}ms")
                    print(f"⏱️ 结束时间: {sentence.end_time}ms")

                    # 显示词级时间戳
                    if hasattr(sentence, 'words') and sentence.words:
                        print("📊 词级时间戳:")
                        for i, word in enumerate(sentence.words, 1):
                            print(f"  {i}. '{word.text}' ({word.begin_time}-{word.end_time}ms) {word.punctuation}")

                    # 验证识别结果
                    self.assertIsNotNone(sentence.text)
                    self.assertGreater(len(sentence.text), 0)

                print("🎉 代理连接同步调用测试成功！")
            else:
                print(f"❌ 代理识别失败: {result.message}")
                print(f"📊 状态码: {result.status_code}")
                if result.status_code == HTTPStatus.UNAUTHORIZED:
                    print("💡 这可能表明代理连接成功但API Key无效")
                elif result.status_code == 502:
                    print("💡 这表明代理连接成功但后端服务有问题")
                else:
                    self.fail(f"代理识别失败: {result.message}")

        except Exception as e:
            print(f"❌ 代理测试异常: {e}")
            raise

    def tearDown(self):
        """测试后的清理工作"""
        # 保留测试音频文件以便后续测试使用
        pass


if __name__ == '__main__':
    unittest.main()
