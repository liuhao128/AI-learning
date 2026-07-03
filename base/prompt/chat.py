from itertools import chain

from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate

chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "假设你是一个{expert}专家"),
    ("human", "什么是{user_input}")
])
# prompt = chat_prompt_template.format(expert="AI", user_input="Langgraph")
# print(type(prompt)) # <class 'str'>
# print(prompt) # System: 假设你是一个AI专家 Human: 什么是Langgraph
#
# prompt = chat_prompt_template.invoke(input={"expert": "AI", "user_input": "Langgraph"}).to_string()
# print(type(prompt)) # <class 'str'>
# print(prompt) # System: 假设你是一个AI专家 Human: 什么是Langgraph

llm = ChatTongyi(model="qwen3.7-max",   streaming=True)
chain = chat_prompt_template | llm
result = chain.stream(input={"expert": "AI", "user_input": "Langgraph"})
for chunk in result:
    print(chunk.content, end='', flush=True)