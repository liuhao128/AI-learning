import requests
import json


class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def chat(self, model, message, stream=False):
        """调用本地模型进行对话

        重要：如果一个函数体里出现了 yield，那么这个函数会变成“生成器函数”。
        为了保证：
        - stream=False 时返回字符串（模型完整结果）
        - stream=True 时返回迭代器（逐段产出）
        我们把 yield 放到内部生成器函数里。
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": message,
            "stream": stream
        }

        # 1) 流式：返回一个“内部生成器”，外部 for chunk in client.chat(..., stream=True)
        if stream:
            def _gen():
                try:
                    # 注意：requests 需要 stream=True 才能边下边读
                    response = requests.post(url, json=payload, stream=True)
                    response.raise_for_status()

                    for line in response.iter_lines():
                        if not line:
                            continue
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        if chunk:
                            yield chunk

                        # Ollama 会在最后一条返回 done=true
                        if data.get("done") is True:
                            break
                except Exception as e:
                    yield f"调用失败：{str(e)}"

            return _gen()

        # 2) 非流式：直接返回字符串
        try:
            response = requests.post(url, json=payload, stream=False)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            return f"调用失败：{str(e)}"


# 使用示例
if __name__ == "__main__":
    client = OllamaClient()

    # 非流式（返回字符串）
    # response = client.chat("qwen3:8b", "什么是Python？", stream=False)
    # print("通义千问回答：", response)

    # 流式（返回迭代器）
    for chunk in client.chat("qwen3:8b", "写一个Python Hello World", stream=True):
        print(chunk, end="", flush=True)