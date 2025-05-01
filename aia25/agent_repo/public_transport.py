from aia25.bootstrap import *  # noqa: F403,E402

import os
from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

from aia25.tools_repo.public_transport import get_connections
from aia25.tools_repo.time import get_current_date_and_time


class PublicTransportAgent(Agent):
    def __init__(self):
        assert "AGENT_MODEL" in os.environ, "AGENT_MODEL environment variable is not set"
        assert "OPENROUTER_API_KEY" in os.environ, "OPENROUTER_API_KEY environment variable is not set"
        super().__init__(
            name="Public Transport Agent",
            instructions=(
                "You are a specialist when it comes to planning trips using public transport. "
                "You have access to a public transport API that allows you to look up connections "
                "between two locations. You can also get the current date and time, which is useful "
                "for planning trips. Your goal is to help the user if they have any questions about "
                "public transport. You can answer questions like: 'When does the next train leave?' "
                "or 'How long does it take to get from A to B?'. You can also help the user plan a trip "
                "by providing them with the best connections and travel times. Make sure to plan your "
                "actions before calling a tool. If you don't have enough information to answer the "
                "user's question, ask them for more details."
            ),
            model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
            tools=[get_current_date_and_time, get_connections],
        )
