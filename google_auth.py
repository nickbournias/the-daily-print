from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.readonly"
]

flow = InstalledAppFlow.from_client_secrets_file(
    str(BASE_DIR / "credentials.json"),
    SCOPES,
)

credentials = flow.run_local_server(
    host="localhost",
    port=8080,
    open_browser=False,
)

token_path = BASE_DIR / "token.json"
token_path.write_text(credentials.to_json())
token_path.chmod(0o600)

print("Google Calendar authorization successful!")
