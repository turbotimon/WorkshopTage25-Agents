from datetime import datetime
from aia25.agent_repo.shared import GlobalContext
from aia25.agent_repo.agent_service import execute_agent, get_default_agent
from aia25.bootstrap import *  # noqa: F403,E402

import chainlit as cl
from agents import enable_verbose_stdout_logging


enable_verbose_stdout_logging()


def get_agent_response(user_message: str):
    agent = cl.user_session.get("agent")
    history = cl.user_session.get("history") or []
    global_context = cl.user_session.get("global_context") or GlobalContext()

    # Execute agent with input and handle exceptions in the service layer
    response, updated_history = execute_agent(
        agent=agent, user_input=user_message, history=history, context=global_context
    )

    # Only update history if we got a valid updated history back
    # (it will be None if the guardrail was triggered)
    if updated_history is not None:
        cl.user_session.set("history", updated_history)

    return response


@cl.on_chat_start
def on_chat_start():
    current_datetime = datetime.now()
    date_only = current_datetime.strftime("%Y-%m-%d")
    time_only = current_datetime.strftime("%H:%M:%S")

    # Reset the agent and history when the chat starts
    cl.user_session.set("agent", get_default_agent())
    cl.user_session.set("history", [])
    cl.user_session.set("global_context", GlobalContext(current_date=date_only, current_time=time_only))


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def handle_message(message: cl.Message):
    response = get_agent_response(message.content)
    await cl.Message(content=response).send()
