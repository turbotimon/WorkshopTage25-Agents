from typing import Any, List
from datetime import datetime
import os
from pathlib import Path
from pydantic import BaseModel

from agents import function_tool
from aia25.tools_repo.calendar_client import ICSClient


class Appointment(BaseModel):
    name: str
    location: str
    start: datetime
    end: datetime


class Connection(BaseModel):
    departure: datetime
    arrival: datetime
    duration: str
    departure_delay: bool = False
    arrival_delay: bool = False


class Conflict(BaseModel):
    appointment: str
    appointment_time: str
    location: str
    reason: str
    severity: str


class ConflictAnalysis(BaseModel):
    connection: dict
    conflicts: List[Conflict]
    has_major_conflict: bool
    total_conflicts: int


class Error(BaseModel):
    error: str


@function_tool
def get_calendar_appointments(date_str: str) -> List[Appointment]:
    """
    Get all calendar appointments for a given day.

    Args:
        date_str: The date to get appointments for in ISO format (YYYY-MM-DD)

    Returns:
        List of appointments for the given day, each containing start and end times, name, and location.
    """
    current_dir = Path(__file__).parent
    calendar_path = str(current_dir / "ExampleCalendar.ics")

    if not os.path.exists(calendar_path):
        # Return empty list instead of error dictionary to match return type
        return []

    # Parse the date string
    try:
        year, month, day = map(int, date_str.split("-"))
        start_datetime = datetime(year, month, day, 0, 0, 0)
        end_datetime = datetime(year, month, day, 23, 59, 59)
    except (ValueError, IndexError):
        # Return empty list instead of error dictionary to match return type
        return []

    # Initialize the calendar client and get the events
    client = ICSClient(calendar_path)
    events = client.list_events(start_datetime, end_datetime)

    # Format the events for the scheduling functions
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


@function_tool
def check_appointment_conflicts(
    connection: Connection, date_str: str, appointments: list[Appointment]
) -> ConflictAnalysis:
    """
    Check if a transport connection conflicts with any calendar appointments.

    Args:
        connection: A public transport connection dictionary with details about departure and arrival
        date_str: The date to check for appointments in ISO format (YYYY-MM-DD)
        appointments: List of appointments to check for conflicts

    Returns:
        Dictionary with conflict analysis
    """

    if len(appointments) == 0:
        return ConflictAnalysis(
            connection={"departure": "", "arrival": "", "duration": ""},
            conflicts=[],
            has_major_conflict=False,
            total_conflicts=0,
        )

    # Create datetime objects for departure and arrival
    try:
        departure = connection.departure
        arrival = connection.arrival
    except (KeyError, TypeError):
        return ConflictAnalysis(
            connection={"departure": "", "arrival": "", "duration": ""},
            conflicts=[],
            has_major_conflict=False,
            total_conflicts=0,
        )

    # Buffer times (in minutes)
    pre_appointment_buffer = 20
    post_appointment_buffer = 15

    conflicts: List[Conflict] = []
    has_major_conflict = False

    for appointment in appointments:
        # Create datetime objects for appointment
        try:
            year, month, day = map(int, date_str.split("-"))

            appt_start = appointment.start
            appt_end = appointment.end
        except (KeyError, ValueError, TypeError):
            continue  # Skip this appointment if format is invalid

        # Check if connection overlaps with appointment
        if departure < appt_end and arrival > appt_start:
            conflicts.append(
                Conflict(
                    appointment=appointment.name,
                    appointment_time=f"{appt_start.strftime('%H:%M')} - {appt_end.strftime('%H:%M')}",
                    location=appointment.location,
                    reason="Transport time overlaps with appointment",
                    severity="major",
                )
            )
            has_major_conflict = True

        # Check if arrival is too close to appointment start
        if appt_start > arrival and (appt_start - arrival).total_seconds() < pre_appointment_buffer * 60:
            conflicts.append(
                Conflict(
                    appointment=appointment.name,
                    appointment_time=f"{appt_start.strftime('%H:%M')} - {appt_end.strftime('%H:%M')}",
                    location=appointment.location,
                    reason=f"Arrival is less than {pre_appointment_buffer} minutes before appointment",
                    severity="minor",
                )
            )

        # Check if departure is too close to appointment end
        if departure > appt_end and (departure - appt_end).total_seconds() < post_appointment_buffer * 60:
            conflicts.append(
                Conflict(
                    appointment=appointment.name,
                    appointment_time=f"{appt_start.strftime('%H:%M')} - {appt_end.strftime('%H:%M')}",
                    location=appointment.location,
                    reason=f"Departure is less than {post_appointment_buffer} minutes after appointment",
                    severity="minor",
                )
            )

    return ConflictAnalysis(
        connection={
            "departure": f"{departure.strftime('%Y-%m-%d %H:%M')}",
            "arrival": f"{arrival.strftime('%Y-%m-%d %H:%M')}",
            "duration": connection.duration,
        },
        conflicts=conflicts,
        has_major_conflict=has_major_conflict,
        total_conflicts=len(conflicts),
    )


