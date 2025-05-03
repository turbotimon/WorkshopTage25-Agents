import asyncio
from contextlib import AsyncExitStack
import os
from agents.mcp import MCPServerStdio
import chainlit as cl


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
            "playwright": MCPServerStdio(
                cache_tools_list=True,
                params={
                    "command": "npx",
                    "args": ["@playwright/mcp@latest"],
                },
                client_session_timeout_seconds=15,
            ),
            "linkup": MCPServerStdio(
                cache_tools_list=True,
                params={
                    "command": "uvx",
                    "args": ["mcp-search-linkup"],
                    "env": {"LINKUP_API_KEY": os.environ.get("LINKUP_API_KEY")},
                },
                client_session_timeout_seconds=15,
            ),
        }

        # Enter async context for each serverß
        for name, server in servers.items():
            # Wrap the server call_tool method with a Chainlit step
            server.call_tool = cl.step(type="tool")(server.call_tool)

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
        print(f"Available tools: {await repo.get_server('puppeteer').list_tools()}")
    finally:
        await repo.aclose()
        print("MCP servers have been cleaned up.")


if __name__ == "__main__":
    asyncio.run(main())
