from agents import Agent, Runner, InputGuardrailTripwireTriggered, TResponseInputItem
from aia25.agent_repo.shared import GlobalContext
from aia25.agent_repo.topic_guardrail import OFF_TOPIC_MESSAGE
from typing import Any, List, Dict


def execute_agent(
    agent: Agent, user_input: str, history: List[Dict[str, str]], context: GlobalContext
) -> tuple[Any, list[TResponseInputItem]]:
    """
    Executes the agent with the given input and handles any guardrail exceptions.

    Args:
        agent: The agent to execute
        user_input: The user's message
        history: The conversation history
        context: The global context

    Returns:
        A tuple containing (response_message, updated_history)
        If the guardrail was triggered, updated_history will be None indicating
        the history should not be updated
    """
    current_history = history + [{"role": "user", "content": user_input}]

    try:
        result = Runner.run_sync(starting_agent=agent, input=current_history, context=context)

        return result.final_output, result.to_input_list()
    except InputGuardrailTripwireTriggered:
        return OFF_TOPIC_MESSAGE, None


def get_default_agent() -> Agent:
    """
    Returns the default agent for the application (currently the triage agent).
    """
    from aia25.agent_repo.triage_agent import triage_agent

    return triage_agent


if __name__ == "__main__":
    from aia25.agent_repo.triage_agent import triage_agent
    import datetime

    context = GlobalContext(
        current_date=datetime.date.today().isoformat(),
        current_time=datetime.datetime.now().time().strftime("%H:%M:%S"),
    )

    user_input = "What is the meaning of life?"
    history = []

    response, new_history = execute_agent(triage_agent, user_input, history, context)
    print("Response:", response)
    if new_history is None:
        print("Guardrail triggered: history not updated")
    else:
        print("Updated history:", new_history)
