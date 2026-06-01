import ollama

client = ollama.Client(host="http://localhost:11434")

res = client.chat(
    model="qwen3:8b",
    messages=[
        {"role": "user", "content": "你好，介绍一下你自己"}
    ],
    stream=False
)

print(res["message"]["content"])