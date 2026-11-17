#!/usr/bin/env python3
"""The Daily Print — Raspberry Pi + Epson TM-T20III."""

from datetime import datetime
from pathlib import Path
import json
import random
import textwrap
import time
import urllib.request

from PIL import Image, ImageDraw, ImageFont, ImageOps
from google_calendar import get_todays_events

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "images" / "mountain.png"
PRINTER_PATH = "/dev/usb/lp0"
PRINT_WIDTH = 576
TEXT_WIDTH = 48
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

GREETINGS = [
    "Good morning.", "Rise and shine.", "Hello, today.",
    "A fresh start.", "Here's to today.", "Morning!",
    "Another beautiful day.", "Welcome to a new day.",
    "Make it a good one.", "A new day begins.",
]

THOUGHTS = [
    ("The journey of a thousand miles begins with a single step.", "Lao Tzu"),
    ("The only way out is through.", "Robert Frost"),
    ("Well done is better than well said.", "Benjamin Franklin"),
    ("The unexamined life is not worth living.", "Socrates"),
    ("What we think, we become.", "Traditional saying"),
    ("Simplicity is the ultimate sophistication.", "Often attributed to Leonardo da Vinci"),
    ("The obstacle is the way.", "Stoic-inspired saying"),
]

HABITS = [
    "Get outside for 10 minutes",
    "Stretch for 5 minutes",
    "Meditate for 5 min BEFORE 10 AM",
    "Meditate for 5 min AFTER 10 AM",
]


def write(printer, data):
    printer.write(data)
    printer.flush()


def line(printer, text=""):
    write(printer, (text + "\n").encode("ascii", errors="replace"))


def center(printer):
    write(printer, b"\x1b\x61\x01")


def left(printer):
    write(printer, b"\x1b\x61\x00")


def bold(printer, enabled=True):
    write(printer, b"\x1b\x45" + (b"\x01" if enabled else b"\x00"))


def text_size(printer, width=1, height=1):
    value = ((width - 1) << 4) | (height - 1)
    write(printer, b"\x1d\x21" + bytes([value]))


def divider(printer):
    left(printer)
    line(printer, "-" * TEXT_WIDTH)


def heading(printer, title):
    line(printer)
    bold(printer, True)
    line(printer, title)
    bold(printer, False)
    divider(printer)


def raster_bytes(image):
    """Encode a 1-bit Pillow image as ESC/POS GS v 0 raster data."""
    image = image.convert("1")
    width, height = image.size
    bytes_per_row = (width + 7) // 8
    data = bytearray()
    for y in range(height):
        for byte_x in range(bytes_per_row):
            value = 0
            for bit in range(8):
                x = byte_x * 8 + bit
                if x < width and image.getpixel((x, y)) == 0:
                    value |= 0x80 >> bit
            data.append(value)
    return (
        b"\x1d\x76\x30\x00"
        + bytes([
            bytes_per_row & 255,
            (bytes_per_row >> 8) & 255,
            height & 255,
            (height >> 8) & 255,
        ])
        + data
    )


def print_mountain(printer):
    if not IMAGE_PATH.exists():
        print(f"Mountain image not found: {IMAGE_PATH}", flush=True)
        return
    with Image.open(IMAGE_PATH) as source:
        image = source.convert("RGB")
    gray = ImageOps.grayscale(image)
    mask = gray.point(lambda pixel: 255 if pixel < 180 else 0)
    bounds = mask.getbbox()
    if bounds:
        image = image.crop(bounds)
    new_height = max(1, round(image.height * PRINT_WIDTH / image.width))
    image = image.resize((PRINT_WIDTH, new_height), Image.Resampling.LANCZOS)
    image = ImageOps.grayscale(image).convert(
        "1", dither=Image.Dither.FLOYDSTEINBERG
    )
    left(printer)
    write(printer, raster_bytes(image))
    line(printer)


def print_header(printer, now):
    print_mountain(printer)
    center(printer)
    bold(printer, True)
    text_size(printer, 2, 2)
    line(printer, "THE DAILY PRINT")
    text_size(printer)
    bold(printer, False)
    line(printer)
    line(printer, now.strftime("%A, %B %d, %Y").upper())
    line(printer)
    line(printer, random.choice(GREETINGS))
    left(printer)


