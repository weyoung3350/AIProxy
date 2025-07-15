#!/usr/bin/env python3
"""
OpenAI API HTTP聊天完成测试
基于unittest框架的标准化测试
"""

import os
import unittest
import json
from openai import OpenAI


class TestChatHTTP(unittest.TestCase):
    """OpenAI API HTTP聊天完成测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 测试配置
        self.base_url = "http://10.10.5.176"
        self.api_key = os.getenv("AIPROXY_API_KEY")
        
        # 检查必要的环境变量
        if not self.api_key:
            self.skipTest("未设置AIPROXY_API_KEY环境变量")
            
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 测试参数
        self.test_model = "qwen-plus"
        self.test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你的模型名称是什么，能做什么？"}
        ]
        
    def test_chat_completions_success(self):
        """测试基础聊天完成功能"""
        print(f"正在测试聊天完成API - 模型: {self.test_model}")
        
        try:
            completion = self.client.chat.completions.create(
                model=self.test_model,
                messages=self.test_messages
            )
            
            # 验证响应结构
            self.assertIsNotNone(completion, "响应不应为空")
            self.assertIsNotNone(completion.choices, "响应应包含choices字段")
            self.assertGreater(len(completion.choices), 0, "choices应至少包含一个选项")
            
            # 验证第一个选择的内容
            first_choice = completion.choices[0]
            self.assertIsNotNone(first_choice.message, "选择应包含message字段")
            self.assertIsNotNone(first_choice.message.content, "消息应包含content字段")
            
            # 验证返回的内容不为空
            content = first_choice.message.content
            self.assertIsInstance(content, str, "响应内容应为字符串")
            self.assertGreater(len(content.strip()), 0, "响应内容不应为空")
            
            print(f"✅ 聊天完成测试成功")
            print(f"📝 响应内容: {content[:100]}...")
            
            # 验证能够序列化为JSON
            json_response = completion.model_dump_json()
            self.assertIsInstance(json_response, str, "响应应能序列化为JSON")
            
            # 验证JSON可以解析
            parsed_response = json.loads(json_response)
            self.assertIn("choices", parsed_response, "JSON响应应包含choices字段")
            
        except Exception as e:
            self.fail(f"聊天完成API调用失败: {str(e)}")
    
    def test_chat_completions_with_different_messages(self):
        """测试不同消息内容的聊天完成"""
        test_cases = [
            {
                "name": "简单问候",
                "messages": [{"role": "user", "content": "你好"}]
            },
            {
                "name": "技术问题",
                "messages": [{"role": "user", "content": "什么是人工智能？"}]
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["name"]):
                print(f"测试用例: {case['name']}")
                
                try:
                    completion = self.client.chat.completions.create(
                        model=self.test_model,
                        messages=case["messages"]
                    )
                    
                    self.assertIsNotNone(completion, f"{case['name']} - 响应不应为空")
                    self.assertGreater(len(completion.choices), 0, f"{case['name']} - 应有响应内容")
                    
                    content = completion.choices[0].message.content
                    self.assertIsNotNone(content, f"{case['name']} - 响应内容不应为空")
                    
                    print(f"✅ {case['name']} 测试通过")
                    
                except Exception as e:
                    self.fail(f"{case['name']} 测试失败: {str(e)}")
    
    def tearDown(self):
        """测试后的清理工作"""
        # 清理客户端资源
        self.client = None
        print("🧹 测试清理完成")


if __name__ == "__main__":
    print("🚀 OpenAI API HTTP聊天完成测试启动")
    print("=" * 60)
    unittest.main(verbosity=2)