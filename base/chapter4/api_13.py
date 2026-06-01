from langchain_community.llms import Ollama

# 1) 本地 Ollama
llm = Ollama(model="qwen3:8b", base_url="http://localhost:11434")

# 2) 如果是远程 Ollama，把 base_url 改成远端地址即可
# llm = Ollama(model="qwen:7b", base_url="http://192.168.1.50:11434")

result = llm.invoke("用三点解释 top_p 和 temperature 的区别")
print(result)