def get_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=39.75&longitude=-105.02"
        "&current=temperature_2m,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        "&temperature_unit=fahrenheit"
        "&wind_speed_unit=mph"
        "&timezone=America%2FDenver"
        "&forecast_days=1"
    )
    request = urllib.request.Request(url, headers={"User-Agent": "DailyPrint/1.0"})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.load(response)
            current = data["current"]
            daily = data["daily"]
            return {
                "temp": round(current["temperature_2m"]),
                "high": round(daily["temperature_2m_max"][0]),
                "low": round(daily["temperature_2m_min"][0]),
                "rain": daily["precipitation_probability_max"][0],
                "wind": round(current["wind_speed_10m"]),
            }
        except Exception as error:
            print(f"Weather attempt {attempt}/3 failed: {error}", flush=True)
            if attempt == 3:
                raise
            time.sleep(5)


def print_weather(printer):
    heading(printer, "DENVER WEATHER")
    try:
        weather = get_weather()
        col_width = TEXT_WIDTH // 2

        def two_cols(first, second):
            line(printer, first.ljust(col_width) + second)

        two_cols(f"CURRENT TEMP: {weather['temp']} F", f"HIGH: {weather['high']} F")
        two_cols(f"RAIN: {weather['rain']}%", f"LOW: {weather['low']} F")
        two_cols(f"WIND: {weather['wind']} mph", "")
    except Exception as error:
        print(f"Weather fetch failed: {error}", flush=True)
        line(printer, "Weather unavailable")


def print_calendar(printer):
    heading(printer, "TODAY'S CALENDAR")

    try:
        events = get_todays_events()

        if not events:
            line(printer, "No events today.")
            return

        for time_label, title in events:
            entry = f"{time_label}  {title}"

            for wrapped_line in textwrap.wrap(
                entry,
                width=TEXT_WIDTH,
                subsequent_indent="    "
            ):
                line(printer, wrapped_line)

    except Exception as error:
        print(f"Calendar fetch failed: {error}", flush=True)
        line(printer, "Calendar unavailable")


def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        print("DejaVu font unavailable; using Pillow fallback", flush=True)
        return ImageFont.load_default()


def print_checkbox(printer, label=""):
    """Print a real square and optional label in one aligned raster row."""
    row_height = 42
    image = Image.new("1", (PRINT_WIDTH, row_height), 1)
    draw = ImageDraw.Draw(image)
    draw.rectangle((5, 8, 29, 32), outline=0, width=2)
    if label:
        font = load_font(22)
        # Shrink only if needed to keep the full label on the paper.
        for size in range(22, 13, -1):
            font = load_font(size)
            if draw.textbbox((0, 0), label, font=font)[2] <= PRINT_WIDTH - 50:
                break
        draw.text((44, 7), label, font=font, fill=0)
    left(printer)
    write(printer, raster_bytes(image))


def print_checklist(printer):
    heading(printer, "TODAY'S CHECKLIST")
    for habit in HABITS:
        print_checkbox(printer, habit)
    bold(printer, True)


def get_daily_quote():
    request = urllib.request.Request(
        "https://nickbournias.com/daily-quote.json",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.load(response)
    return data["quote"], data["author"]


def print_thought(printer):
    # Single separator; no empty heading or extra trailing dividers.
    line(printer)
    divider(printer)
    line(printer)
    try:
        quote, author = get_daily_quote()
    except Exception as error:
        print(f"Quote fetch failed: {error}", flush=True)
        quote, author = random.choice(THOUGHTS)
    for wrapped_line in textwrap.wrap(f'"{quote}"', width=TEXT_WIDTH - 4):
        line(printer, wrapped_line)
    line(printer)
    line(printer, f"- {author}")
    line(printer)
    divider(printer)


def main():
    now = datetime.now()
    with open(PRINTER_PATH, "wb", buffering=0) as printer:
        write(printer, b"\x1b\x40")
        print_header(printer, now)
        print_weather(printer)
        print_calendar(printer)
        print_checklist(printer)
        print_thought(printer)
        line(printer)
        line(printer)
        line(printer)
        line(printer)
        write(printer, b"\x1d\x56\x00")


if __name__ == "__main__":
    main()
