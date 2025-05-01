from datetime import datetime
import re

import requests
from agents import function_tool
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

    :param start: A string representing either the name of the station or its ID
    :param end: A string representing either the name of the station or its ID
    :param date: The date for which to check the connections (iso format)
    :param time: The time for which to check the connections (%H:%M)
    :param is_arrival_time: Boolean value specifying whether the date and time refer
        to the arrival (True) or the departure (False). The argument should be formatted
        as a string because it will be converted into a boolean upon executing this tool.
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
