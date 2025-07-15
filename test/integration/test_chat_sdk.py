#!/usr/bin/env python3
"""
OpenAI API和DashScope SDK聊天完成测试
基于unittest框架的标准化测试
"""

import os
import unittest
import json
import time
from openai import OpenAI
import dashscope
from dashscope.audio.tts_v2 import *


class TestChatSDK(unittest.TestCase):
    """OpenAI API和DashScope SDK聊天完成测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 测试配置
        self.base_url = "https://aiproxy.bwton.cn"
        self.proxy_key_001 = "sk-bailian-tester-001"
        self.proxy_key_003 = "sk-bailian-tester-003"
        
        # 测试参数
        self.test_prompt = "你的模型名称是什么，能做什么？"
        self.test_system_message = "You are a helpful assistant."
        
        # 生成的文件列表，用于清理
        self.generated_files = []
        
        print(f"设置测试环境 - Base URL: {self.base_url}")
        
    def _create_openai_client(self, api_key):
        """创建OpenAI客户端的辅助方法"""
        return OpenAI(
            api_key=api_key,
            base_url=self.base_url
        )
        
    def test_basic_chat_completions(self):
        """测试基础聊天完成功能"""
        print("正在测试基础聊天完成...")
        
        client = self._create_openai_client(self.proxy_key_003)
        model_name = "gemini-2.0-flash"
        
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": self.test_system_message},
                    {"role": "user", "content": self.test_prompt}
                ]
            )
            
            # 验证响应结构
            self.assertIsNotNone(completion, "响应不应为空")
            self.assertIsNotNone(completion.choices, "响应应包含choices字段")
            self.assertGreater(len(completion.choices), 0, "choices应至少包含一个选项")
            
            # 验证响应内容
            first_choice = completion.choices[0]
            self.assertIsNotNone(first_choice.message, "选择应包含message字段")
            self.assertIsNotNone(first_choice.message.content, "消息应包含content字段")
            
            content = first_choice.message.content
            self.assertIsInstance(content, str, "响应内容应为字符串")
            self.assertGreater(len(content.strip()), 0, "响应内容不应为空")
            
            print(f"✅ 基础聊天完成测试成功 - 模型: {model_name}")
            print(f"📝 响应内容: {content[:100]}...")
            
            # 验证JSON序列化
            json_response = completion.model_dump_json()
            self.assertIsInstance(json_response, str, "响应应能序列化为JSON")
            
            return json_response
            
        except Exception as e:
            self.fail(f"基础聊天完成测试失败: {str(e)}")
            
    def test_stream_chat_completions(self):
        """测试流式聊天完成功能"""
        print("正在测试流式聊天完成...")
        
        client = self._create_openai_client(self.proxy_key_001)
        model_name = "qwen-plus"
        
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": self.test_system_message},
                    {"role": "user", "content": self.test_prompt}
                ],
                stream=True
            )
            
            # 收集流式响应
            full_content = ""
            chunk_count = 0
            
            print("流式输出内容:")
            for chunk in completion:
                chunk_count += 1
                
                # 验证chunk结构
                self.assertIsNotNone(chunk, "chunk不应为空")
                self.assertIsNotNone(chunk.choices, "chunk应包含choices字段")
                
                if chunk.choices and chunk.choices[0].delta.content:
                    delta_content = chunk.choices[0].delta.content
                    full_content += delta_content
                    print(delta_content, end='', flush=True)
            
            print()  # 换行
            
            # 验证流式响应结果
            self.assertGreater(chunk_count, 0, "应至少收到一个chunk")
            self.assertIsInstance(full_content, str, "完整内容应为字符串")
            self.assertGreater(len(full_content.strip()), 0, "完整内容不应为空")
            
            print(f"✅ 流式聊天完成测试成功 - 模型: {model_name}")
            print(f"📊 总chunk数: {chunk_count}")
            print(f"📝 完整内容: {full_content[:100]}...")
            
            return full_content
            
        except Exception as e:
            self.fail(f"流式聊天完成测试失败: {str(e)}")
            
    def test_cosyvoice_synthesis(self):
        """测试CosyVoice语音合成功能"""
        print("正在测试CosyVoice语音合成...")
        
        # 设置DashScope配置
        dashscope.api_key = self.proxy_key_001
        dashscope.base_url = self.base_url
        
        model = "cosyvoice-v1"
        voice = "longxiaochun" 
        test_text = self.test_prompt
        
        try:
            # 调用语音合成
            result = dashscope.SpeechSynthesizer.call(
                model=model,
                text=test_text,
                voice=voice,
                format='wav'
            )
            
            # 验证响应结构
            self.assertIsNotNone(result, "合成结果不应为空")
            
            # 检查结果的属性（不同版本的SDK可能有不同的属性）
            if hasattr(result, 'request_id'):
                print(f"Request ID: {result.request_id}")
            
            if hasattr(result, 'status_code'):
                print(f"Status Code: {result.status_code}")
                # 验证合成成功
                self.assertEqual(result.status_code, 200, "语音合成状态码应为200")
            
            # 验证输出数据存在（不同版本的SDK可能有不同的属性）
            audio_data = None
            if hasattr(result, 'output') and result.output:
                audio_data = result.output
            elif hasattr(result, 'audio') and result.audio:
                audio_data = result.audio
            elif hasattr(result, 'data') and result.data:
                audio_data = result.data
            
            self.assertIsNotNone(audio_data, "合成结果应包含音频数据")
            
            # 保存音频文件
            output_filename = f"unittest_cosyvoice_output_{int(time.time())}.wav"
            self.generated_files.append(output_filename)
            
            with open(output_filename, 'wb') as f:
                f.write(audio_data)
                
            # 验证文件生成
            self.assertTrue(os.path.exists(output_filename), "音频文件应该生成成功")
            self.assertGreater(os.path.getsize(output_filename), 0, "音频文件不应为空")
            
            print(f"✅ CosyVoice语音合成测试成功 - 模型: {model}")
            print(f"📁 音频文件已保存: {output_filename}")
            
            return True
            
        except Exception as e:
            self.fail(f"CosyVoice语音合成测试失败: {str(e)}")
            
    def test_multiple_model_compatibility(self):
        """测试多个模型的兼容性"""
        print("正在测试多个模型的兼容性...")
        
        test_cases = [
            {
                "name": "Qwen Plus",
                "model": "qwen-plus",
                "api_key": self.proxy_key_001
            },
            {
                "name": "Gemini 2.0 Flash",
                "model": "gemini-2.0-flash", 
                "api_key": self.proxy_key_003
            }
        ]
        
        for case in test_cases:
            with self.subTest(model=case["name"]):
                print(f"测试模型: {case['name']}")
                
                client = self._create_openai_client(case["api_key"])
                
                try:
                    completion = client.chat.completions.create(
                        model=case["model"],
                        messages=[
                            {"role": "user", "content": "请简短回答：你是什么模型？"}
                        ]
                    )
                    
                    self.assertIsNotNone(completion, f"{case['name']} - 响应不应为空")
                    self.assertGreater(len(completion.choices), 0, f"{case['name']} - 应有响应内容")
                    
                    content = completion.choices[0].message.content
                    self.assertIsNotNone(content, f"{case['name']} - 响应内容不应为空")
                    
                    print(f"✅ {case['name']} 测试通过")
                    print(f"📝 响应: {content[:50]}...")
                    
                except Exception as e:
                    self.fail(f"{case['name']} 测试失败: {str(e)}")
    
    def tearDown(self):
        """测试后的清理工作"""
        print("🧹 开始清理测试环境...")
        
        # 清理生成的音频文件
        for filename in self.generated_files:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    print(f"已清理文件: {filename}")
                except Exception as e:
                    print(f"清理文件失败 {filename}: {e}")
        
        # 清理DashScope配置
        dashscope.api_key = None
        dashscope.base_url = None
        
        print("🧹 测试清理完成")


if __name__ == "__main__":
    print("🚀 OpenAI API和DashScope SDK聊天完成测试启动")
    print("=" * 60)
    unittest.main(verbosity=2)