import dashscope
from dashscope import Generation
import os

# 设置API Key
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')

class ChatWithMemory:
    """带记忆的聊天类"""

    def __init__(self, system_prompt=None):
        """初始化

        Args:
            system_prompt: 系统提示词，定义AI的角色和行为
        """
        self.messages = []

        print(f"初始化方法init====================")

        # 如果有系统提示词，添加到消息列表开头
        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt
            })

    def chat(self, user_input):
        """发送消息并获取回复"""
        # 添加用户消息
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        # 调用API
        response = Generation.call(
            model='qwen-turbo',
            messages=self.messages,
            result_format='message'
        )

        # 获取并保存AI回复
        assistant_message = response.output.choices[0].message.content
        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def get_history(self):
        """获取对话历史"""
        return self.messages

    def clear_history(self):
        """清空对话历史（保留system消息）"""
        system_messages = [msg for msg in self.messages if msg["role"] == "system"]
        self.messages = system_messages

    def get_message_count(self):
        """获取消息数量"""
        return len(self.messages)


# 使用示例
print("=== 创建一个Python助手 ===\n")

# 创建带系统提示词的聊天
assistant = ChatWithMemory(
    system_prompt="你是一个Python编程助手，擅长解答Python相关问题。"
)

# 多轮对话
print(f"AI: {assistant.chat('什么是列表？')}\n")
print(f"AI: {assistant.chat('它和元组有什么区别？')}\n")
print(f"AI: {assistant.chat('给我举个例子')}\n")

# 查看消息数量
print(f"当前消息数量：{assistant.get_message_count()}")