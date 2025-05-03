from typing import Optional
from aia25.bootstrap import *  # noqa: F403,E402

import os
from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

from aia25.tools_repo.mcp_servers import MCPServerRepository


class WebbrowserAgent(Agent):
    @classmethod
    async def setup(cls):
        assert "AGENT_MODEL" in os.environ, "AGENT_MODEL environment variable is not set"
        assert "OPENROUTER_API_KEY" in os.environ, "OPENROUTER_API_KEY environment variable is not set"

        mcp_repo = await MCPServerRepository.get_instance()

        return cls(
            name="Webbrowser Agent",
            instructions=(
                "You are an expert at browsing the web and finding information. "
                "You should use the available web browser tools to accomplish the user's tasks."
            ),
            model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
            mcp_servers=[mcp_repo.get_server("playwright")],
        )
