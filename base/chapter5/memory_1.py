import dashscope
from dashscope import Generation
import os

# 设置API Key
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')

# 创建消息历史列表
messages = []


def chat(user_input):
    """带记忆的聊天函数"""
    # 1. 添加用户消息到历史
    messages.append({
        "role": "user",
        "content": user_input
    })

    # 2. 调用API，发送完整历史
    response = Generation.call(
        model='qwen-turbo',
        messages=messages,  # 发送所有历史消息
        result_format='message'
    )

    # 3. 获取AI回复
    assistant_message = response.output.choices[0].message.content

    # 4. 添加AI回复到历史
    messages.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message


# 使用示例
print("=== 带记忆的对话 ===\n")

# 第1轮对话
response1 = chat("我叫小明，今年25岁，喜欢编程")
print(f"AI: {response1}\n")

# 第2轮对话
response2 = chat("我叫什么名字？")
print(f"AI: {response2}\n")

# 第3轮对话
response3 = chat("我今年多大？")
print(f"AI: {response3}\n")

# 第4轮对话
response4 = chat("我的爱好是什么？")
print(f"AI: {response4}\n")

# 查看完整的消息历史
print("=== 消息历史 ===")
for i, msg in enumerate(messages, 1):
    role = "用户" if msg["role"] == "user" else "AI"
    print(f"{i}. {role}: {msg['content']}")