from openai import OpenAI


# 实现多轮对话
class MultiTurnChat:
    def __init__(self, base_url: str, model: str, system_prompt: str = None):
        self.client = OpenAI(base_url = base_url)
        self.model = model
        self.chat_history = []
        if system_prompt:
            self.chat_history.append({"role": "system", "content": system_prompt})

    def add_message(self, role: str ,message: str):
        self.chat_history.append({"role": role, "content": message})

    def send(self, message: str):
        self.add_message("user", message)
        stream = self.client.chat.completions.create(
            model = self.model,
            messages = self.chat_history,
            stream = True
        )
        # assistant_reply = completions.choices[0].message.content
        full_reply = ""
        # 1. 使用 for 循环直接遍历 stream，无需手动调用 next()
        for chunk in stream:
            # 2. 关键修复：检查 choices 列表是否为空
            if chunk.choices:
                # 3. 关键修复：检查 delta 和 content 是否存在
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    content = chunk.choices[0].delta.content
                    full_reply += content
                    yield content
        print()  # 换行
        self.add_message("assistant", full_reply)


if __name__ == "__main__":
    chat = MultiTurnChat(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model = "qwen3.7-max",
        system_prompt = "你是一个AI老师，请回答AI相关问题"
    )

    while True:
        user_input = input("请输出：")
        if user_input == "quit" or user_input == "exit":
            break
        if user_input == "":
            continue
        content = chat.send(user_input)
        for chunk in content:
            print(chunk, end="", flush=True)



