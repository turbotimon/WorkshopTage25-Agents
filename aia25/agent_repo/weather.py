from aia25.bootstrap import *  # noqa: F403,E402

from agents import Agent

from aia25.tools_repo.mcp_servers import MCPServerRepository


class WeatherAgent(Agent):
    @classmethod
    async def setup(cls):
        mcp_repo = await MCPServerRepository.get_instance()

        return cls(
            name="Weather Agent",
            instructions=(
                "You are an expert at finding weather information. Use the available tools to find the "
                "weather information for a given location and time."
            ),
            mcp_servers=[mcp_repo.get_server("weather")],
        )
