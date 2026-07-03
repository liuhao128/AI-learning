"""
生产级三层记忆系统 —— 基于 DashScope (通义千问)
L1 工作记忆 (内存/滑动窗口) + L2 会话记忆 (摘要) + L3 长期记忆 (结构化事实)
依赖: pip install dashscope
"""
import os
import json
import dashscope
from dashscope import Generation
from http import HTTPStatus

dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')


# ============================================================
# 工具函数：统一封装一次大模型调用
# ============================================================
def llm_call(messages, model='qwen-plus', temperature=0.7):
    """调用 DashScope，返回纯文本回复。失败时抛异常，方便上层感知。"""
    resp = Generation.call(
        model=model,
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        messages=messages,
        temperature=temperature,
        result_format='message',
    )
    if resp.status_code != HTTPStatus.OK:
        raise RuntimeError(f"模型调用失败: {resp.code} - {resp.message}")
    return resp.output.choices[0].message.content


# ============================================================
# L3 · 长期记忆：跨会话的用户画像（结构化事实）
# 真实项目存 DB / 向量库；这里用 JSON 文件模拟持久化
# ============================================================
class LongTermMemory:
    EXTRACT_PROMPT = """从下面的对话里抽取关于"用户"的长期事实（姓名、职业、城市、
偏好、忌口、目标等）。只输出 JSON，键用中文，没有就返回 {{}}，不要编造。

对话：
{conversation}

JSON："""

    def __init__(self, user_id: str, path='ltm.json'):
        self.user_id = user_id
        self.path = path
        self.profile = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, encoding='utf-8') as f:
                return json.load(f).get(self.user_id, {})
        return {}

    def _save(self):
        data = {}
        if os.path.exists(self.path):
            with open(self.path, encoding='utf-8') as f:
                data = json.load(f)
        data[self.user_id] = self.profile
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def extract_and_update(self, recent_dialog: list):
        """异步抽取（演示用同步）：从对话里提炼新事实，合并进画像"""
        conv = "\n".join(f"{m['role']}: {m['content']}" for m in recent_dialog)
        try:
            raw = llm_call(
                [{"role": "user", "content": self.EXTRACT_PROMPT.format(conversation=conv)}],
                model='qwen-turbo', temperature=0,
            )
            facts = json.loads(raw[raw.find('{'): raw.rfind('}') + 1])
            if facts:
                self.profile.update(facts)   # 新事实覆盖/补充旧画像
                self._save()
        except (json.JSONDecodeError, RuntimeError):
            pass  # 抽取失败不影响主流程，下轮再试

    def as_text(self):
        if not self.profile:
            return ""
        items = "；".join(f"{k}：{v}" for k, v in self.profile.items())
        return f"【已知用户画像】{items}"


# ============================================================
# L2 · 会话记忆：本次会话的摘要（溢出对话压缩）
# ============================================================
class SessionMemory:
    SUMMARY_PROMPT = """把下面对话压成一段事实陈述，保留人名/数字/偏好/决定，
去掉寒暄，用第三人称，100 字以内。\n\n对话：\n{conversation}\n\n摘要："""

    def __init__(self, summary=""):
        self.summary = summary

    def compress(self, overflow_msgs: list):
        conv = "\n".join(f"{m['role']}: {m['content']}" for m in overflow_msgs)
        new = llm_call(
            [{"role": "user", "content": self.SUMMARY_PROMPT.format(conversation=conv)}],
            model='qwen-turbo', temperature=0,
        )
        self.summary = f"{self.summary}\n{new}".strip() if self.summary else new


# ============================================================
# 记忆系统总装：把 L1 / L2 / L3 装配成一次完整请求
# ============================================================
class MemorySystem:
    def __init__(self, user_id, role_prompt, window=4, trigger=8):
        self.role_prompt = role_prompt
        self.window = window          # L1 保留最近几条
        self.trigger = trigger        # 累积多少条触发 L2 压缩
        self.l1 = []                  # L1 工作记忆（内存）
        self.l2 = SessionMemory()     # L2 会话摘要
        self.l3 = LongTermMemory(user_id)  # L3 长期画像

    def _build_messages(self):
        """核心：把三层记忆装配成发给大模型的 messages"""
        system = self.role_prompt
        ltm = self.l3.as_text()
        if ltm:
            system += f"\n\n{ltm}"                       # 注入 L3 长期画像
        if self.l2.summary:
            system += f"\n\n【历史摘要】{self.l2.summary}"  # 注入 L2 会话摘要
        return [{"role": "system", "content": system}] + self.l1  # 拼上 L1 原文

    def chat(self, user_input: str) -> str:
        # 1) 新消息进 L1
        self.l1.append({"role": "user", "content": user_input})
        # 2) 装配 messages 并调用大模型
        reply = llm_call(self._build_messages(), model='qwen-plus')
        self.l1.append({"role": "assistant", "content": reply})
        # 3) L1 溢出 → 压进 L2，同时抽取 L3 事实
        if len(self.l1) >= self.trigger:
            overflow = self.l1[:-self.window]
            self.l1 = self.l1[-self.window:]
            self.l2.compress(overflow)            # 沉淀为会话摘要
            self.l3.extract_and_update(overflow)  # 抽取长期事实
        return reply


# ==================== 使用示例 ====================
if __name__ == '__main__':
    bot = MemorySystem(
        user_id='user_007',
        role_prompt='你是用户的私人助理，回答简洁、贴心。',
        window=4, trigger=8,
    )
    for line in [
        "我叫小明，是 Python 后端工程师",
        "我对花生过敏，平时爱健身",
        "周末想找个地方放松一下",
        "帮我推荐个午餐吧",   # ← 此时系统已记住"花生过敏"，会主动避开
    ]:
        print(f"\n👤 {line}")
        print(f"🤖 {bot.chat(line)}")

    print("\n🗄️ 沉淀到长期记忆的画像：", bot.l3.profile)