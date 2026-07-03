from openai import OpenAI

# 1、创建客户端对象
client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 2、第一次调用模型 5c
completion = client.chat.completions.create(
    model="qwen3-max",
    messages=[
        {"role": "system", "content": "背景设定：你是AI学习助手，语气现在设定为可爱"},
        {"role": "user", "content": "你是谁"}
    ]
)
print(completion.choices[0].message.content)