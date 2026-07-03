#!/usr/bin/env python3
"""AI猜数字游戏 - 展示对话记忆的重要性"""

import os
from dashscope import Generation
from http import HTTPStatus

# 游戏Prompt
GAME_PROMPT = """你是一个猜数字游戏的主持人。

游戏规则：
1. 你在心里想一个1-100之间的整数（不要告诉我）
2. 我会猜测数字
3. 你告诉我：太大了、太小了、或猜对了
4. 记录我猜了几次

要求：态度友好、使用emoji、每次给出明确提示"""


def chat_with_ai(messages):
    """调用AI - 核心函数"""
    response = Generation.call(
        model='qwen-plus',
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        messages=messages,
        temperature=0.8,
        result_format='message'
    )

    if response.status_code == HTTPStatus.OK:
        return response.output.choices[0].message.content
    return "错误"


def play_game():
    """开始游戏"""
    print("🎮 AI猜数字游戏\n")

    # 【核心】创建消息历史列表
    messages = [
        {'role': 'system', 'content': GAME_PROMPT}
    ]

    # AI开场白
    ai_msg = chat_with_ai(messages)
    print(f"🤖 AI: {ai_msg}\n")
    messages.append({'role': 'assistant', 'content': ai_msg})

    # 游戏循环
    while True:
        guess = input("👤 你的猜测: ").strip()
        if not guess:
            continue

        # 【核心】添加用户消息到历史
        messages.append({'role': 'user', 'content': guess})

        # 【核心】发送完整历史给AI
        ai_msg = chat_with_ai(messages)
        print(f"🤖 AI: {ai_msg}\n")

        # 【核心】保存AI回复到历史
        messages.append({'role': 'assistant', 'content': ai_msg})

        # 检查是否猜对
        if '恭喜' in ai_msg or '猜对' in ai_msg:
            break

    print("👋 游戏结束！")


if __name__ == "__main__":
    play_game()