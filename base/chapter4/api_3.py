import dashscope
from dashscope import Generation
import os

# 从环境变量读取API Key（更安全）
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')


def chat_with_qwen(user_message):
    """与通义千问对话"""
    response = Generation.call(
        model='qwen-turbo',  # 使用turbo模型
        messages=[
            {'role': 'system', 'content': '你是一个helpful助手'},
            {'role': 'user', 'content': user_message}
        ],
        temperature=0.7,  # 平衡的创造性
        max_tokens=1000  # 最多生成1000个token
    )

    if response.status_code == 200:
        return response.output.text
    else:
        return f"错误：{response.message}"


# 使用示例
result = chat_with_qwen("用Python写一个冒泡排序算法")
print(result)