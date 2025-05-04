from typing import List
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
import chainlit as cl

from agents import function_tool
from aia25.tools_repo.calendar_client import ICSClient


class Appointment(BaseModel):
    name: str
    location: str
    start: datetime
    end: datetime


@function_tool
@cl.step(type="tool")
def get_calendar_appointments(date_str: str) -> List[Appointment] | str:
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

    appointments: List[Appointment] = []
    for event in events:
        appointment: Appointment = Appointment(
            name=event.name,
            location=event.location,
            start=event.start,
            end=event.end,
        )
        appointments.append(appointment)

    return appointments
