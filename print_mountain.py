#!/usr/bin/env python3
"""Print the Daily Print mountain header on an Epson TM-T20III via /dev/usb/lp0."""
from datetime import datetime
from pathlib import Path
from PIL import Image

PRINTER = '/dev/usb/lp0'
IMAGE = Path(__file__).resolve().parent / 'images' / 'mountain.png'
MAX_WIDTH = 576


def raster_bytes(image):
    image = image.convert('1')
    width, height = image.size
    if width > MAX_WIDTH:
        raise ValueError('Image exceeds printer width')
    stride = (width + 7) // 8
    data = bytearray()
    pixels = image.load()
    for y in range(height):
        for byte_x in range(stride):
            value = 0
            for bit in range(8):
                x = byte_x * 8 + bit
                if x < width and pixels[x, y] == 0:
                    value |= 0x80 >> bit
            data.append(value)
    return bytes((0x1D, 0x76, 0x30, 0, stride & 255, stride >> 8,
                  height & 255, height >> 8)) + data


def main():
    with Image.open(IMAGE) as original:
        artwork = original.copy()
    artwork.thumbnail((MAX_WIDTH, 1000))
    now = datetime.now()
    receipt = bytearray(b'\x1b@\x1ba\x01')  # Initialize and center
    receipt.extend(raster_bytes(artwork))
    receipt.extend(b'\n\x1d!\x11THE DAILY PRINT\n\x1d!\x00')
    receipt.extend(now.strftime('%A, %B %d, %Y\n').encode('ascii'))
    receipt.extend(b'\nA LITTLE PAPER FOR YOUR DAY\n\n\n\n')
    receipt.extend(b'\x1dV\x00')  # Full cut
    with open(PRINTER, 'wb') as device:
        device.write(receipt)
    print('Mountain receipt sent to printer.')


if __name__ == '__main__':
    main()
