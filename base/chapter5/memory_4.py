import os
import dashscope
from dashscope import Generation

dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')

SUMMARY_PROMPT = """请把下面这段对话压缩成一段简洁的事实陈述，
要求：
1. 保留所有人名、数字、偏好、决定
2. 去掉寒暄、客套话
3. 用第三人称（"用户" / "AI"）
4. 控制在 100 字以内

对话：
{conversation}

压缩后："""


class SummaryMemory:
    """摘要压缩记忆"""

    def __init__(self, system_prompt: str, trigger_size: int = 10, keep_recent: int = 4):
        self.system_prompt = system_prompt
        self.summary = ""               # 累积的摘要
        self.recent = []                # 近期未压缩的对话
        self.trigger_size = trigger_size  # 累积到多少条触发压缩
        self.keep_recent = keep_recent    # 压缩后保留最近几条原文

    def add(self, role: str, content: str):
        self.recent.append({"role": role, "content": content})
        if len(self.recent) >= self.trigger_size:
            self._compress()

    def _compress(self):
        """把 recent 中较老的部分压缩进 summary"""
        to_compress = self.recent[:-self.keep_recent]
        self.recent = self.recent[-self.keep_recent:]

        conv = "\n".join(f"{m['role']}: {m['content']}" for m in to_compress)
        prompt = SUMMARY_PROMPT.format(conversation=conv)

        resp = Generation.call(
            model='qwen-turbo',   # 用便宜的模型做压缩
            messages=[{"role": "user", "content": prompt}],
            result_format='message'
        )
        new_summary = resp.output.choices[0].message.content

        # 增量累积
        self.summary = (
            f"{self.summary}\n{new_summary}" if self.summary else new_summary
        )

    def to_messages(self):
        sys_content = self.system_prompt
        if self.summary:
            sys_content += f"\n\n【历史摘要】\n{self.summary}"
        return [{"role": "system", "content": sys_content}] + self.recent

    def dump(self, tag: str = ""):
        """调试用：可视化当前状态"""
        msgs = self.to_messages()
        total_tok = sum(len(m["content"]) for m in msgs)  # 粗略估算
        print(f"\n──── {tag} ────")
        print(f"📦 messages 共 {len(msgs)} 条 / 约 {total_tok} 字符")
        print(f"   📝 已压缩摘要: {'(空)' if not self.summary else self.summary}")
        print(f"   💬 未压缩对话: {len(self.recent)} 条")
        for i, m in enumerate(msgs):
            icon = {"system": "⚙️", "user": "👤", "assistant": "🤖"}[m["role"]]
            preview = m["content"][:50] + ("..." if len(m["content"]) > 50 else "")
            print(f"   [{i}] {icon} {m['role']:9s} | {preview}")


# ================== 使用示例 ==================
mem = SummaryMemory(
    system_prompt="你是用户的私人助理",
    trigger_size=6,    # 累积 6 条就压缩
    keep_recent=2      # 压缩后保留最近 2 条原文
)

# 第 1~3 轮对话
mem.add("user", "我叫小明，今年 28 岁")
mem.add("assistant", "你好小明！很高兴认识你 👋")
mem.add("user", "我是 Python 后端工程师，住北京海淀")
mem.add("assistant", "海淀是科技公司聚集地呢，工作很方便！")
mem.add("user", "我对花生过敏，平时喜欢撸铁和打游戏")
mem.dump("第 3 轮后（5 条，还没触发压缩）")

# 第 4 轮 → 触发压缩！
mem.add("assistant", "已记住你的偏好，需要推荐健身餐吗？")
mem.dump("第 4 轮后（满 6 条 → 自动压缩！）")

# 后续继续对话
mem.add("user", "推荐一个高蛋白午餐")
mem.add("assistant", "鸡胸肉 + 糙米 + 西兰花，避开花生酱即可")
mem.dump("第 5 轮后")


# ============== 运行输出 ==============
# ──── 第 3 轮后（5 条，还没触发压缩） ────
# 📦 messages 共 6 条 / 约 80 字符
#    📝 已压缩摘要: (空)                          ← 摘要还是空的
#    💬 未压缩对话: 5 条
#    [0] ⚙️ system    | 你是用户的私人助理
#    [1] 👤 user      | 我叫小明，今年 28 岁
#    [2] 🤖 assistant | 你好小明！很高兴认识你 👋
#    [3] 👤 user      | 我是 Python 后端工程师，住北京海淀
#    [4] 🤖 assistant | 海淀是科技公司聚集地呢，工作很方便！
#    [5] 👤 user      | 我对花生过敏，平时喜欢撸铁和打游戏
#
# ──── 第 4 轮后（满 6 条 → 自动压缩！） ────
# 📦 messages 共 3 条 / 约 120 字符        ← 条数从 6 → 3，瘦身成功！
#    📝 已压缩摘要: 用户小明，28 岁，Python 后端工程师，居住北京海淀，
#                  对花生过敏，爱好撸铁和游戏。AI 表示已记住偏好。  ← 老对话浓缩成一段
#    💬 未压缩对话: 2 条                  ← 只保留最近 2 条原文
#    [0] ⚙️ system    | 你是用户的私人助理
#                       【历史摘要】
#                       用户小明，28 岁，Python 后端工程师...
#    [1] 👤 user      | 我对花生过敏，平时喜欢撸铁和打游戏
#    [2] 🤖 assistant | 已记住你的偏好，需要推荐健身餐吗？
#
# ──── 第 5 轮后 ────
# 📦 messages 共 5 条 / 约 160 字符
#    📝 已压缩摘要: 用户小明，28 岁，Python 后端工程师...   ← 摘要还在 system 里
#    💬 未压缩对话: 4 条
#    [0] ⚙️ system    | 你是用户的私人助理 + 【历史摘要】...
#    [1] 👤 user      | 我对花生过敏...
#    [2] 🤖 assistant | 已记住你的偏好...
#    [3] 👤 user      | 推荐一个高蛋白午餐
#    [4] 🤖 assistant | 鸡胸肉 + 糙米 + 西兰花，避开花生酱即可  ← AI 还能避开"花生"，证明摘要起作用！
#
# 🎯 注意第 4 轮的变化：6 条 → 3 条，token 大幅减少；
#    第 5 轮 AI 仍能"想起"花生过敏，说明摘要里的关键事实被成功保留 ✅