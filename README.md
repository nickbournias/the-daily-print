# The Daily Print 🧾

The Daily Print is a Raspberry Pi-powered thermal receipt printer project that turns digital information into small, tangible prints. It automatically prints a personalized morning briefing and can receive on-demand messages from a web interface.

Built around an **Epson TM-T20III** receipt printer and a **Raspberry Pi 4 Model B**.

## What it does

### ☀️ Daily morning receipt

A scheduled Python script generates a compact daily printout featuring:

- A morning greeting
- Local weather
- A calendar / day overview
- A daily quote

The goal is to make the morning briefing useful without turning it into another screen to check.

### ✉️ Print messages from the web

A custom website interface lets me send short messages to the printer. These arrive as physical receipt-style slips, with distinctive formatting for incoming messages. Want to try it? Send me a message at https://nickbournias.com/contact.

The web-to-printer workflow uses a Cloudflare-protected endpoint. 

## Hardware

| Component | Purpose |
| --- | --- |
| Raspberry Pi 4 Model B | Runs the printing scripts and automation |
| Epson TM-T20III | 80 mm thermal receipt printer |
| USB connection | Connects the printer to the Pi |

## Software and services

- **Python 3** for generating and sending print jobs
- **Linux / Raspberry Pi OS** on the Pi
- **cron** for scheduled execution
- **Cloudflare** for the secured web-facing workflow
- **Weather API** for current conditions
- **Git / GitHub** for version control

The project uses a Python-based receipt-printing workflow; exact package dependencies and environment settings should be taken from the source code in this repository.

## Getting started

This is a personal project, so setup depends on your printer, Raspberry Pi configuration, and the scripts included in the repository.

1. Connect a supported USB thermal receipt printer to a Raspberry Pi.
2. Install Python 3 and the dependencies used by the project scripts.
3. Configure the printer connection and any required API credentials.
4. Run the printing script manually to verify the layout and printer communication.
5. Schedule the daily script using cron.
6. If enabling web-triggered printing, configure the Cloudflare endpoint and its secret separately.

> **Security:** Never commit API keys, Cloudflare secrets, tokens, or local environment files. Use environment variables or a private configuration mechanism, and authenticate requests before accepting remote print jobs.

## Design philosophy

The Daily Print is deliberately simple:

- **Physical over digital:** A small paper receipt can feel more intentional than another notification.
- **Useful, not overwhelming:** Only a handful of things worth seeing each morning.
- **Playful formatting:** Receipt typography, compact graphics, and small details make ordinary information more fun.
- **Hackable by design:** New data sources and print formats can be added as the project evolves.

## Ideas for future prints

- Short, relevant articles with QR codes linking to the full text
- Weekly snowboarding conditions and mountain forecasts
- More calendar integrations
- Special holiday editions
- Additional custom receipt templates

