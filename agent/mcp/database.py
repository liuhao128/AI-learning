#!/usr/bin/env python3
"""
MySQL MCP Server - Mock版本
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MySQL")

# Mock数据
TABLES = {
    "users": "id, username, email, created_at",
    "orders": "id, user_id, product, amount, status",
    "products": "id, name, price, stock"
}

@mcp.tool()
def list_tables() -> str:
    """
    列出所有表
    :return: 所有的表名
    """
    return f"📋 数据库表: {', '.join(TABLES.keys())}"

@mcp.tool()
def describe_table(table_name: str) -> str:
    """
    查看表结构
    :param table_name: 表名
    :return: 表的描述信息
    """
    if table_name in TABLES:
        return f"📊 表 {table_name} 的字段: {TABLES[table_name]}"
    return f"❌ 表 {table_name} 不存在"

if __name__ == "__main__":
    print("MCP Server Started")
    mcp.run(transport="stdio")