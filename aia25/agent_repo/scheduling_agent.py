from aia25.agent_repo.shared import GlobalContext
from aia25.bootstrap import *  # noqa: F403,E402

import os

from agents import Agent, RunContextWrapper
from agents.extensions.models.litellm_model import LitellmModel

from aia25.tools_repo.calendar_scheduling import get_calendar_appointments


def scheduling_agent_system_prompt(context: RunContextWrapper[GlobalContext], agent: Agent[GlobalContext]) -> str:
    ctx = context.context
    return f"""
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


class SchedulingAgent(Agent):
    def __init__(self):
        assert "AGENT_MODEL" in os.environ, "AGENT_MODEL environment variable is not set"
        assert "OPENROUTER_API_KEY" in os.environ, "OPENROUTER_API_KEY environment variable is not set"

        super().__init__(
            name="Scheduling Agent",
            instructions=scheduling_agent_system_prompt,
            model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
            tools=[get_calendar_appointments],
        )
