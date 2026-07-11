from mcp.server.fastmcp import FastMCP
from db_manager import DBManager
import json

# ========== 1. 创建 MCP Server 对象 ==========
mcp = FastMCP("database")

# ========== 2. 创建数据库连接实例 ==========
# 这里可以改为从配置文件读取
db = DBManager(
    username="root",
    password="root",
    host="localhost",
    port=3306,
    database="test"
)


# ========== 3. 定义 MCP 工具函数 ==========
@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


# ========== 4. 可选：添加清理资源的工具 ==========
@mcp.tool()
def close_database_connection() -> str:
    """
    关闭数据库连接池，释放资源。
    返回: 关闭状态的描述
    """
    try:
        db.close()
        return "数据库连接已关闭"
    except Exception as e:
        return f"关闭数据库连接失败: {str(e)}"

# ========== 定义 Prompts ==========

@mcp.prompt()
def sql_assistant() -> str:
    """
    数据库查询全流程的提示词
    """
    return f"""
你是一个专业的 SQL 查询专家。

请按以下步骤工作：
1. 理解用户想要查询什么数据
2. 使用 get_table_names 查看有哪些表
3. 使用 get_table_schema 查看表结构
4. 根据表结构生成正确的 SQL 语句
5. 使用 execute_sql_query 执行查询
6. 用中文解释查询结果

规则：
- 只能使用 SELECT 查询
- 生成 SQL 前必须先了解表结构
- 涉及多个表时使用 JOIN 关联
- 始终用中文回答用户
"""

#
# @mcp.prompt()
# def sql_debugger(sql: str, error: str) -> str:
#     """
#     SQL 调试提示词
#     参数: sql - 有问题的 SQL 语句, error - 错误信息
#     """
#     return f"""
# SQL 语句执行出错，请帮我调试：
#
# SQL: {sql}
# 错误信息: {error}
#
# 请分析：
# 1. 错误原因
# 2. 如何修复
# 3. 给出正确的 SQL 语句
# 4. 如果无法修复，建议替代方案
# """

# ========== 启动服务器 ==========
if __name__ == "__main__":
    mcp.run(transport="stdio")