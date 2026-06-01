def code_review(api_key, code_snippet, language="Python"):
    """使用API进行代码审查"""
    import dashscope
    from dashscope import Generation

    dashscope.api_key = api_key

    prompt = f"""
你是一位经验丰富的{language}开发工程师，请审查以下代码：

代码：
{code_snippet}

请从以下角度进行分析：
1. 代码质量和规范性
2. 潜在的bug和安全问题  
3. 性能优化建议
4. 最佳实践建议
5. 改进后的代码示例

输出格式：使用markdown格式，包含代码块
"""

    response = Generation.call(
        model="qwen-plus",
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.2
    )

    if response.status_code == 200:
        return response.output.text
    else:
        return f"审查失败：{response.message}"


# 使用示例
code_to_review = """
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return db.execute(query)
"""

review_result = code_review("sk-57cbe6ae462f4b698eeab5ce4337ef9b", code_to_review)
print(review_result)