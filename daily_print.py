
#!/usr/bin/env python3

from datetime import datetime

PRINTER = "/dev/usb/lp0"

def print_receipt():
    today = datetime.now()

    with open(PRINTER, "wb") as printer:
        # Initialize printer
        printer.write(b"\x1b@")

        # Center alignment
        printer.write(b"\x1ba\x01")

        # Double-size title
        printer.write(b"\x1d!\x11")
        printer.write(b"THE DAILY PRINT\n")

        # Normal text size
        printer.write(b"\x1d!\x00")
        printer.write(b"\n")
        printer.write(today.strftime("%A, %B %d, %Y\n").encode())

        # Divider
        printer.write(b"\n")
        printer.write(b"-" * 32 + b"\n")

        # Greeting
        printer.write(b"\n")
        printer.write(b"Good morning!\n")
        printer.write(b"Make today a good one.\n")

        # Footer
        printer.write(b"\n")
        printer.write(b"-" * 32 + b"\n")
        printer.write(b"Powered by Raspberry Pi\n")
        printer.write(b"Version 0.1\n")

        # Feed paper and cut
        printer.write(b"\n\n\n")
        printer.write(b"\x1dV\x00")

    print("The Daily Print printed successfully!")

if __name__ == "__main__":
    print_receipt()
