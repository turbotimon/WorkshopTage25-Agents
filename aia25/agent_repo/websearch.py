from aia25.bootstrap import *  # noqa: F403,E402

from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

from aia25.tools_repo.mcp_servers import MCPServerRepository


class WebsearchAgent(Agent):
    @classmethod
    async def setup(cls):
        mcp_repo = await MCPServerRepository.get_instance()

        return cls(
            name="Webbrowser Agent",
            instructions=(
                "You are an expert at browsing the web and finding the right information. "
                "Use the available tools via Linkup to find relevant information."
            ),
            mcp_servers=[mcp_repo.get_server("linkup")],
            model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
        )
