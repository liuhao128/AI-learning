from langchain_ollama import OllamaLLM

# 初始化模型
llm = OllamaLLM(
    model="qwen3:8b",
    base_url="http://localhost:11434"
)

# 流式输出
prompt = "用三点解释 top_p 和 temperature 的区别"

for chunk in llm.stream(prompt):
    print(chunk, end="", flush=True)



