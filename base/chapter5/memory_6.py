# 摘要 + 滑动窗口（生产最常用） —— LangChain 1.x 写法
# 目的：直观演示 "对话变长 → 自动摘要老的 + 保留最近原文" 的过程
import os
import warnings
from langchain_classic.memory import ConversationSummaryBufferMemory
from langchain_community.chat_models import ChatTongyi

warnings.filterwarnings("ignore")   # 屏蔽 Deprecation / Tokenizer 警告，让输出更干净

# ============ 0. 准备模型 ============
# 需提前设置环境变量 DASHSCOPE_API_KEY
llm = ChatTongyi(model_name="qwen-turbo")

# max_token_limit 故意调小到 80，方便快速看到 "摘要触发" 的效果
memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=80,
    return_messages=True,
)

def show(step: str):
    """打印当前 memory 内部状态，让学员一眼看清结构"""
    print(f"\n========== {step} ==========")
    vars = memory.load_memory_variables({})
    msgs = vars["history"]
    # moving_summary_buffer 是 LangChain 内部存"已压缩的摘要文本"的字段
    summary = getattr(memory, "moving_summary_buffer", "") or "(暂无摘要)"
    print(f"📝 当前摘要(summary)：{summary}")
    print(f"💬 缓冲区消息数：{len(msgs)} 条  （这些是没被压缩、原样保留的最近对话）")
    for i, m in enumerate(msgs, 1):
        role = m.__class__.__name__.replace("Message", "")
        content = m.content if len(m.content) <= 40 else m.content[:40] + "..."
        print(f"   [{i}] {role}: {content}")

# ============ 1. 初始状态 ============
show("Step 0：还没有任何对话")

# ============ 2. 逐轮喂入对话，观察 memory 怎么变 ============
rounds = [
    ("我叫小明，今年 28 岁。",        "你好小明！很高兴认识你。"),
    ("我是一名 Python 后端工程师。",   "Python 后端是个很棒的方向，有什么我能帮你的？"),
    ("我最近在学 LangChain 做 AI 应用。", "LangChain 是个不错的选择，它把 LLM 工程化做得很完善。"),
    ("我特别想搞懂 Memory 是怎么工作的。", "Memory 主要解决多轮对话上下文管理，常见有窗口、摘要、向量等策略。"),
    ("能给我讲个 ConversationSummaryBufferMemory 的例子吗？",
     "当然，它会在 token 超限时自动把老对话压成摘要，保留最近原文。"),
]

for i, (user_msg, ai_msg) in enumerate(rounds, 1):
    memory.save_context({"input": user_msg}, {"output": ai_msg})
    show(f"Step {i}：刚存入第 {i} 轮对话")

# ============ 3. 最终对比 ============
print("\n========== 🎯 最终结论 ==========")
print("👀 观察上面的输出你会发现：")
print("   • 前几轮：摘要为空，所有原文都在缓冲区。")
print("   • 当 token 超过 max_token_limit=80：早期对话被压成一段 summary，")
print("     缓冲区里只剩下最近 1~2 轮原文。")
print("   • 这就是 '摘要 + 滑动窗口' 的核心：老的省 token，新的保精度。")
