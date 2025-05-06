from textwrap import dedent
from aia25.agent_repo.shared import GlobalContext
from aia25.bootstrap import *  # noqa: F403,E402

from agents import Agent, RunContextWrapper
from agents.extensions.models.litellm_model import LitellmModel

from aia25.tools_repo.mcp_servers import MCPServerRepository


def weather_agent_system_prompt(context: RunContextWrapper[GlobalContext], agent: Agent[GlobalContext]) -> str:
    ctx = context.context
    return dedent(
        f"""
        You are an expert at finding weather information. Use the available tools to find the 
        weather information for a given location and time.

        Current date: {ctx.current_date}
        Current time: {ctx.current_time}

        If the user asks for a specific date and time, use that information. If the user refers
        to the current date and time, use the current date and time specified above.
        """
    )


class WeatherAgent(Agent):
    @classmethod
    async def setup(cls):
        mcp_repo = await MCPServerRepository.get_instance()

        return cls(
            name="Weather Agent",
            instructions=weather_agent_system_prompt,
            mcp_servers=[mcp_repo.get_server("weather")],
            model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
        )
