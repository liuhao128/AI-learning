import os
from openai import OpenAI

# 1.创建客户端对象
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    # api_key=os.getenv("DASHSCOPE_API_KEY"),
    api_key="sk-ws-H.EMRXIDL.0sei.MEUCIQDmN903u_L2HB2boskv5XrOYp_acb74pvNAJWbQP24DwgIgfKbuFOmEnPCAADIWVanzRXYR5wd74St2Wur1yExXTnM",
    # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    base_url="https://ws-m71z8s6gl9pvodik.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
)

# 2.调用模型 5c
completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model = "qwen-plus",
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你的模型具体名字是qwen3.7-max吗"},
    ],
    stream=True,
)

# # 3.打印输出
# print(completion.model_dump_json())
# # 3.1.只打印内容
# print(completion.choices[0].message.content)

# 4.流示打印
for chunk in completion:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)  # end="" 避免换行，flush=True 强制立即输出