from agents import Agent

from aia25.agent_repo.public_transport import PublicTransportAgent
from aia25.agent_repo.scheduling_agent import SchedulingAgent
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
    ],
    input_guardrails=[topic_guardrail],  # Add the guardrail here
)
