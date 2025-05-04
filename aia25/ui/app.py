from datetime import datetime
from aia25.agent_repo.shared import GlobalContext
from aia25.agent_repo.triage_agent import triage_agent
from aia25.bootstrap import *  # noqa: F403,E402

import chainlit as cl
from agents import Agent, Runner, enable_verbose_stdout_logging


enable_verbose_stdout_logging()


def get_agent_response(user_message: str):
    agent: Agent = cl.user_session.get("agent")

    # Retrieve the history from the user session and add the user message to it
    history = cl.user_session.get("history") or [] + [{"role": "user", "content": user_message}]

    # retrieve the global context from the user session
    global_context: GlobalContext = cl.user_session.get("global_context") or GlobalContext()

    # Run the agent with the user message and history
    result = Runner.run_sync(starting_agent=agent, input=history, context=global_context)

    # Overwrite the history with the new one in the user session
    cl.user_session.set("history", result.to_input_list())

    # Return only the final output
    return result.final_output


@cl.on_chat_start
def on_chat_start():
    current_datetime = datetime.now()
    date_only = current_datetime.strftime("%Y-%m-%d")
    time_only = current_datetime.strftime("%H:%M:%S")

    # Reset the agent and history when the chat starts
    cl.user_session.set("agent", triage_agent)
    cl.user_session.set("history", [])
    cl.user_session.set("global_context", GlobalContext(current_date=date_only, current_time=time_only))


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def handle_message(message: cl.Message):
    response = get_agent_response(message.content)
    await cl.Message(content=response).send()
