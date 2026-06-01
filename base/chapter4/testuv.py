import os
import subprocess
import importlib.metadata
import time

UV = r"D:\Work\uv\uv.exe"
PY = r"D:/Work/code/python/AI-learing/.venv/Scripts/python.exe"


def run(cmd, timeout=60):
    print(f"\n▶ {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        print(result.stdout)
        if result.stderr:
            print("⚠️", result.stderr)
        return result
    except subprocess.TimeoutExpired:
        print("⏱️ 超时，跳过该步骤")
        return None


def step_check_env():
    print("\n🔍 Step 1 - 检查环境变量")
    for k in ["PIP_INDEX_URL", "UV_INDEX_URL"]:
        print(f"{k} = {os.environ.get(k)}")


def step_clean_cache():
    print("\n🧹 Step 2 - 清理缓存（非必须）")

    # ⚡ 改成非阻塞 + 短超时
    run(f'"{UV}" cache clean', timeout=10)


def step_uninstall():
    print("\n🗑 Step 3 - 卸载 ollama")
    run(f'"{UV}" pip uninstall ollama -y', timeout=30)


def step_install():
    print("\n📦 Step 4 - 安装最新 ollama SDK（强制 PyPI）")

    run(
        f'"{UV}" pip install ollama --index-url https://pypi.org/simple --no-cache',
        timeout=120
    )


def step_version():
    print("\n🔎 Step 5 - 检查版本")

    try:
        v = importlib.metadata.version("ollama")
        print("✔ ollama version =", v)

        if v.startswith("0.6"):
            print("⚠️ 仍然是旧版本（说明源没切成功）")
        else:
            print("✅ 版本正常")
    except Exception as e:
        print("❌ 获取版本失败:", e)


def step_test_chat():
    print("\n💬 Step 6 - 测试 chat API")

    code = """
import ollama

client = ollama.Client(host="http://localhost:11434")

res = client.chat(
    model="qwen3:8b",
    messages=[{"role": "user", "content": "你好，简单介绍一下你自己"}],
    stream=False
)

print("\\n===== AI 回复 =====\\n")
print(res["message"]["content"])
"""

    with open("test_chat.py", "w", encoding="utf-8") as f:
        f.write(code)

    run(f'"{UV}" run "{PY}" test_chat.py', timeout=60)


def main():
    print("🚀 Ollama SDK 快速修复开始")

    step_check_env()
    step_clean_cache()
    step_uninstall()
    step_install()
    step_version()
    step_test_chat()

    print("\n🎉 完成！")


if __name__ == "__main__":
    main()