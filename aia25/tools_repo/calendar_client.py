# calendar_client.py
from datetime import datetime
from typing import List, NamedTuple
from dateutil import tz
from ics import Calendar, Event  # tiny, pure‑Python


class CalendarEvent(NamedTuple):
    start: datetime
    end: datetime
    name: str
    location: str


class ICSClient:
    def __init__(self, path: str):
        self.path = path
        with open(path, "r", encoding="utf8") as f:
            self.cal = Calendar(f.read())

    def list_events(self, start: datetime, end: datetime) -> List[CalendarEvent]:
        # Make sure start and end are timezone-aware if they aren't already
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
            for e in self.cal.timeline  # timeline auto‑expands recurrences
            if e.begin < end and e.end > start
        ]

    def add_event(self, summary: str, start: datetime, end: datetime, location: str = ""):
        # Make sure start and end are timezone-aware if they aren't already
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


# identical interface, different engines ----------------------
# Outlook: subclass using O365.Event objects
# CalDAV : subclass using caldav.Event objects

if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path

    # Get the path to ExampleCalendar.ics
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    calendar_path = current_dir / "ExampleCalendar.ics"

    if not calendar_path.exists():
        print(f"Error: Calendar file not found at {calendar_path}")
        sys.exit(1)

    # Initialize the calendar client
    client = ICSClient(str(calendar_path))

    # Test listing events for next month - use timezone-aware datetimes
    today = datetime.now(tz.UTC)
    next_month = datetime(today.year, today.month + 1 if today.month < 12 else 1, 1, tzinfo=tz.UTC)
    end_next_month = datetime(next_month.year, next_month.month + 1 if next_month.month < 12 else 1, 1, tzinfo=tz.UTC)

    print(f"\nListing events from {next_month.strftime('%Y-%m-%d')} to {end_next_month.strftime('%Y-%m-%d')}:")
    events = client.list_events(next_month, end_next_month)

    if events:
        for i, event in enumerate(events, 1):
            print(f"Event {i}: {event.name}")
            print(f"  Time: {event.start.strftime('%Y-%m-%d %H:%M')} - {event.end.strftime('%Y-%m-%d %H:%M')}")
            if event.location:
                print(f"  Location: {event.location}")
            print()
    else:
        print("No events found in the specified time range.")

    # Test adding a new event - use timezone-aware datetimes
    new_event_start = datetime(today.year, today.month, today.day, 14, 0, tzinfo=tz.UTC)  # Today at 2 PM
    new_event_end = datetime(today.year, today.month, today.day, 15, 0, tzinfo=tz.UTC)  # Today at 3 PM

    print(
        f"\nAdding a new event 'Team Meeting' from {new_event_start.strftime('%Y-%m-%d %H:%M')} to {new_event_end.strftime('%Y-%m-%d %H:%M')}"
    )
    client.add_event("Team Meeting", new_event_start, new_event_end, location="Conference Room B")

    # Verify the event was added
    today_start = datetime(today.year, today.month, today.day, 0, 0, tzinfo=tz.UTC)
    tomorrow_start = datetime(today.year, today.month, today.day + 1, 0, 0, tzinfo=tz.UTC)
    events = client.list_events(today_start, tomorrow_start)
    print("\nEvents for today after adding the new event:")
    for i, event in enumerate(events, 1):
        print(f"Event {i}: {event.name}")
        print(f"  Time: {event.start.strftime('%Y-%m-%d %H:%M')} - {event.end.strftime('%Y-%m-%d %H:%M')}")
        if event.location:
            print(f"  Location: {event.location}")
        print()
