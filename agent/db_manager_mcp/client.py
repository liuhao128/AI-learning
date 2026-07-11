import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_agent


async def main():
    # 1. 创建客户端，连接 MCP Server
    client = MultiServerMCPClient(
        {
            "database": {
                "transport": "stdio",
                "command": "python",
                "args": [
                    "mcp_db_server.py"  # 请修改为实际文件路径
                ]
            }
        }
    )

    # 2. 获取工具（使用 await）
    tools = await client.get_tools()

    print("=" * 60)
    print("【已加载的 MCP 工具】")
    print("=" * 60)
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print("=" * 60)

    # 3. 创建 Agent
    agent = create_agent(
        model=ChatTongyi(model="qwen3-max"),
        tools=tools,
        system_prompt="""
你是一个专业的 SQL 查询助手。你的职责是根据用户的自然语言问题，生成准确的 SQL 查询语句并执行。

【工作流程】
1. 如果用户问的是"有哪些表"，直接调用 get_table_names
2. 如果需要了解表结构，调用 get_table_schema
3. 根据表结构生成正确的 SQL 查询语句
4. 调用 execute_sql_query 执行查询
5. 根据查询结果用中文回答用户

【重要规则】
- 只能使用 SELECT 查询，不能修改数据
- 生成 SQL 前必须先了解表结构
- 涉及多个表时使用 JOIN 关联
- 始终用中文回答用户
"""
    )

    # 4. 测试问题
    questions = [
        "数据库里有哪些表？",
        "销量排名前5的商品是哪些？",
        "电子产品类的商品有哪些？",
        "苹果手机一共卖了多少台？",
    ]

    print("\n" + "=" * 60)
    print("【Text To SQL 智能查询助手 - MCP 版本】")
    print("=" * 60)

    for question in questions:
        print(f"\n用户: {question}")
        print("-" * 40)

        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": question}]
        })

        # 提取最终回答
        final_message = result["messages"][-1]
        print(f"AI: {final_message.content}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())