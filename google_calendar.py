from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent
TOKEN_PATH = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.readonly"
]

TIMEZONE = ZoneInfo("America/Denver")

CALENDARS = {
    "Nick": "primary",
    "Family": "family07256489403358841644@group.calendar.google.com",
}


def get_todays_events():
    credentials = Credentials.from_authorized_user_file(
        str(TOKEN_PATH), SCOPES
    )

    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            TOKEN_PATH.write_text(credentials.to_json())
            TOKEN_PATH.chmod(0o600)
        else:
            raise RuntimeError("Google Calendar authorization expired")

    service = build(
        "calendar",
        "v3",
        credentials=credentials,
        cache_discovery=False
    )

    now = datetime.now(TIMEZONE)
    start = now.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end = start + timedelta(days=1)

    events = []

    for calendar_name, calendar_id in CALENDARS.items():
        result = service.events().list(
            calendarId=calendar_id,
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=50,
        ).execute()

        for event in result.get("items", []):
            start_data = event.get("start", {})
            title = event.get("summary", "(Untitled event)")

            if "date" in start_data:
                time_label = "ALL DAY"
                sort_time = start
            else:
                event_time = datetime.fromisoformat(
                    start_data["dateTime"].replace("Z", "+00:00")
                ).astimezone(TIMEZONE)

                time_label = event_time.strftime(
                    "%I:%M %p"
                ).lstrip("0")

                sort_time = event_time

            events.append({
                "time": time_label,
                "title": title,
                "calendar": calendar_name,
                "sort_time": sort_time,
            })

    events.sort(key=lambda event: event["sort_time"])

    return [
        (
            event["time"],
            f'{event["calendar"]}: {event["title"]}'
        )
        for event in events
    ]


if __name__ == "__main__":
    for time_label, title in get_todays_events():
        print(f"{time_label}  {title}")
