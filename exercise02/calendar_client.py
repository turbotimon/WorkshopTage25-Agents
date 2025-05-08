from datetime import date, datetime
from typing import List, NamedTuple
from dateutil import tz
from ics import Calendar, Event


class CalendarEvent(NamedTuple):
    """
    A named tuple that represents a calendar event with essential properties.

    Attributes:
        start (datetime): Start time of the event
        end (datetime): End time of the event
        name (str): Title of the event
        location (str): Location where the event takes place
    """

    start: datetime
    end: datetime
    name: str
    location: str


class ICSClient:
    """
    A client for working with ICS (iCalendar) files.

    This class allows you to read from and write to ICS calendar files,
    including listing events within a date range and adding new events.
    """

    def __init__(self, path: str):
        """
        Initialize the ICS client with a calendar file.

        Args:
            path (str): Path to the ICS calendar file
        """
        self.path = path
        with open(path, "r", encoding="utf8") as f:
            self.cal = Calendar(f.read())

    def list_events(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        """
        List all events within the specified time range.

        Args:
            start (datetime): Start of the time range (can be timezone-aware or naive)
            end (datetime): End of the time range (can be timezone-aware or naive)

        Returns:
            List[CalendarEvent]: List of calendar events within the specified range

        Note:
            The method handles both timezone-aware and naive datetime objects.
            All returned events have UTC-normalized times with timezone info stripped.
        """
        if start.tzinfo is None:
            start = start.replace(tzinfo=tz.UTC)
        if end.tzinfo is None:
            end = end.replace(tzinfo=tz.UTC)

        return [
            CalendarEvent(
                start=e.begin.astimezone(tz.UTC).replace(tzinfo=None),
                end=e.end.astimezone(tz.UTC).replace(tzinfo=None),
                name=e.name or "",
                location=e.location or "",
            )
            for e in self.cal.timeline
            if e.begin < end and e.end > start
        ]

    def add_event(self, summary: str, start: datetime, end: datetime, location: str = ""):
        """
        Add a new event to the calendar and save it to the ICS file.

        Args:
            summary (str): Title/name of the event
            start (datetime): Start time (can be timezone-aware or naive)
            end (datetime): End time (can be timezone-aware or naive)
            location (str, optional): Location of the event

        Note:
            This method will immediately write the updated calendar to the file.
            Both timezone-aware and naive datetime objects are supported.
        """
        if start.tzinfo is None:
            start = start.replace(tzinfo=tz.UTC)
        if end.tzinfo is None:
            end = end.replace(tzinfo=tz.UTC)

        ev = Event(name=summary, begin=start, end=end)
        if location:
            ev.location = location
        self.cal.events.add(ev)
        with open(self.path, "w", encoding="utf8") as f:
            f.writelines(self.cal.serialize_iter())


if __name__ == "__main__":
    from datetime import datetime, timedelta

    calendar_file = "ExampleCalendar.ics"

    # Create a fresh calendar file
    with open(calendar_file, "w", encoding="utf8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Example//Example Calendar//EN\nEND:VCALENDAR")

    client = ICSClient(calendar_file)

    tomorrow_date = date.today() + timedelta(days=1)

    # Create a datetime at 2pm tomorrow
    tomorrow_2pm = datetime.combine(tomorrow_date, datetime.strptime("2 PM", "%I %p").time())
    print(f"Adding event for: {tomorrow_2pm.strftime('%Y-%m-%d %H:%M')}")

    client.add_event(
        summary="Team Meeting",
        start=tomorrow_2pm,  # Tomorrow at 2pm
        end=tomorrow_2pm + timedelta(hours=1),  # 1 hour duration
        location="Meeting Room A",
    )
    print("Added new event: Team Meeting for tomorrow at 2pm")

    tomorrow_noon = datetime.combine(tomorrow_date, datetime.min.time().replace(hour=12))
    tomorrow_6pm = datetime.combine(tomorrow_date, datetime.min.time().replace(hour=18))

    # Verify the newly added event appears, We'll look specifically for events tomorrow afternoon
    print()
    for e in client.list_events(tomorrow_noon, tomorrow_6pm):
        print(f"- {e.name}: {e.start.strftime('%Y-%m-%d %H:%M')} - {e.end.strftime('%H:%M')} at {e.location}")
