
import os
import json
import time
import textwrap
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / "daily-print"
ENV_FILE = BASE_DIR / ".env"
PRINTER_PATH = "/dev/usb/lp0"
POLL_INTERVAL = 5

# Load local configuration
for raw_line in ENV_FILE.read_text().splitlines():
    if not raw_line or raw_line.startswith("#"):
        continue
    key, separator, value = raw_line.partition("=")
    if separator:
        os.environ.setdefault(
            key.strip(), value.strip().strip('"').strip("'")
        )

API_URL = os.environ["PRINT_API_URL"].rstrip("/")
API_KEY = os.environ["PRINTER_API_KEY"]


def api_post(endpoint, payload=None):
    data = json.dumps(payload or {}).encode("utf-8")

    request = urllib.request.Request(
        API_URL + endpoint,
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "DailyPrintPi/1.0"
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def print_receipt(job):
    sender = str(job.get("sender") or "Anonymous")[:50]
    message = str(job["message"])[:200]
    job_id = int(job["id"])

    # Keep user-submitted content as plain printable text.
    def safe(value):
        return "".join(
            char if 32 <= ord(char) <= 126 else " "
            for char in value
        )

    sender = safe(sender)
    message = safe(message)

    with open(PRINTER_PATH, "wb", buffering=0) as printer:
        def write(data):
            printer.write(data)

        def line(text=""):
            write((text + "\n").encode("ascii", errors="replace"))

        # Initialize
        write(b"\x1b\x40")

        # Center + bold
        write(b"\x1b\x61\x01")
        write(b"\x1b\x45\x01")
        line("THE DAILY PRINT")
        write(b"\x1b\x45\x00")
        line("INCOMING MESSAGE")
        line()

        # Left alignment
        write(b"\x1b\x61\x00")
        line("-" * 42)
        line(f"FROM: {sender}")
        line(f"MESSAGE #{job_id:04d}")
        line(datetime.now().strftime("%b %d, %Y  %I:%M %p"))
        line("-" * 42)
        line()

        for paragraph in message.splitlines():
            for wrapped in textwrap.wrap(paragraph, width=42):
                line(wrapped)
            if not paragraph.strip():
                line()

        line()
        line("-" * 42)

        # Footer
        write(b"\x1b\x61\x01")
        line("SENT FROM THE INTERNET")
        line()
        line()
        line()

        # Cut paper
        write(b"\x1d\x56\x00")


def main():
    print("Daily Print worker started", flush=True)

    while True:
        try:
            result = api_post("/api/print/claim")

            if result.get("status") == "claimed":
                job = result["message"]
                print(f"Claimed message #{job['id']}", flush=True)

                try:
                    print_receipt(job)
                except Exception as error:
                    print(
                        f"Printing failed for #{job['id']}: {error}",
                        flush=True
                    )
                    # Leave the job in 'printing' to avoid
                    # accidental duplicate receipts.
                else:
                    api_post(
                        "/api/print/complete",
                        {"id": job["id"]}
                    )
                    print(f"Completed message #{job['id']}", flush=True)

        except Exception as error:
            print(f"Worker error: {error}", flush=True)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
