import os
from openai import OpenAI
import dashscope
from dashscope.audio.tts_v2 import *

base_url="http://localhost:8001"

# 基础聊天完成测试
def chat_completions(ProxyKey, modelName, userPrompt):
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


def chunk_completions(ProxyKey, modelName, userPrompt):
    client = OpenAI(
        api_key=ProxyKey,
        base_url=base_url,
    )
    try:
        completion = client.chat.completions.create(
            model=modelName,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": userPrompt}
            ],
            stream=True,
        )
        full_content = ""
        print("流式输出内容为：")
        for chunk in completion:
            if chunk.choices:
                full_content += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content)
        print(f"完整内容为：{full_content}")
        return full_content
    except Exception as e:
        print("API调用失败：", e)


def test_chat_completions():
    userPrompt = "你的模型名称是什么，能做什么？"
    result = chat_completions("sk-bailian-tester-003", "gemini-2.0-flash", userPrompt)
    
def test_chunk_completions():
    ProxyKey = "sk-bailian-tester-001"
    modelName = "qwen-plus"
    userPrompt = "你的模型名称是什么，能做什么？"
    result = chunk_completions(ProxyKey, modelName, userPrompt)

def test_cosyVoice():
    ProxyKey = "sk-bailian-tester-001"
    model = "cosyvoice-v1"
    voice = "longxiaochun"
    userPrompt = "你的模型名称是什么，能做什么？"
    
    # 设置API Key和base_url
    dashscope.api_key = ProxyKey
    dashscope.base_url = base_url
    
    try:
        # 使用dashscope顶层API调用
        result = dashscope.SpeechSynthesizer.call(
            model=model, 
            text=userPrompt, 
            voice=voice,  # voice作为kwargs参数
            format='wav'  # 指定输出格式
        )
        
        print('requestId: ', result.request_id)
        print('status_code: ', result.status_code)
        
        # 检查结果状态
        if result.status_code == 200 and result.output:
            with open('output.wav', 'wb') as f:
                f.write(result.output)
            print("语音合成成功，已保存到 output.wav")
            return True
        else:
            print("语音合成失败：status_code =", result.status_code)
            if hasattr(result, 'message'):
                print("错误信息：", result.message)
            return False
            
    except Exception as e:
        print("语音合成调用出错：", str(e))
        return False

def test_all():
    #test_chat_completions()
    #test_chunk_completions()
    test_cosyVoice()

if __name__ == "__main__":
    test_all()