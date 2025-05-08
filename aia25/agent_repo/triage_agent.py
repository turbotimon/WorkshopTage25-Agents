from aia25.bootstrap import *  # noqa: F403,E402

import asyncio
from textwrap import dedent
from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

from aia25.agent_repo.maps import OpenStreetMapAgent
from aia25.agent_repo.public_transport import PublicTransportAgent
from aia25.agent_repo.scheduling_agent import SchedulingAgent
from aia25.agent_repo.weather import WeatherAgent

from aia25.agent_repo.topic_guardrail import topic_guardrail

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "You are a smart assistant that helps users find the best public transport connections "
        "based on their calendar appointments.\n"
        "1. First find the connections for the given start and end locations, date and time.\n"
        "2. Then, check the user's calendar appointments for the travel date.\n"
        "When referring to an appointment, always mention the name of the appointment. "
        "Answer in a friendly and helpful manner. "
    ),
    tools=[
        PublicTransportAgent().as_tool(
            tool_name="find_transport_routes",
            tool_description="Find public transport routes between two locations for a specific date and time",
        ),
        SchedulingAgent().as_tool(
            tool_name="select_best_connection",
            tool_description=(
                "Select the optimal transport connection by first getting the user's appointments and "
                "then determine the connection that best fits with the user's calendar appointments"
            ),
        ),
        asyncio.run(WeatherAgent.setup()).as_tool(
            tool_name="get_weather",
            tool_description="Ask the weather agent to get weather information for a specific location and time",
        ),
        asyncio.run(OpenStreetMapAgent.setup()).as_tool(
            tool_name="explore_locations",
            tool_description=dedent(
                """Explore locations and find information about them. Useful if you want things such as:
                - Find nearby places
                - Get directions for routes
                - Search for specific types of places
                - Find the ideal meeting point for multiple people
                - Get information about a specific place
                - Explore a specific area
                - etc.
                """
            ),
        ),
    ],
    model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
    input_guardrails=[topic_guardrail],  # Add the guardrail here
)
