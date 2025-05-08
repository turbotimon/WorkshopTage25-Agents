from textwrap import dedent
from typing import Any, Dict, List
from agents import Agent, RunContextWrapper, Runner, TResponseInputItem
from pydantic import BaseModel
from aia25.tools_repo.calendar_scheduling import get_calendar_appointments
from .my_tools import get_connections


class GlobalContext(BaseModel):
    """
    This class holds the global context for the agent, including the current date and time.
    It is used to provide context to the agent during its execution.
    """

    current_date: str = ""  # Date in YYYY-MM-DD format
    current_time: str = ""  # Time in HH:MM:SS format


def scheduling_agent_system_prompt(context: RunContextWrapper[GlobalContext], agent: Agent[GlobalContext]) -> str:
    ctx = context.context
    return dedent(
        f"""
        You are a scheduling assistant that optimizes transport recommendations based on calendar appointments.

        Current date: {ctx.current_date}
        Current time: {ctx.current_time}

        # Tasks
        - Evaluate transport options against calendar appointments
        - Recommend optimal connections with rationale
        - Ensure journey-appointment alignment

        # Process
        1. For travel requests: Use YYYY-MM-DD format. Retrieve calendar appointments for specified date.
        2. Analyze connections for: appointment conflicts, 15+ min buffers, journey duration, transfers, reliability.
        3. Recommend with: connection details, selection rationale, and schedule considerations.
        4. If no appointments exist, select the most efficient connection.
        """
    )


scheduling_agent = Agent(
    name="Scheduling Agent",
    instructions=scheduling_agent_system_prompt,
    tools=[get_calendar_appointments],
)


def public_transport_agent_system_prompt(
    context: RunContextWrapper[GlobalContext], agent: Agent[GlobalContext]
) -> str:
    ctx = context.context
    return dedent(
        f"""
        You are a public transport assistant that helps users find the best public transport
        connections based on their restrictions and preferences.

        Current date: {ctx.current_date}
        Current time: {ctx.current_time}

        # Tasks
        - Find the best public transport connections between two locations.
        - Provide travel times and schedules.
        - Answer questions about public transport.
        - Help users plan their trips using public transport.

        # Process
        1. For travel requests: Use YYYY-MM-DD format
        2. If more details are needed, ask the user for clarification.
        3. Adhere to the explicit or implicitly provided travel date and time.
        4. Return the optimal connections with travel times and schedules.
        5. Explicitly state travel delays, transfers, and any other relevant information.

        IMPORTANT: After calling the get_connections tool and receiving sufficient information:
        1. Stop calling tools
        2. Synthesize the information into a clear response
        3. Provide a final answer to the user's query

        DO NOT call the same tool multiple times unless specifically needed for different parameters.
        """
    )


public_transport_agent = Agent(
    name="Public Transport Agent",
    instructions=public_transport_agent_system_prompt,
    tools=[get_connections],
)


triage_agent_system_prompt = """
You are a smart assistant that helps users find the best public transport connections
based on their calendar appointments.
1. First find the connections for the given start and end locations, date and time.
2. Then, check the user's calendar appointments for the travel date.
When referring to an appointment, always mention the name of the appointment.
Answer in a friendly and helpful manner.
"""

triage_agent = Agent(
    name="Triage agent",
    instructions=triage_agent_system_prompt,
    tools=[
        public_transport_agent.as_tool(
            tool_name="find_transport_routes",
            tool_description="Find public transport routes between two locations for a specific date and time",
        ),
        scheduling_agent.as_tool(
            tool_name="select_best_connection",
            tool_description=(
                "Select the optimal transport connection by first getting the user's appointments and "
                "then determine the connection that best fits with the user's calendar appointments"
            ),
        ),
    ],
)


async def execute_agent(user_input: str, history: List[Dict[str, str]]) -> tuple[Any, list[TResponseInputItem]]:
    """
    Executes the main agent with the given input and returns the response and the updated history.

    Args:
        user_input: The user's message
        history: The conversation history

    Returns:
        A tuple containing (response_message, updated_history)
        If the guardrail was triggered, updated_history will be None indicating
        the history should not be updated
    """
    current_history = history + [{"role": "user", "content": user_input}]

    result = await Runner.run(starting_agent=triage_agent, input=current_history)

    return result.final_output, result.to_input_list()
