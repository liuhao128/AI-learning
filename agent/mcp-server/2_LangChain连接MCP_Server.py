import asyncio

from langchain_community.chat_models import ChatTongyi
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


async def main():
    # 1. 创建客户端
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "stdio",
                "command": "/Users/liuhao/Documents/file/agent/code/AI-learning/.venv/bin/python",
                "args": [
                    "/Users/liuhao/Documents/file/agent/code/AI-learning/agent/mcp-server/weather.py"
                ]
            }
        }
    )

    # 2. 获取工具（使用 await）
    tools = await client.get_tools()

    # 3. 创建 agent
    agent = create_agent(
        model=ChatTongyi(model="qwen3-max"),
        tools=tools,
        system_prompt="你是一个助手，可以调用工具帮助用户解决问题"
    )

    # 4. 使用 agent
    result = await agent.ainvoke({"messages": [("user", "北京天气怎么样？")]})
    print(result)


if __name__ == "__main__":
    asyncio.run(main())