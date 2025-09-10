import os

os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")  # Disable default OpenAI tracing


import asyncio
import time
from pathlib import Path

from agents import Agent, Runner, set_default_openai_api, set_default_openai_client, enable_verbose_stdout_logging
from agents.mcp import MCPServer, MCPServerStdio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(str(Path(__file__).parent.parent / ".env"))


custom_client = AsyncOpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")
set_default_openai_client(custom_client)
set_default_openai_api("chat_completions")

enable_verbose_stdout_logging()


async def run_agent(mcp_server: MCPServer):
    agent = Agent(name="Assistant", instructions="Use the tools navigate the webbrowser.", mcp_servers=[mcp_server])

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
