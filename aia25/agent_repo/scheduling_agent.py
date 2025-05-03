from aia25.bootstrap import *  # noqa: F403,E402

from textwrap import dedent

from agents import Agent, RunContextWrapper

from aia25.agent_repo.shared import GlobalContext
from aia25.tools_repo.calendar_scheduling import get_calendar_appointments


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


class SchedulingAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Scheduling Agent",
            instructions=scheduling_agent_system_prompt,
            tools=[get_calendar_appointments],
        )
