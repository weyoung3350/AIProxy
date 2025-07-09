import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("AIPROXY_API_KEY"),
    base_url="http://localhost:8003", # 配置代理地址
)

# 基础聊天完成测试
def test_chat_completions():
    try:
        completion = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "你的模型名称是什么，能做什么？"},
            ],
        )
        print("响应内容：", completion.model_dump_json())   
    except Exception as e:
        print("API调用失败：", e)



if __name__ == "__main__":
    test_chat_completions()