#!/usr/bin/env python3
"""
天气查询 MCP Server - Mock 版本
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
def get_current_weather(city: str) -> str:
    """
    获取指定城市的当前天气
    :param city: 城市地址
    :return: 天气信息
    """
    return f"{city}: 100°C, 风速 0km/h, 天气状况: ☀️ 超级热"

if __name__ == "__main__":
    print("Server Started")
    mcp.run(transport="stdio")