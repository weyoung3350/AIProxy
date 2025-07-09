import os
from openai import OpenAI

base_url="http://localhost:8001"

# 基础聊天完成测试
def test_chat_completions(ProxyKey, modelName, userPrompt):
    client = OpenAI(
        api_key=ProxyKey,
        base_url=base_url,
    )
    try:
        completion = client.chat.completions.create(
            model=modelName,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": userPrompt},
            ],
        )
        print("响应内容：", completion.model_dump_json())   
        return completion.model_dump_json()
    except Exception as e:
        print("API调用失败：", e)


def test_chat_completions_gemini():
    ProxyKey = "sk-bailian-tester-003"
    modelName = "gemini-2.0-flash"
    userPrompt = "你的模型名称是什么，能做什么？"
    result = test_chat_completions(ProxyKey, modelName, userPrompt)
    

def test_all():
    test_chat_completions_gemini()

if __name__ == "__main__":
    test_all()