import os
from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

from aia25.agent_repo.public_transport import PublicTransportAgent
from aia25.agent_repo.scheduling_agent import SchedulingAgent

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "You are a smart assistant that helps users find the best public transport connections "
        "based on their calendar appointments. Your goal is to recommend the most suitable "
        "connections for the user, taking into account their existing appointments. "
        "Answer the user's question, by telling them which connections best fit their schedule. When referring to an appointment, always mention the name of the appointment. "
        "Answer in a friendly and helpful manner. "
    ),
    model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
    tools=[
        PublicTransportAgent().as_tool(
            tool_name="get_public_transport_connections",
            tool_description="Get public transport connections between two locations for a given date and time",
        ),
        SchedulingAgent().as_tool(
            tool_name="identify_best_connection",
            tool_description="from a list of connections identify the best connection for the user based on their calendar appointments",
        ),
    ],
)
