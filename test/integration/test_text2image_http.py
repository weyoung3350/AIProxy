#!/usr/bin/env python3
"""
通义万相文生图V2版HTTP API测试
基于官方文档：https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference
"""

import os
import sys
import time
import unittest
import requests
import json
from http import HTTPStatus


class Text2ImageHTTPClient:
    """封装的文生图HTTP调用客户端"""
    
    def __init__(self, api_key, base_url="https://dashscope.aliyuncs.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.create_task_url = f"{base_url}/api/v1/services/aigc/text2image/image-synthesis"
        self.query_task_url = f"{base_url}/api/v1/tasks"

    def create_task(self, prompt, model="wanx2.1-t2i-turbo"):
        """创建文生图任务"""
        print(f"正在创建文生图任务...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }
        
        data = {
            "model": model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "size": "1024*1024",
                "n": 1
            }
        }
        
        response = requests.post(
            self.create_task_url,
            headers=headers,
            json=data,
            timeout=30
        )
        
        return response

    def query_task(self, task_id):
        """查询任务状态和结果"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.get(
            f"{self.query_task_url}/{task_id}",
            headers=headers,
            timeout=30
        )
        
        return response

    def wait_for_task_completion(self, task_id, timeout=300):
        """等待任务完成"""
        print(f"等待任务完成，任务ID: {task_id}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.query_task(task_id)
                if response.status_code == 200:
                    result = response.json()
                    task_status = result.get("output", {}).get("task_status")
                    
                    print(f"任务状态: {task_status}")
                    
                    if task_status == "SUCCEEDED":
                        return result
                    elif task_status == "FAILED":
                        error_msg = result.get("output", {}).get("message", "任务失败")
                        raise Exception(f"任务失败: {error_msg}")
                    
                    # 继续等待
                    time.sleep(5)
                else:
                    print(f"查询任务失败: {response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"查询任务异常: {e}")
                time.sleep(5)
        
        raise Exception("任务超时")

    def generate_image(self, prompt, model="wanx2.1-t2i-turbo"):
        """完整的图片生成流程"""
        # 创建任务
        create_response = self.create_task(prompt, model)
        
        if create_response.status_code != 200:
            raise Exception(f"创建任务失败: {create_response.status_code}, {create_response.text}")
        
        create_result = create_response.json()
        task_id = create_result.get("output", {}).get("task_id")
        
        if not task_id:
            raise Exception("未获取到任务ID")
        
        print(f"任务创建成功，任务ID: {task_id}")
        
        # 等待任务完成
        result = self.wait_for_task_completion(task_id)
        
        return {
            'task_id': task_id,
            'result': result,
            'images': result.get("output", {}).get("results", [])
        }


class TestText2ImageHTTP(unittest.TestCase):
    """通义万相文生图V2版HTTP API测试类"""

    def test_text2image_http_direct(self):
        """直接对接文生图HTTP API测试"""
        test_prompt = "一只可爱的小猫咪在花园里玩耍"
        
        print("设置官方直连环境变量...")
        
        # 从环境变量获取API Key
        api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not api_key:
            self.skipTest("未设置 DASHSCOPE_API_KEY 环境变量")
        
        print(f"使用API Key: {api_key[:10]}...")
        
        # 创建客户端实例
        try:
            client = Text2ImageHTTPClient(api_key, "https://dashscope.aliyuncs.com")
        except Exception as e:
            self.skipTest(f"配置错误: {e}")
        
        try:
            # 调用文生图
            result = client.generate_image(test_prompt)
            self.check_result_images(result)
            
        except Exception as e:
            print(f"测试异常: {e}")
            self.fail(f"直连测试失败: {e}")

    def test_text2image_http_proxy(self):
        """通过代理访问文生图HTTP API测试"""
        test_prompt = "深夜，码农在一杯浓美式的陪伴下做牛马"
        
        print("设置代理环境变量...")
        
        # 从环境变量获取API Key
        api_key = os.getenv("AIPROXY_API_KEY")
        
        if not api_key:
            self.skipTest("未设置 AIPROXY_API_KEY 环境变量")
        
        print(f"使用API Key: {api_key[:10]}...")
        
        # 创建客户端实例
        try:
            client = Text2ImageHTTPClient(api_key, "https://aiproxy.bwton.cn")
        except Exception as e:
            self.skipTest(f"配置错误: {e}")
        
        try:
            # 调用文生图
            result = client.generate_image(test_prompt)
            self.check_result_images(result)
            
        except Exception as e:
            print(f"测试异常: {e}")
            self.fail(f"代理测试失败: {e}")

    def check_result_images(self, result):
        """检查生成的图片结果"""
        # 检查返回结果
        if result['images'] and len(result['images']) > 0:
            print(f"图片生成成功")
            
            for i, image_info in enumerate(result['images']):
                image_url = image_info.get('url')
                if image_url:
                    print(f"图片 {i+1} URL: {image_url}")
                    
                    # 验证URL格式
                    self.assertTrue(image_url.startswith('https://'))
                    self.assertTrue('oss' in image_url)
                    
                    print(f"原始提示词: {image_info.get('orig_prompt', 'N/A')}")
                    print(f"实际提示词: {image_info.get('actual_prompt', 'N/A')}")
                else:
                    print(f"图片 {i+1} 未获取到URL")
            
            print(f"任务ID: {result['task_id']}")
            print(f"HTTP文生图测试成功！")
        else:
            print("未收到图片数据")
            self.fail("未生成图片")

    def tearDown(self):
        """测试后的清理工作"""
        pass


if __name__ == '__main__':
    print("通义万相文生图V2版HTTP API测试启动")
    print("=" * 60)
    unittest.main() 