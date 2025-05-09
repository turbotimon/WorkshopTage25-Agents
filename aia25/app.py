from aia25.bootstrap import *  # noqa: F403,E402
import sys
from pathlib import Path

from agents import enable_verbose_stdout_logging
import chainlit as cl

sys.path.append(str(Path(__file__).resolve().parent.parent))

from exercise01.my_agents import execute_agent as execute_agent_ex01
from exercise02.my_agents import execute_agent as execute_agent_ex02
from exercise03.my_agents import execute_agent as execute_agent_ex03
from exercise04.my_agents import execute_agent as execute_agent_ex04

from solution_exercise02.my_agents import execute_agent as execute_agent_ex02_solution
from solution_exercise03.my_agents import execute_agent as execute_agent_ex03_solution
from solution_exercise04.my_agents import execute_agent as execute_agent_ex04_solution


EXERCISE_TO_EXECUTE_AGENT = {
    "Exercise 1": execute_agent_ex01,
    "Exercise 2": execute_agent_ex02,
    "Exercise 3": execute_agent_ex03,
    "Exercise 4": execute_agent_ex04,
    "Exercise 2 Solution": execute_agent_ex02_solution,
    "Exercise 3 Solution": execute_agent_ex03_solution,
    "Exercise 4 Solution": execute_agent_ex04_solution,
}


async def get_agent_response(user_message: str) -> str:
    """
    Run the agent with the chat history and the given user message and update the history.
    Returns only the final output.

    Args:
        user_message: The user's message.

    Returns:
        The agent's response.
    """
    # Retrieve the history from the user session and add the user message to it
    history = cl.user_session.get("history") or []

    # Retrieve the execute agent function from the user session
    execute_agent = cl.user_session.get("execute_agent", EXERCISE_TO_EXECUTE_AGENT["Exercise 1"])

    # Execute agent with input and handle exceptions in the service layer
    response, updated_history = await execute_agent(user_input=user_message, history=history)

    # Only update history if we got a valid updated history back
    if updated_history is not None:
        cl.user_session.set("history", updated_history)

    return response


@cl.on_chat_start
async def on_chat_start():
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="exercise",
                label="Exercise",
                values=[
                    "Exercise 1",
                    "Exercise 2",
                    "Exercise 3",
                    "Exercise 4",
                    "Exercise 2 Solution",
                    "Exercise 3 Solution",
                    "Exercise 4 Solution",
                ],
                initial_index=0,
            ),
            cl.input_widget.Switch(
                id="verbose_stdout_logging",
                label="Enable verbose stdout logging",
                initial_value=False,
                description="Enable verbose logging for stdout. This is useful for debugging.",
            ),
        ]
    ).send()

    # Update the agent execution function based on the selected exercise
    await on_settings_update(settings)

    # Reset the chat history
    cl.user_session.set("history", [])


@cl.on_settings_update
async def on_settings_update(settings):
    # Update the agent execution function based on the selected exercise
    cl.user_session.set("execute_agent", EXERCISE_TO_EXECUTE_AGENT[settings["exercise"]])

    # If user selected verbose logging, enable it (can't be disabled until restart)
    if settings["verbose_stdout_logging"]:
        enable_verbose_stdout_logging()


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def handle_message(message: cl.Message):
    response = await get_agent_response(message.content)
    await cl.Message(content=response).send()


@cl.server.app.on_event("shutdown")
async def on_shutdown():
    # Get the current selected exercise from the user session
    current_exercise = cl.user_session.get("execute_agent", None)

    # Variable to hold the correct repository class
    repo_class = None

    # Determine the repository class based on the selected exercise
    if current_exercise == execute_agent_ex02:
        from exercise02.my_tools import McpServerRepository

        repo_class = McpServerRepository
    elif current_exercise == execute_agent_ex03:
        from exercise03.my_agents import McpServerRepository

        repo_class = McpServerRepository
    elif current_exercise == execute_agent_ex04:
        from exercise04.my_agents import McpServerRepository

        repo_class = McpServerRepository
    elif current_exercise == execute_agent_ex02_solution:
        from solution_exercise02.my_agents import McpServerRepository

        repo_class = McpServerRepository
    elif current_exercise == execute_agent_ex03_solution:
        from solution_exercise03.my_agents import McpServerRepository

        repo_class = McpServerRepository
    elif current_exercise == execute_agent_ex04_solution:
        from solution_exercise04.my_agents import McpServerRepository

        repo_class = McpServerRepository

    repo = await repo_class.get_instance()
    await repo.aclose()
