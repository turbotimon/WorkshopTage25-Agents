import asyncio
from datetime import datetime
from pathlib import Path
import re

from pydantic import BaseModel
import requests
from agents import function_tool
from .calendar_client import ICSClient
import chainlit as cl


def format_duration(duration: str) -> str:
    """Formats the duration returned by the public transport API such that it is more readable."""
    readable_duration_str = "Invalid format"

    match = re.match(r"(\d{2})d(\d{2}):(\d{2}):(\d{2})", duration)
    if match:
        days, hours, minutes, seconds = map(int, match.groups())

        readable_duration = []

        if days > 0:
            readable_duration.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0:
            readable_duration.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            readable_duration.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        if seconds > 0:
            readable_duration.append(f"{seconds} second{'s' if seconds > 1 else ''}")

        readable_duration_str = ", ".join(readable_duration)

    return readable_duration_str


@function_tool
@cl.step(type="tool")
def get_connections(start: str, end: str, date: str, time: str, is_arrival_time: bool):
    """
    Gets public transport connections for a given start and end location and a specific date and time.
    Requires UTF-8 encoded arguments, do not use unicode characters!

    Args:
        start: A string representing either the name of the station or its ID
        end: A string representing either the name of the station or its ID
        date: The date for which to check the connections (iso format)
        time: The time for which to check the connections (%H:%M)
        is_arrival_time: Boolean value specifying whether the date and time refer
            to the arrival (True) or the departure (False). The argument should be formatted
            as a string because it will be converted into a boolean upon executing this tool.

    Returns:
        A list of dictionaries containing the connection details.
    """
    response = requests.get(
        f"http://transport.opendata.ch/v1/connections?from={start}&to={end}&date={date}&time={time}&isArrivalTime={int(is_arrival_time)}"
    )
    data = response.json()

    connections = []
    for connection in data["connections"]:
        departure = datetime.strptime(connection["from"]["departure"], "%Y-%m-%dT%H:%M:%S%z")
        arrival = datetime.strptime(connection["to"]["arrival"], "%Y-%m-%dT%H:%M:%S%z")

        connections.append(
            {
                "from": connection["from"]["station"]["name"],
                "departure_platform": connection["from"]["platform"],
                "departure_date": {"year": departure.year, "month": departure.month, "day": departure.day},
                "departure_time": {"hour": departure.hour, "minute": departure.minute},
                "departure_delay": connection["from"]["delay"],
                "to": connection["to"]["station"]["name"],
                "arrival_platform": connection["to"]["platform"],
                "arrival_date": {"year": arrival.year, "month": arrival.month, "day": arrival.day},
                "arrival_time": {"hour": arrival.hour, "minute": arrival.minute},
                "arrival_delay": connection["to"]["delay"],
                "duration": format_duration(connection["duration"]),
            }
        )

    if not connections:
        raise Exception(
            "Couldn't find any connection, please verify that all of the arguments are correctly formatted in UTF-8"
        )

    return connections


@function_tool
@cl.step(type="tool")
def think(thoughts: str) -> str:
    """
    Use this tool to either come up with a plan to solve the user's query or to
    take a step back and think about the current state of the conversation, i.e.
    whether your can already answer the user's question or whether you need to
    come up with another plan. Write your thoughts in a clear and concise manner.
    If you decide to ask the user for more information, just return the follow up
    question in the next step directly as the output.
    """
    return f"Thoughts: {thoughts}"


async def ask_user(question: str, timeout=120) -> str:
    """
    Ask the user for clarification on a specific question.
    """
    res = await cl.AskUserMessage(content=question, timeout=timeout).send()
    return res["output"] if res else "No user feedback received."


@function_tool
@cl.step(type="tool")
def ask_for_clarification(question: str) -> str:
    """
    Ask the user for clarification on a specific question.
    """
    user_feedback = asyncio.run(ask_user(question))
    return f"""Thought: I need to ask the user for clarification.
        Asking user: {question}
        User response: {user_feedback}"""


class Appointment(BaseModel):
    name: str
    location: str
    start: datetime
    end: datetime


@function_tool
@cl.step(type="tool")
def get_calendar_appointments(date_str: str) -> list[Appointment] | str:
    """
    Get all calendar appointments for a given day.

    Args:
        date_str: The date to get appointments for in ISO format (YYYY-MM-DD)

    Returns:
        List of appointments for the given day, each containing start and end times, name, and location.
        If the date is invalid, a string error message is returned.
    """
    current_dir = Path(__file__).parent
    calendar_path = str(current_dir / "ExampleCalendar.ics")

    try:
        year, month, day = map(int, date_str.split("-"))
        start_datetime = datetime(year, month, day, 0, 0, 0)
        end_datetime = datetime(year, month, day, 23, 59, 59)
    except (ValueError, IndexError):
        return "Invalid date format. Please use YYYY-MM-DD."

    client = ICSClient(calendar_path)
    events = client.list_events(start_datetime, end_datetime)

    appointments: list[Appointment] = []
    for event in events:
        appointment: Appointment = Appointment(
            name=event.name,
            location=event.location,
            start=event.start,
            end=event.end,
        )
        appointments.append(appointment)

    return appointments
