from aia25.bootstrap import *  # noqa: F403,E402

from textwrap import dedent

from agents import Agent, RunContextWrapper

from aia25.agent_repo.shared import GlobalContext
from aia25.tools_repo.public_transport import get_connections


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


class PublicTransportAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Public Transport Agent",
            instructions=public_transport_agent_system_prompt,
            tools=[get_connections],
        )
