import time
import dashscope
from dashscope import Generation


class RobustLLMClient:
    def __init__(self, api_key, max_retries=3):
        dashscope.api_key = api_key
        self.max_retries = max_retries

    def call_with_retry(self, messages, **kwargs):
        """
        带重试机制的API调用

        参数说明：
        - messages: 对话消息列表
        - **kwargs: 可变关键字参数，用于接收任意数量的额外参数
                   例如: model='qwen-turbo', temperature=0.7, max_tokens=1000
                   这些参数会被原封不动地传递给 Generation.call()

        **kwargs 的作用：
        1. 让函数更灵活，可以接收任意额外参数
        2. 使用 **kwargs 展开时，会将字典形式的参数转换为关键字参数
        3. 例如: call_with_retry(messages, model='qwen-turbo', temperature=0.7)
           这里的 model 和 temperature 就会被 **kwargs 捕获并传递
        """
        for attempt in range(self.max_retries):
            try:
                # **kwargs 在这里展开，将接收到的所有额外参数传递给 Generation.call()
                response = Generation.call(
                    messages=messages,
                    **kwargs  # 例如会展开为: model='qwen-turbo', temperature=0.7
                )
                if response.status_code == 200:
                    return response.output.text
                else:
                    raise Exception(f"API错误：{response.message}")

            except Exception as e:
                if attempt == self.max_retries - 1:
                    return f"调用失败：{str(e)}"

                # 指数退避策略
                wait_time = 2 ** attempt
                print(f"第{attempt + 1}次失败，{wait_time}秒后重试...")
                time.sleep(wait_time)

        return "所有重试均失败"


# 使用示例
client = RobustLLMClient(api_key="sk-57cbe6ae462f4b698eeab5ce4337ef9b")

# # 示例1：只传递 model 参数（通过 **kwargs 传递）
# result = client.call_with_retry([
#     {'role': 'user', 'content': '介绍一下Python'}
# ], model='qwen-turbo')
# print(result)

# 示例2：传递多个参数（都会被 **kwargs 捕获并传递给 Generation.call）
result = client.call_with_retry([
    {'role': 'user', 'content': '写一首诗'}
], model='qwen-turbo', temperature=0.9, max_tokens=500)
# 这里的 model, temperature, max_tokens 都会被 **kwargs 接收
# 然后在函数内部通过 **kwargs 展开传递给 Generation.call()

print(result)