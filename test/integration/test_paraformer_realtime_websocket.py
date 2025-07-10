#!/usr/bin/env python3
"""
Paraformer实时语音识别WebSocket API测试
基于官方文档：https://help.aliyun.com/zh/model-studio/websocket-for-paraformer-real-time-service
"""

import websocket
import json
import uuid
import os
import time
import threading
import subprocess
import platform
import unittest
import io
import wave
import tempfile


class ParaformerRealtimeASRClient:
    def __init__(self, api_key, uri, audio_file=None):
        """
        初始化 ParaformerRealtimeASRClient 实例

        参数:
            api_key (str): 鉴权用的 API Key
            uri (str): WebSocket 服务地址
            audio_file (str): 音频文件路径，如果为None则生成测试音频
        """
        self.api_key = api_key
        self.uri = uri
        self.task_id = str(uuid.uuid4())
        self.audio_file = audio_file
        self.ws = None
        self.task_started = False
        self.task_finished = False
        self.recognition_results = []
        self.error_occurred = False
        self.error_message = ""
        self.final_result = ""

    def _get_audio_format(self, audio_file):
        """根据文件扩展名确定音频格式"""
        if not audio_file:
            return "mp3"
        
        ext = os.path.splitext(audio_file)[1].lower()
        format_map = {
            '.wav': 'wav',
            '.mp3': 'mp3',
            '.pcm': 'pcm',
            '.opus': 'opus',
            '.speex': 'speex',
            '.aac': 'aac',
            '.amr': 'amr'
        }
        return format_map.get(ext, 'mp3')  # 默认为mp3
    
    def _get_audio_sample_rate(self, audio_file):
        """获取音频文件的采样率"""
        if not audio_file or not os.path.exists(audio_file):
            return 16000  # 默认采样率
        
        try:
            # 使用ffprobe获取音频信息
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', audio_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                for stream in info.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        sample_rate = stream.get('sample_rate')
                        if sample_rate:
                            return int(sample_rate)
            
            print("⚠️ 无法获取音频采样率，使用默认值16000")
            return 16000
            
        except Exception as e:
            print(f"⚠️ 获取音频采样率失败: {e}，使用默认值16000")
            return 16000

    def on_open(self, ws):
        """
        WebSocket 连接建立时回调函数
        发送 run-task 指令开启语音识别任务
        """
        print("✅ WebSocket 连接已建立")

        # 构造 run-task 指令
        run_task_cmd = {
            "header": {
                "action": "run-task",
                "task_id": self.task_id,
                "streaming": "duplex"
            },
            "payload": {
                "task_group": "audio",
                "task": "asr",
                "function": "recognition",
                "model": "paraformer-realtime-v2",
                "parameters": {
                    "format": self._get_audio_format(self.audio_file),
                    "sample_rate": self._get_audio_sample_rate(self.audio_file),
                    "disfluency_removal_enabled": True,
                    "language_hints": ["zh"]
                },
                "input": {}
            }
        }

        # 发送 run-task 指令
        ws.send(json.dumps(run_task_cmd))
        print("📤 已发送 run-task 指令")

    def on_message(self, ws, message):
        """
        接收到消息时的回调函数
        处理JSON文本消息（识别结果）
        """
        if isinstance(message, str):
            # 处理 JSON 文本消息
            try:
                msg_json = json.loads(message)
                print(f"📨 收到 JSON 消息: {msg_json}")

                if "header" in msg_json:
                    header = msg_json["header"]

                    if "event" in header:
                        event = header["event"]

                        if event == "task-started":
                            print("🚀 任务已启动")
                            self.task_started = True
                            # 开始发送音频数据
                            self._send_audio_data()

                        elif event == "result-generated":
                            print("📝 收到识别结果")
                            if "payload" in msg_json and "output" in msg_json["payload"]:
                                output = msg_json["payload"]["output"]
                                print(f"🔍 输出内容: {output}")
                                if "sentence" in output:
                                    sentence = output["sentence"]
                                    text = sentence.get("text", "")
                                    words = sentence.get("words", [])
                                    print(f"📝 句子信息: text='{text}', words={len(words)}")
                                    if text:
                                        print(f"🎯 识别文本: {text}")
                                        self.recognition_results.append(text)
                                        
                                        # 检查是否是最终结果
                                        if sentence.get("end_time") is not None:
                                            self.final_result = text
                                            print(f"✅ 最终识别结果: {text}")
                                    elif words:
                                        # 有时候文本在words中
                                        word_texts = [w.get("text", "") for w in words]
                                        if word_texts:
                                            combined_text = "".join(word_texts)
                                            print(f"🎯 从词汇中组合的文本: {combined_text}")
                                            self.recognition_results.append(combined_text)

                        elif event == "task-finished":
                            print("✅ 任务已完成")
                            self.task_finished = True
                            self.close(ws)

                        elif event == "task-failed":
                            error_msg = header.get("error_message", "未知错误")
                            error_code = header.get("error_code", "unknown")
                            print(f"❌ 任务失败: [{error_code}] {error_msg}")
                            self.error_occurred = True
                            self.error_message = f"[{error_code}] {error_msg}"
                            self.task_finished = True
                            self.close(ws)

            except json.JSONDecodeError as e:
                print(f"❌ JSON 解析失败: {e}")
        else:
            # 语音识别通常不会收到二进制消息
            print(f"📨 收到二进制消息，大小: {len(message)} 字节")

    def on_error(self, ws, error):
        """发生错误时的回调"""
        print(f"❌ WebSocket 错误: {error}")
        self.error_occurred = True
        self.error_message = str(error)

    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭时的回调"""
        print(f"🔌 WebSocket 连接已关闭: {close_msg} ({close_status_code})")

    def _send_audio_data(self):
        """发送音频数据"""
        def send_audio():
            try:
                print(f"📤 开始发送音频文件: {self.audio_file}")
                
                # 检查文件是否存在
                if not os.path.exists(self.audio_file):
                    print(f"❌ 音频文件不存在: {self.audio_file}")
                    return
                
                # 读取音频文件并分块发送
                with open(self.audio_file, 'rb') as f:
                    chunk_size = 1024  # 每次发送1024字节
                    chunk_count = 0
                    
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        
                        # 发送二进制音频数据
                        self.ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
                        chunk_count += 1
                        print(f"📤 发送音频块 {chunk_count}, 大小: {len(chunk)} 字节")
                        
                        # 模拟实时发送，每100ms发送一次
                        time.sleep(0.1)
                
                print("📤 音频发送完成")
                
                # 发送 finish-task 指令
                self._send_finish_task()
                
            except Exception as e:
                print(f"❌ 发送音频数据时出错: {e}")
                self.error_occurred = True
                self.error_message = str(e)
        
        # 在单独线程中发送音频数据
        audio_thread = threading.Thread(target=send_audio)
        audio_thread.daemon = True
        audio_thread.start()

    def _send_finish_task(self):
        """发送 finish-task 指令，结束语音识别任务"""
        cmd = {
            "header": {
                "action": "finish-task",
                "task_id": self.task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {}
            }
        }

        self.ws.send(json.dumps(cmd))
        print("📤 已发送 finish-task 指令")

    def close(self, ws):
        """主动关闭连接"""
        if ws and ws.sock and ws.sock.connected:
            ws.close()
            print("🔌 已主动关闭连接")

    def run(self):
        """启动 WebSocket 客户端"""
        # 设置请求头部（鉴权）
        header = {
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-DataInspection": "enable"
        }

        # 创建 WebSocketApp 实例
        self.ws = websocket.WebSocketApp(
            self.uri,
            header=header,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        print("🔗 正在连接 WebSocket...")
        self.ws.run_forever()

    def run_test(self, timeout=30):
        """运行测试并等待结果"""
        print("=" * 80)
        print("🎤 Paraformer实时语音识别WebSocket API测试")
        print("=" * 80)

        # 检查音频文件
        if not self.audio_file:
            print("❌ 错误: 未指定音频文件")
            return False
        
        if not os.path.exists(self.audio_file):
            print(f"❌ 错误: 音频文件不存在: {self.audio_file}")
            return False
        
        print(f"📁 使用音频文件: {self.audio_file}")
        print(f"🎵 音频格式: {self._get_audio_format(self.audio_file)}")
        print(f"🔊 采样率: {self._get_audio_sample_rate(self.audio_file)}Hz")

        # 在单独线程中运行WebSocket
        ws_thread = threading.Thread(target=self.run)
        ws_thread.daemon = True
        ws_thread.start()

        # 等待测试完成或超时
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.task_finished or self.error_occurred:
                break
            time.sleep(0.1)

        # 输出测试结果
        print("\n" + "=" * 80)
        print("📊 测试结果")
        print("=" * 80)

        if self.error_occurred:
            print(f"❌ 测试失败: {self.error_message}")
            return False
        elif self.task_finished:
            print("✅ WebSocket 连接成功")
            print(f"✅ 任务启动: {'成功' if self.task_started else '失败'}")
            print(f"✅ 识别结果数量: {len(self.recognition_results)}")
            print(f"✅ 任务完成: {'成功' if self.task_finished else '失败'}")

            if self.recognition_results:
                print("📝 识别结果:")
                for i, result in enumerate(self.recognition_results, 1):
                    print(f"  {i}. {result}")
                
                if self.final_result:
                    print(f"🎯 最终结果: {self.final_result}")
                
                return True
            else:
                print("⚠️ 未收到识别结果")
                return False
        else:
            print("⏰ 测试超时")
            return False

    def cleanup(self):
        """清理测试文件"""
        # 无需清理，直接使用原始音频文件
        pass


class TestParaformerRealtime(unittest.TestCase):
    def setUp(self):
        pass

    @unittest.skip("Reason")
    def test_paraformer_realtime_direct(self):
        """直接对接Paraformer实时语音识别WebSocket API测试"""

        # 从环境变量获取API Key
        api_key = os.getenv("DASHSCOPE_API_KEY")

        if not api_key:
            print("❌ 错误: 未设置 DASHSCOPE_API_KEY 环境变量")
            print("请设置环境变量: export DASHSCOPE_API_KEY=your_api_key")
            return False

        print(f"🔑 使用API Key: {api_key[:10]}...")

        # WebSocket服务地址 - 直接连接官方API
        server_uri = "wss://dashscope.aliyuncs.com/api-ws/v1/inference/"

        print(f"🌐 直接连接官方服务: {server_uri}")

        # 创建客户端并运行测试
        audio_file = "cosyvoice_output_1752115478.mp3"
        client = ParaformerRealtimeASRClient(api_key, server_uri, audio_file)

        try:
            success = client.run_test(timeout=60)

            if success:
                print("\n🎉 Paraformer实时语音识别WebSocket API 直接对接测试成功！")
                print("💡 阿里云百炼平台的语音识别服务正常工作")
            else:
                print("\n❌ Paraformer实时语音识别WebSocket API 直接对接测试失败")

            return success

        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
        finally:
            # 清理测试文件
            client.cleanup()

    #@unittest.skip("Reason")
    def test_paraformer_realtime_proxy(self):
        """通过AIProxy代理访问Paraformer实时语音识别WebSocket API测试"""

        # 从环境变量获取API Key
        api_key = os.getenv("AIPROXY_API_KEY")

        if not api_key:
            print("❌ 错误: 未设置 AIPROXY_API_KEY 环境变量")
            print("请设置环境变量: export AIPROXY_API_KEY=your_api_key")
            return False

        print(f"🔑 使用API Key: {api_key[:10]}...")

        # WebSocket服务地址 - 通过AIProxy代理
        server_uri = "ws://localhost:8001/api-ws/v1/inference"

        print(f"🌐 通过AIProxy代理访问: {server_uri}")

        # 创建客户端并运行测试
        audio_file = "cosyvoice_output_1752115478.mp3"
        client = ParaformerRealtimeASRClient(api_key, server_uri, audio_file)

        try:
            success = client.run_test(timeout=60)

            if success:
                print("\n🎉 Paraformer实时语音识别WebSocket API 通过AIProxy代理测试成功！")
                print("💡 阿里云百炼平台的语音识别服务正常工作")
            else:
                print("\n❌ Paraformer实时语音识别WebSocket API 通过AIProxy代理测试失败")

            return success

        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
        finally:
            # 清理测试文件
            client.cleanup()


if __name__ == "__main__":
    unittest.main() 