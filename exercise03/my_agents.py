import os
from typing import Any, Dict, List
from agents import Agent, Runner, TResponseInputItem
from agents.extensions.models.litellm_model import LitellmModel


agent = Agent(
    name="Giraffe",
    instructions="You are a chill giraffe. Respond to the user in your typical giraffe attitude.",
    model=LitellmModel(model=os.getenv("AGENT_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY")),
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

    result = await Runner.run(starting_agent=agent, input=current_history)

    return result.final_output, result.to_input_list()
