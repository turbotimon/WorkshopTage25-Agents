from aia25.agent_repo.triage_agent import triage_agent
from aia25.bootstrap import *  # noqa: F403,E402

import chainlit as cl
from agents import Agent, Runner, enable_verbose_stdout_logging


enable_verbose_stdout_logging()


def get_agent_response(user_message: str):
    agent: Agent = cl.user_session.get("agent")

    # Retrieve the history from the user session and add the user message to it
    history = cl.user_session.get("history") + [{"role": "user", "content": user_message}]

    # Run the agent with the user message and history
    result = Runner.run_sync(agent, history)

    # Overwrite the history with the new one in the user session
    cl.user_session.set("history", result.to_input_list())

    # Return only the final output
    return result.final_output


@cl.on_chat_start
def on_chat_start():
    # Reset the agent and history when the chat starts
    cl.user_session.set("agent", triage_agent)
    cl.user_session.set("history", [])


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def handle_message(message: cl.Message):
    response = get_agent_response(message.content)
    await cl.Message(content=response).send()
