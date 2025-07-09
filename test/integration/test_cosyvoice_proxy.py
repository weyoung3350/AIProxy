#!/usr/bin/env python3
"""
CosyVoice WebSocket API 代理测试
通过AIProxy代理服务连接阿里云百炼平台CosyVoice语音合成API
"""

import websocket
import json
import uuid
import os
import time
import threading
import subprocess
import platform


class CosyVoiceProxyTTSClient:
    def __init__(self, api_key, proxy_uri):
        """
        初始化 CosyVoiceProxyTTSClient 实例

        参数:
            api_key (str): 代理密钥（将被代理服务替换为真实API Key）
            proxy_uri (str): AIProxy代理服务的WebSocket地址
        """
        self.api_key = api_key
        self.proxy_uri = proxy_uri
        self.task_id = str(uuid.uuid4())
        self.output_file = f"cosyvoice_proxy_output_{int(time.time())}.mp3"
        self.ws = None
        self.task_started = False
        self.task_finished = False
        self.audio_received = False
        self.error_occurred = False
        self.error_message = ""

    def on_open(self, ws):
        """
        WebSocket 连接建立时回调函数
        发送 run-task 指令开启语音合成任务
        """
        print("✅ WebSocket 代理连接已建立")

        # 构造 run-task 指令
        run_task_cmd = {
            "header": {
                "action": "run-task",
                "task_id": self.task_id,
                "streaming": "duplex"
            },
            "payload": {
                "task_group": "audio",
                "task": "tts",
                "function": "SpeechSynthesizer",
                "model": "cosyvoice-v2",
                "parameters": {
                    "text_type": "PlainText",
                    "voice": "longxiaochun_v2",
                    "format": "mp3",
                    "sample_rate": 22050,
                    "volume": 50,
                    "rate": 1,
                    "pitch": 1
                },
                "input": {}
            }
        }

        # 发送 run-task 指令
        ws.send(json.dumps(run_task_cmd))
        print("📤 已通过代理发送 run-task 指令")

    def on_message(self, ws, message):
        """
        接收到消息时的回调函数
        区分文本和二进制消息处理
        """
        if isinstance(message, str):
            # 处理 JSON 文本消息
            try:
                msg_json = json.loads(message)
                print(f"📨 收到代理转发的 JSON 消息: {msg_json}")

                if "header" in msg_json:
                    header = msg_json["header"]

                    if "event" in header:
                        event = header["event"]

                        if event == "task-started":
                            print("🚀 任务已通过代理启动")
                            self.task_started = True

                            # 发送测试文本
                            test_texts = [
                                "你好，这是通过AIProxy代理服务连接的CosyVoice语音合成测试。",
                                "代理服务正在将我的请求转发到阿里云百炼平台，效果如何？"
                            ]

                            for text in test_texts:
                                self.send_continue_task(text)

                            # 发送完成指令
                            self.send_finish_task()

                        elif event == "task-finished":
                            print("✅ 任务已通过代理完成")
                            self.task_finished = True
                            self.close(ws)

                        elif event == "task-failed":
                            error_msg = msg_json.get("error_message", "未知错误")
                            print(f"❌ 任务通过代理失败: {error_msg}")
                            self.error_occurred = True
                            self.error_message = error_msg
                            self.task_finished = True
                            self.close(ws)

                        elif event == "result-generated":
                            print("🎵 正在通过代理接收音频数据...")

            except json.JSONDecodeError as e:
                print(f"❌ JSON 解析失败: {e}")
        else:
            # 处理二进制消息（音频数据）
            print(f"🎵 收到代理转发的音频数据块，大小: {len(message)} 字节")
            self.audio_received = True
            with open(self.output_file, "ab") as f:
                f.write(message)

    def on_error(self, ws, error):
        """发生错误时的回调"""
        print(f"❌ WebSocket 代理错误: {error}")
        self.error_occurred = True
        self.error_message = str(error)

    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭时的回调"""
        print(f"🔌 WebSocket 代理连接已关闭: {close_msg} ({close_status_code})")

    def send_continue_task(self, text):
        """发送 continue-task 指令，附带要合成的文本内容"""
        cmd = {
            "header": {
                "action": "continue-task",
                "task_id": self.task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {
                    "text": text
                }
            }
        }

        self.ws.send(json.dumps(cmd))
        print(f"📤 已通过代理发送文本: {text}")

    def send_finish_task(self):
        """发送 finish-task 指令，结束语音合成任务"""
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
        print("📤 已通过代理发送 finish-task 指令")

    def close(self, ws):
        """主动关闭连接"""
        if ws and ws.sock and ws.sock.connected:
            ws.close()
            print("🔌 已主动关闭代理连接")

    def run(self):
        """启动 WebSocket 客户端"""
        # 设置请求头部（鉴权）- 使用代理密钥，代理服务会替换为真实API Key
        header = {
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-DataInspection": "enable"
        }

        # 创建 WebSocketApp 实例
        self.ws = websocket.WebSocketApp(
            self.proxy_uri,
            header=header,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        print("🔗 正在连接 AIProxy 代理服务...")
        self.ws.run_forever()

    def run_test(self, timeout=30):
        """运行测试并等待结果"""
        print("=" * 80)
        print("🎤 CosyVoice WebSocket API 代理服务测试")
        print("=" * 80)
        
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
        print("📊 代理测试结果")
        print("=" * 80)
        
        if self.error_occurred:
            print(f"❌ 代理测试失败: {self.error_message}")
            return False
        elif self.task_finished:
            print("✅ WebSocket 代理连接成功")
            print(f"✅ 任务启动: {'成功' if self.task_started else '失败'}")
            print(f"✅ 音频接收: {'成功' if self.audio_received else '失败'}")
            print(f"✅ 任务完成: {'成功' if self.task_finished else '失败'}")
            
            if os.path.exists(self.output_file):
                file_size = os.path.getsize(self.output_file)
                print(f"📁 输出文件: {self.output_file} ({file_size} 字节)")
                if file_size > 0:
                    print("🎵 通过代理的音频文件生成成功！")
                    return True
                else:
                    print("⚠️ 音频文件为空")
                    return False
            else:
                print("❌ 未生成音频文件")
                return False
        else:
            print("⏰ 代理测试超时")
            return False

    def play_audio(self):
        """播放生成的音频文件"""
        if not os.path.exists(self.output_file):
            print("❌ 音频文件不存在")
            return False
            
        print(f"🎵 准备播放代理生成的音频文件: {self.output_file}")
        
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", self.output_file])
                print("✅ 代理音频播放完成")
            elif system == "Linux":
                # 尝试不同的Linux音频播放器
                players = ["mpg123", "mplayer", "vlc", "paplay"]
                for player in players:
                    try:
                        subprocess.run([player, self.output_file], check=True)
                        print("✅ 代理音频播放完成")
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                print("❌ 未找到可用的音频播放器")
                return False
            elif system == "Windows":
                os.startfile(self.output_file)
                print("✅ 已使用默认播放器打开代理音频文件")
            else:
                print(f"❌ 不支持的操作系统: {system}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ 播放代理音频时出错: {e}")
            return False


def test_cosyvoice_websocket_proxy():
    """通过AIProxy代理服务测试CosyVoice WebSocket API"""
    
    # 使用代理密钥（不是真实的DashScope API Key）
    proxy_key = "sk-bailian-tester-001"  # 使用配置文件中的代理密钥
    
    print(f"🔑 使用代理密钥: {proxy_key}")
    
    # 代理服务WebSocket地址 - 通过AIProxy代理
    # 使用配置文件中定义的WebSocket端点
    proxy_uri = "ws://localhost:8001/api-ws/v1/inference"
    
    print(f"🌐 通过AIProxy代理连接: {proxy_uri}")
    print("💡 代理服务将转发请求到: wss://dashscope.aliyuncs.com/api-ws/v1/inference/")
    
    # 创建客户端并运行测试
    client = CosyVoiceProxyTTSClient(proxy_key, proxy_uri)
    
    try:
        success = client.run_test(timeout=60)
        
        if success:
            print("\n🎉 CosyVoice WebSocket API 代理测试成功！")
            print("💡 AIProxy代理服务正常工作，成功转发语音合成请求")
            
            # 播放音频文件
            print("\n🎵 准备播放代理生成的音频...")
            client.play_audio()
            
            print(f"\n📁 代理音频文件已保存: {client.output_file}")
            print("💾 文件已保留，您可以手动播放或分享")
            
        else:
            print("\n❌ CosyVoice WebSocket API 代理测试失败")
            print("💡 可能的原因:")
            print("   1. AIProxy代理服务未启动")
            print("   2. WebSocket代理配置不正确")
            print("   3. 代理服务无法连接到DashScope API")
            
        return success
        
    except Exception as e:
        print(f"❌ 代理测试异常: {e}")
        return False


def check_proxy_service():
    """检查AIProxy代理服务状态"""
    print("🔍 检查AIProxy代理服务状态...")
    
    try:
        import requests
        # 检查HTTP代理服务状态
        response = requests.get("http://localhost:8001/stats", timeout=5)
        if response.status_code == 200:
            print("✅ AIProxy HTTP服务正在运行")
            print(f"📊 服务状态: {response.text[:100]}...")
            return True
        else:
            print(f"⚠️ AIProxy HTTP服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ AIProxy服务未启动或无法连接")
        print("💡 请先启动AIProxy服务: ./start.sh")
        return False
    except Exception as e:
        print(f"❌ 检查代理服务时出错: {e}")
        return False


if __name__ == "__main__":
    # 检查websocket-client依赖
    try:
        import websocket
        print("✅ websocket-client 已安装")
    except ImportError:
        print("❌ 缺少依赖: websocket-client")
        print("请安装: pip install websocket-client")
        exit(1)
    
    # 检查代理服务状态
    if not check_proxy_service():
        print("\n⚠️ 代理服务检查失败，但仍将尝试WebSocket连接...")
        print("💡 如果测试失败，请确保AIProxy服务正在运行")
    
    # 运行代理测试
    test_cosyvoice_websocket_proxy() 