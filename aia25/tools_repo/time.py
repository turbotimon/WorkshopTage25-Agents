from datetime import datetime
from agents import function_tool
import chainlit as cl


@function_tool
@cl.step(type="tool")
def get_current_date_and_time() -> str:
    """
    Get the current date and time in ISO format.
    """
    return datetime.now().isoformat()
