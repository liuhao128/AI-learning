import dashscope
from dashscope import Generation

# 设置API Key
dashscope.api_key = "sk-57cbe6ae462f4b698eeab5ce4337ef9b"

# 调用通义千问
response = Generation.call(
    model='qwen-turbo',  # 或 qwen-plus, qwen-max
    messages=[
        {'role': 'system', 'content': '你是一个helpful助手'},
        {'role': 'user', 'content': '什么是人工智能？'}
    ]
)

# 打印结果
print(response.output.text)