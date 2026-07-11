#!/usr/bin/env python3
"""
天气查询 MCP Server - Mock 版本
"""

import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")


@mcp.tool()
def get_current_weather(city: str) -> str:
    """
    获取指定城市的当前天气。

    :param city: 城市名称，例如：北京、上海
    :return: 当前天气信息
    """
    return f"{city}当前天气：100°C，风速 0km/h，天气状况：☀️ 超级热"


@mcp.tool()
def get_weather_forecast(city: str, days_ahead: int = 1) -> str:
    """
    获取指定城市未来几天的天气预报。

    :param city: 城市名称，例如：北京、上海
    :param days_ahead: 查询未来第几天，1 表示明天
    :return: 天气预报信息
    """
    return (
        f"{city}未来第 {days_ahead} 天的天气："
        f"99°C，风速 1km/h，天气状况：☀️ 依然超级热"
    )


if __name__ == "__main__":
    # stdio 模式下，普通日志只能输出到 stderr
    print("Weather MCP Server Started", file=sys.stderr, flush=True)

    # stdout 交给 MCP SDK，用于传输 JSON-RPC 消息
    mcp.run(transport="stdio")