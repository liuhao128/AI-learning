
import ollama

client = ollama.Client(host="http://localhost:11434")

res = client.chat(
    model="qwen3:8b",
    messages=[{"role": "user", "content": "你好，简单介绍一下你自己"}],
    stream=False
)

print("\n===== AI 回复 =====\n")
print(res["message"]["content"])
