from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate


# 1、聊天模板
chat_template = ChatPromptTemplate.from_messages([
    ("system",  "你是一个 experienced {language} 开发工程师"),
    ("human", "请告诉我关于{content}方面的知识")
])
# 2、创建客户端
llm = ChatTongyi(model="qwen3.7-max", streaming=True)
# 3、链式组装
chain = chat_template | llm
# 4、链式调用
output = chain.stream(input={"language": "Python", "content": "langchain"})
# 5、处理输出
for chunk in output:
    print(chunk.content, end='', flush=True)