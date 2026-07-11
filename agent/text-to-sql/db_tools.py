from langchain_community.chat_models import ChatTongyi
from langchain_core.tools import tool
from langchain.agents import create_agent
from typing import List, Dict, Any

# ========== 1. 导入 DBManager ==========
from db_manager import DBManager


# ========== 2. 创建数据库连接 ==========
db = DBManager(
    username="root",
    password="root",
    host="localhost",
    port=3306,
    database="test"
)


# ========== 3. 定义工具函数 ==========
@tool
def execute_sql_query(sql: str) -> str:
    """
    执行 SQL 查询语句并返回结果。
    参数 sql: 要执行的 SELECT 查询语句
    返回: 查询结果的文本描述
    """
    try:
        result = db.execute_query(sql)

        if not result:
            return "查询结果为空"

        # 格式化输出
        if len(result) == 1:
            return str(result[0])
        else:
            output = f"共查询到 {len(result)} 条记录：\n"
            for i, row in enumerate(result, 1):
                output += f"  {i}. {row}\n"
            return output.strip()

    except Exception as e:
        return f"查询失败: {str(e)}"


@tool
def get_table_schema() -> str:
    """
    获取当前数据库的所有表结构信息，包括表名、字段、类型、主键等。
    返回: 表结构的文本描述
    """
    try:
        schemas = db.get_all_table_schemas()

        if not schemas:
            return "数据库中没有表"

        output = "【数据库表结构】\n\n"
        for table_name, info in schemas.items():
            output += f"   表名: {table_name}\n"
            output += f"   注释: {info['comment']}\n"
            output += "   字段:\n"
            for col in info["columns"]:
                null_str = "可空" if col["nullable"] else "非空"
                output += f"     - {col['name']} ({col['type']}) {null_str}"
                if col['comment']:
                    output += f" 注释: {col['comment']}"
                output += "\n"

            if info["primary_keys"]:
                output += f"   主键: {', '.join(info['primary_keys'])}\n"

            if info["indexes"]:
                output += "   索引:\n"
                for idx in info["indexes"]:
                    unique_str = "唯一" if idx["unique"] else "普通"
                    output += f"     - {idx['name']} ({unique_str}): {', '.join(idx['columns'])}\n"
            output += "\n"

        return output.strip()

    except Exception as e:
        return f"获取表结构失败: {str(e)}"


@tool
def get_table_names() -> str:
    """
    获取数据库中所有表名列表。
    返回: 表名列表的文本描述
    """
    try:
        tables = db.get_table_names()
        if not tables:
            return "数据库中没有表"
        return f"数据库中的表有：{', '.join(tables)}"
    except Exception as e:
        return f"获取表名失败: {str(e)}"


# ========== 4. 创建 Agent ==========
agent = create_agent(
    model=ChatTongyi(model="qwen3-max"),
    tools=[get_table_names, get_table_schema, execute_sql_query],
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

# ========== 5. 测试 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("【Text To SQL 智能查询助手】")
    print("=" * 60)

    # 测试问题列表
    questions = [
        "数据库里有哪些表？",
        "销量排名前5的商品是哪些？",
        "电子产品类的商品有哪些？",
        "苹果手机一共卖了多少台？",
    ]

    for question in questions:
        print(f"\n用户: {question}")
        print("-" * 40)

        result = agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })

        # 提取最终回答
        final_message = result["messages"][-1]
        print(f"AI: {final_message.content}")
        print("-" * 60)

    # 关闭数据库连接
    db.close()