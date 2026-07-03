from openai import OpenAI

# 1、创建客户端对象
client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

chat_history = []


# 3、第一次调用模型 5c
user_message1 = {"role": "user", "content": "你好，我是阿苑，一个AI老师"};
chat_history.append(user_message1)
completion = client.chat.completions.create(
    model="qwen3-max",
    messages=chat_history
)
print(f"第一次打印回复的内容：")
print(completion.choices[0].message.content)

# 追加AI回复到历史
chat_history.append({"role": "assistant", "content": completion.choices[0].message.content})

# 4、第二次调用模型 5c
# 追加第二次用户问题
user_message2 = {"role": "user", "content": "我是谁？"};
chat_history.append(user_message2)
completion = client.chat.completions.create(
    model="qwen3-max",
    messages=chat_history
)
print(f"第二次打印回复的内容：")
print(completion.choices[0].message.content)