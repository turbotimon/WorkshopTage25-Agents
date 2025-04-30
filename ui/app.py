import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import chainlit as cl

from agents import Runner, enable_verbose_stdout_logging

from agent_repo.public_transport import PublicTransportAgent


enable_verbose_stdout_logging()
agent = PublicTransportAgent()


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def handle_message(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None.
    """

    result = await Runner.run(agent, message.content)

    await cl.Message(content=result.final_output).send()