def analyze_connection_conflicts(
    connection: Connection, appointments: list[Appointment], travel_date: str
) -> dict[str, Any]:
    """
    Analyze a transport connection for conflicts with calendar appointments.

    Args:
        connection: A public transport connection with details about departure and arrival
        appointments: List of calendar appointments
        travel_date: The date of travel in ISO format (YYYY-MM-DD)

    Returns:
        dictionary with conflict analysis and recommendation score
    """
    # Create datetime objects for departure and arrival
    departure = connection.departure
    arrival = connection.arrival

    # Buffer times (in minutes)
    pre_appointment_buffer = 20
    post_appointment_buffer = 15

    conflicts = []
    score = 100  # Start with perfect score

    for appointment in appointments:
        # Create datetime objects for appointment
        appt_start = appointment.start
        appt_end = appointment.end

        # Check if connection overlaps with appointment
        if departure < appt_end and arrival > appt_start:
            conflicts.append({"appointment": appointment, "reason": "Transport time overlaps with appointment"})
            score -= 50  # Major penalty for direct conflict

        # Check if arrival is too close to appointment start
        if appt_start > arrival and (appt_start - arrival).total_seconds() < pre_appointment_buffer * 60:
            conflicts.append(
                {
                    "appointment": appointment,
                    "reason": f"Arrival is less than {pre_appointment_buffer} minutes before appointment",
                }
            )
            score -= 20  # Penalty for insufficient buffer

        # Check if departure is too close to appointment end
        if departure > appt_end and (departure - appt_end).total_seconds() < post_appointment_buffer * 60:
            conflicts.append(
                {
                    "appointment": appointment,
                    "reason": f"Departure is less than {post_appointment_buffer} minutes after appointment",
                }
            )
            score -= 20  # Penalty for insufficient buffer

    # Adjust score based on trip duration (shorter is better)
    duration_parts = connection.duration.split(", ")
    total_minutes = 0

    for part in duration_parts:
        if "hour" in part:
            hours = int(part.split(" ")[0])
            total_minutes += hours * 60
        elif "minute" in part:
            minutes = int(part.split(" ")[0])
            total_minutes += minutes

    duration_penalty = min(15, total_minutes / 20)  # Longer trips get higher penalties, capped at 15
    score -= duration_penalty

    # Adjust for delays
    if connection.departure_delay or connection.arrival_delay:
        score -= 10  # Penalty for connections with known delays

    return {
        "connection": connection.dict(),
        "conflicts": conflicts,
        "score": max(0, score),  # Score can't be negative
        "duration_minutes": total_minutes,
    }


@function_tool
def find_best_connection(
    connections: list[Connection], appointments: List[Appointment], travel_date: str
) -> dict[str, Any]:
    """
    Find the best connection based on appointments and conflicts.

    Args:
        connections: List of public transport connections with departure and arrival details
        appointments: List of calendar appointments
        travel_date: The date of travel in ISO format (YYYY-MM-DD)

    Returns:
        Dictionary with the best connection and analysis
    """
    if not connections:
        return {"error": "No connections found"}

    analyzed_connections = []

    for connection in connections:
        analysis = analyze_connection_conflicts(connection, appointments, travel_date)
        analyzed_connections.append(analysis)

    # Sort by score (highest first)
    analyzed_connections.sort(key=lambda x: x["score"], reverse=True)

    # Return the best connection with its analysis
    return {
        "best_connection": analyzed_connections[0]["connection"],
        "analysis": analyzed_connections[0],
        "all_analyzed": analyzed_connections,
    }
