from agents import Agent

from aia25.tools_repo.mcp_servers import MCPServerRepository


class WebbrowserAgent(Agent):
    @classmethod
    async def setup(cls):
        mcp_repo = await MCPServerRepository.get_instance()

        return cls(
            name="Webbrowser Agent",
            instructions=(
                "You are an expert at browsing the web and finding information. "
                "You should use the available web browser tools to accomplish the user's tasks."
            ),
            mcp_servers=[mcp_repo.get_server("playwright")],
        )
