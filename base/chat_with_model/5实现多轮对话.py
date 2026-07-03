from openai import OpenAI
from sympy import true
from torch.cpu import Stream


class MultiTurnChat:
    def __init__(self, base_url: str, model: str, system_prompt: str = None):
        self.client = OpenAI(base_url=base_url)
        self.model = model
        self.chat_history = []


        if system_prompt:
            self.chat_history.append({"role": "system", "content": system_prompt})


    def add_user_message(self, role: str, content: str):
        """添加消息到历史"""
        self.chat_history.append({"role": role, "content": content})


    def add_user_assistant_message(self, role: str, content: str):
        """添加消息到历史"""
        self.chat_history.append({"role": role, "content": content})


    def send(self, user_message: str) -> str:
        """发送消息"""
        # 1.添加用户消息到历史
        self.add_user_message("user", user_message)
        # 2.调用模型
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.chat_history
        )
        # 3.提取模型的回复
        assistant_message = completion.choices[0].message.content
        # 4.添加AI回复到历史
        self.add_user_assistant_message("assistant", assistant_message)

        return assistant_message


if __name__ == "__main__":
    # 创建多轮对话对象
    chat = MultiTurnChat(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen3-max",
        system_prompt="背景设定：你现在是一个AI老师，负责上AI课程。"
    )


    while true:
        user_message = input("请输入用户消息：")
        if user_message == "exit" or user_message == "quit":
            break
        if user_message == "":
            continue
        assistant_message = chat.send(user_message)
        print(assistant_message)

