import dashscope
from dashscope import Generation

# 设置API Key
dashscope.api_key = "sk-57cbe6ae462f4b698eeab5ce4337ef9b"

# 调用通义千问
responses = Generation.call(
    model='qwen-turbo',
    messages=[{'role': 'user', 'content': '讲个故事'}],
    stream=True
)

for response in responses:
    if response.output.text:
        print(response.output.text, end='')