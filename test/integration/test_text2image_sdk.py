#!/usr/bin/env python3
"""
通义万相文生图V2版SDK测试
基于官方DashScope Python SDK实现
官方文档：https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference
"""

import os
import sys
import time
import unittest
import threading
from http import HTTPStatus


class Text2ImageSDKClient:
    """封装的文生图SDK调用客户端"""
    
    def __init__(self, dashscope):
        self.dashscope = dashscope

    def generate_image(self, prompt, model="wanx2.1-t2i-turbo"):
        """图片生成"""
        print(f"正在调用文生图服务...")
        
        from dashscope import ImageSynthesis
        
        response = ImageSynthesis.call(
            model=model,
            prompt=prompt,
            n=1,
            size='1024*1024'
        )
        
        return response


class TestText2ImageSDK(unittest.TestCase):
    """通义万相文生图V2版SDK测试类"""
    # 要注意两个测试方法不能同时运行，不然其中一个会失败。

    @unittest.skip("跳过")
    def test_text2image_sdk_direct(self):
        """直接对接文生图SDK测试"""
        test_prompt = "一只可爱的小猫咪在花园里玩耍"
        
        print("设置官方直连环境变量...")
        os.environ["DASHSCOPE_HTTP_BASE_URL"] = "https://dashscope.aliyuncs.com/api/v1"
        
        import dashscope
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not dashscope.api_key:
            self.skipTest("未设置 DASHSCOPE_API_KEY 环境变量")
        
        print(f"HTTP Base URL: {os.environ.get('DASHSCOPE_HTTP_BASE_URL')}")
        print(f"使用API Key: {dashscope.api_key[:10]}...")

        # 创建客户端实例
        try:
            self.client = Text2ImageSDKClient(dashscope)
        except ValueError as e:
            self.skipTest(f"配置错误: {e}")
        
        try:
            # 调用文生图
            result = self.client.generate_image(test_prompt)
            self.check_result_images(result, "直连")

        except Exception as e:
            print(f"测试异常: {e}")
            self.fail(f"直连测试失败: {e}")

    def test_text2image_sdk_proxy(self):
        """通过代理访问文生图SDK测试"""
        test_prompt = "一座美丽的山峰在云海中若隐若现"
        
        print("设置代理环境变量...")
        os.environ["DASHSCOPE_HTTP_BASE_URL"] = "https://aiproxy.bwton.cn/api/v1"
        
        import dashscope
        dashscope.api_key = os.getenv("AIPROXY_API_KEY")
        
        if not dashscope.api_key:
            self.skipTest("未设置 AIPROXY_API_KEY 环境变量")
        
        print(f"HTTP Base URL: {os.environ.get('DASHSCOPE_HTTP_BASE_URL')}")
        print(f"使用API Key: {dashscope.api_key[:10]}...")

        # 创建客户端实例
        try:
            self.client = Text2ImageSDKClient(dashscope)
        except ValueError as e:
            self.skipTest(f"配置错误: {e}")
        
        try:
            # 调用文生图
            result = self.client.generate_image(test_prompt)
            self.check_result_images(result, "代理")

        except Exception as e:
            print(f"测试异常: {e}")
            self.fail(f"代理测试失败: {e}")

    def check_result_images(self, result, mode):
        """检查生成的图片结果"""
        # 检查返回结果
        if result.status_code == HTTPStatus.OK:
            print(f"图片生成成功")
            
            # 获取图片URL
            images = result.output.get('results', [])
            if images and len(images) > 0:
                for i, image_info in enumerate(images):
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
                
                print(f"请求ID: {result.request_id}")
                print(f"使用量: {result.usage}")
                print(f"{mode}SDK文生图测试成功！")
            else:
                print("未收到图片数据")
                self.fail("未生成图片")
        else:
            error_msg = result.message if hasattr(result, 'message') else "未知错误"
            print(f"图片生成失败: {error_msg}")
            self.fail(f"图片生成失败: {error_msg}")

    def tearDown(self):
        """测试后的清理工作"""
        pass


if __name__ == '__main__':
    print("通义万相文生图V2版SDK测试启动")
    print("=" * 60)
    unittest.main() 