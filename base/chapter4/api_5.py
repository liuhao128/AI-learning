import dashscope
from dashscope import Generation


class DocumentAssistant:
    def __init__(self, api_key):
        dashscope.api_key = api_key

    def generate_documentation(self, code_content):
        """生成代码文档"""
        prompt = f"""
你是一位资深的技术文档专家，请为以下代码生成详细的文档：

代码：
{code_content}

请按以下格式输出：
1. 功能概述
2. 参数说明  
3. 返回值说明
4. 使用示例
5. 注意事项

要求：专业、准确、易懂
"""

        response = Generation.call(
            model="qwen-turbo",
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3
        )

        if response.status_code == 200:
            return response.output.text
        else:
            return f"生成失败：{response.message}"


# 使用示例
assistant = DocumentAssistant("sk-57cbe6ae462f4b698eeab5ce4337ef9b")
code = "def calculate_factorial(n): return 1 if n <= 1 else n * calculate_factorial(n-1)"
doc = assistant.generate_documentation(code)
print(doc)