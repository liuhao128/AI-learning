"""
MCP 数据库服务器启动文件
这个文件负责启动 MCP 服务器，将所有工具注册到 MCP 协议中
"""

from mcp_tools import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")