class SlidingWindowMemory:
    """滑动窗口记忆：只保留最近 N 轮对话"""

    def __init__(self, system_prompt: str = "", window_size: int = 6):
        """
        window_size: 保留多少条 user/assistant 消息（system 不计入）
        建议偶数 → 保证完整对话对
        """
        self.system_msg = (
            [{"role": "system", "content": system_prompt}] if system_prompt else []
        )
        self.history = []          # 只放 user / assistant
        self.window_size = window_size

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # 关键：只裁 history，不动 system_msg
        if len(self.history) > self.window_size:
            self.history = self.history[-self.window_size:]

    def to_messages(self):
        """组装成 API 需要的格式"""
        return self.system_msg + self.history

    def dump(self, tag: str = ""):
        """调试用：打印当前窗口状态，一眼看到谁被踢出去了"""
        print(f"\n──── {tag} ────")
        print(f"📦 当前 messages 数组（共 {len(self.to_messages())} 条，将发给 API）:")
        for i, m in enumerate(self.to_messages()):
            icon = {"system": "⚙️", "user": "👤", "assistant": "🤖"}[m["role"]]
            print(f"  [{i}] {icon} {m['role']:9s} | {m['content']}")


# 使用示例
memory = SlidingWindowMemory(
    system_prompt="你是 Python 老师",
    window_size=4  # 窗口大小 = 4，只留最近 2 轮（4 条）
)

memory.add("user", "什么是装饰器？")
memory.add("assistant", "装饰器是修改函数行为的语法糖")
memory.dump("第 1 轮后")

memory.add("user", "举个例子")
memory.add("assistant", "比如 @timer 给函数计时")
memory.dump("第 2 轮后（窗口刚好满）")

memory.add("user", "再深入讲讲")          # ⚠️ 第 1 轮即将被挤出
memory.add("assistant", "装饰器本质是高阶函数")
memory.dump("第 3 轮后（老对话被挤出！）")


# ============== 输出 ==============
# ──── 第 1 轮后 ────
# 📦 当前 messages 数组（共 3 条，将发给 API）:
#   [0] ⚙️ system    | 你是 Python 老师
#   [1] 👤 user      | 什么是装饰器？
#   [2] 🤖 assistant | 装饰器是修改函数行为的语法糖
#
# ──── 第 2 轮后（窗口刚好满） ────
# 📦 当前 messages 数组（共 5 条，将发给 API）:
#   [0] ⚙️ system    | 你是 Python 老师
#   [1] 👤 user      | 什么是装饰器？
#   [2] 🤖 assistant | 装饰器是修改函数行为的语法糖
#   [3] 👤 user      | 举个例子
#   [4] 🤖 assistant | 比如 @timer 给函数计时
#
# ──── 第 3 轮后（老对话被挤出！） ────
# 📦 当前 messages 数组（共 5 条，将发给 API）:
#   [0] ⚙️ system    | 你是 Python 老师
#   [1] 👤 user      | 举个例子                   ← 原 [3] 变 [1]
#   [2] 🤖 assistant | 比如 @timer 给函数计时       ← 原 [4] 变 [2]
#   [3] 👤 user      | 再深入讲讲                 ← 本轮新增
#   [4] 🤖 assistant | 装饰器本质是高阶函数         ← 本轮新增
#
# 👀 看到了吗？「什么是装饰器？」和「语法糖」这两条已经从数组里彻底消失，
#    下次 API 调用不会再发送它们 —— 这就是"滑动"。