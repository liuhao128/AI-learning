from openai import OpenAI

# 1、创建客户端对象
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 2、第一次调用模型 5c
completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "user", "content": "你好，我是阿浩，一个学习ai的学生"},
    ]
)

# 3、第二次调用模型 5c
completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "user", "content": "我是谁"},
    ]
)