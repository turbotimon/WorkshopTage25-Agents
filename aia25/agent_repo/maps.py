from aia25.bootstrap import *  # noqa: F403,E402

from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

from aia25.tools_repo.mcp_servers import MCPServerRepository


class OpenStreetMapAgent(Agent):
    @classmethod
    async def setup(cls):
        mcp_repo = await MCPServerRepository.get_instance()

        return cls(
            name="OpenStreetMap Agent",
            instructions=(
                "You are an expert at providing location-based information. Use the available tools "
                "to answer questions about route directions, nearby places, points of interest, etc."
            ),
            mcp_servers=[mcp_repo.get_server("openstreetmap")],
            model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
        )
