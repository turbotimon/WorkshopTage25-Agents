import asyncio
import time

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio


async def run_agent(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools navigate the webbrowser.",
        mcp_servers=[mcp_server]
    )

    result = await Runner.run(
        starting_agent=agent, input="Go to google and search for cat images, then click on the first image."
    )

    print(result.final_output)
    # Leave the browser open for 10 seconds
    time.sleep(10)


async def main():
    async with MCPServerStdio(
        cache_tools_list=True,
        params={
            "command": "npx",
            "args": ["-y", "@playwright/mcp@latest"],
        },
        client_session_timeout_seconds=15,
    ) as server:
        await run_agent(server)


if __name__ == "__main__":
    asyncio.run(main())
