import requests

r = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:8b",
        "prompt": "你好",
        "stream": True
    },
    stream=True
)

print(r.status_code)
print(r.text)


