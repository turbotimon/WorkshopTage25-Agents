import asyncio
from agents.mcp import MCPServerStdio


async def main():
    async with MCPServerStdio(
        cache_tools_list=True,
        params={
            "command": "npx",
            "args": ["-y", "@playwright/mcp@latest"],
        },
        client_session_timeout_seconds=15,
    ) as server:
        tools = await server.list_tools()
        print(tools)


if __name__ == "__main__":
    asyncio.run(main())
