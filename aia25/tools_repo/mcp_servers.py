import asyncio
from contextlib import AsyncExitStack
import os
from agents.mcp import MCPServerStdio
import chainlit as cl


def make_wrapped_call_tool(mcp_server_name, call_tool_func):
    async def wrapped_call_tool(*args, **kwargs):
        tool_name = kwargs.get("tool_name") or (args[0] if args else "call_tool")

        @cl.step(type="tool", name=f"[{mcp_server_name}] {tool_name}")
        async def inner(*args, **kwargs):
            return await call_tool_func(*args, **kwargs)

        return await inner(*args, **kwargs)

    return wrapped_call_tool


class MCPServerRepository:
    _instance = None

    def __init__(self):
        self.stack = AsyncExitStack()
        self.servers = {}

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            repo = MCPServerRepository()
            await repo._setup()
            cls._instance = repo
        return cls._instance

    async def _setup(self):
        servers = {
            # "playwright": MCPServerStdio(
            #     cache_tools_list=True,
            #     params={
            #         "command": "npx",
            #         "args": ["@playwright/mcp@latest"],
            #     },
            #     client_session_timeout_seconds=15,
            # ),
            # "linkup": MCPServerStdio(
            #     cache_tools_list=True,
            #     params={
            #         "command": "uvx",
            #         "args": ["mcp-search-linkup"],
            #         "env": {"LINKUP_API_KEY": os.environ.get("LINKUP_API_KEY")},
            #     },
            #     client_session_timeout_seconds=15,
            # ),
            "weather": MCPServerStdio(
                cache_tools_list=True,
                params={
                    "command": "uvx",
                    "args": [
                        "--from",
                        "git+https://github.com/rolshoven/weather-mcp-server.git",
                        "weather-mcp-server",
                    ],
                    "env": {"WEATHER_API_KEY": os.environ.get("WEATHER_API_KEY")},
                },
                client_session_timeout_seconds=5,
            ),
            "openstreetmap": MCPServerStdio(
                cache_tools_list=True,
                params={
                    "command": "uvx",
                    "args": [
                        "--from",
                        "git+https://github.com/jagan-shanmugam/open-streetmap-mcp.git",
                        "osm-mcp-server",
                    ],
                },
                client_session_timeout_seconds=5,
            ),
        }

        # Enter async context for each server
        for name, server in servers.items():
            # Wrap the server call_tool method with a Chainlit step
            # server.call_tool = cl.step(type="tool")(server.call_tool)
            server.call_tool = make_wrapped_call_tool(name, server.call_tool)

            # Enter async context for each server
            servers[name] = await self.stack.enter_async_context(server)

        self.servers = servers

    async def aclose(self):
        await self.stack.aclose()

    def get_server(self, name):
        return self.servers.get(name)


async def main():
    repo = await MCPServerRepository.get_instance()
    try:
        print("MCP servers are set up and ready to use.")
        print(f"Available tools: {await repo.get_server('weather').list_tools()}")
        # result = await repo.get_server("weather").call_tool("weather_current", {"q": "Bern", "aqi": "no"})
        # print("Weather in Bern:", result)
    finally:
        await repo.aclose()
        print("MCP servers have been cleaned up.")


if __name__ == "__main__":
    asyncio.run(main())
