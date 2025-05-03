from aia25.bootstrap import *  # noqa: F403,E402

import os

from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

from aia25.tools_repo.calendar_scheduling import get_calendar_appointments, check_appointment_conflicts
from datetime import datetime


class SchedulingAgent(Agent):
    def __init__(self):
        assert "AGENT_MODEL" in os.environ, "AGENT_MODEL environment variable is not set"
        assert "OPENROUTER_API_KEY" in os.environ, "OPENROUTER_API_KEY environment variable is not set"

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        super().__init__(
            name="Scheduling Agent",
            instructions=(
                "You are a smart scheduling assistant that helps users find the best public transport "
                "connections based on their calendar appointments. Your goal is to recommend the most "
                "suitable connections for the user, taking into account their existing appointments. "
                "You will be provided with connections and have to find the best one"
                f"The current date and time is: {current_time}\n\n"
                "When helping a user find a connection:\n"
                "1. When working with dates, always use the YYYY-MM-DD format (e.g., 2025-05-06 for May 6, 2025)\n"
                "2. Remember that the current year is 2025 - requests for dates in 2024 or earlier cannot be processed\n"
                "3. Retrieve the user's calendar appointments for the travel date\n"
                "4. Analyze how each connection fits with the user's schedule\n"
                "5. Recommend the best connection with a clear explanation\n\n"
                "Consider factors such as:\n"
                "- Avoiding connections that conflict with existing appointments\n"
                "- Providing adequate buffer time before/after appointments\n"
                "- Minimizing travel time and transfers\n"
                "- Accounting for potential delays\n\n"
            ),
            model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
            tools=[get_calendar_appointments, check_appointment_conflicts],
        )
