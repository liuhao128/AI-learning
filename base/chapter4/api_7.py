import dashscope
from dashscope import Generation


class XiaohongshuGenerator:
    def __init__(self, api_key):
        dashscope.api_key = api_key

    def generate_content(self, topic, style="种草"):
        """生成小红书文案"""
        prompt = f"""
你是一位专业的小红书博主，擅长写{style}风格的文案。请为主题"{topic}"创作一篇小红书文案。

要求：
1. 标题要吸引人，包含emoji表情
2. 正文要口语化，有亲和力
3. 包含3-5个相关话题标签
4. 字数控制在200-300字
5. 适当使用emoji增加趣味性
6. 结尾要有互动引导

格式示例：
✨ 标题 | emoji emoji

正文内容...

#话题1 #话题2 #话题3

姐妹们有什么想法吗？评论区见～
"""

        response = Generation.call(
            model="qwen-turbo",
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.8,
            max_tokens=500
        )

        if response.status_code == 200:
            return response.output.text
        else:
            return f"生成失败：{response.message}"

    def generate_batch(self, topics, count=3):
        """批量生成多个版本的文案"""
        results = []
        for topic in topics:
            for i in range(count):
                content = self.generate_content(topic)
                results.append({
                    "topic": topic,
                    "version": i + 1,
                    "content": content
                })
        return results


# 使用示例
generator = XiaohongshuGenerator("sk-57cbe6ae462f4b698eeab5ce4337ef9b")

# # 生成单个文案
# content = generator.generate_content("秋冬护肤心得", "种草")
# print(content)

# 批量生成
topics = ["健身减肥", "读书推荐", "职场技巧"]
batch_results = generator.generate_batch(topics, count=2)

for result in batch_results:
    print(f"\n=== {result['topic']} - 版本{result['version']} ===")
    print(result['content'])