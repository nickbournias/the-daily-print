
import random
from PIL import Image, ImageDraw

PRINTER = "/dev/usb/lp0"
W, H = 512, 190

def draw_mountains():
    random.seed(42)

    img = Image.new("1", (W, H), 1)
    d = ImageDraw.Draw(img)

    # Stars
    for x, y, size in [
        (38, 30, 7), (82, 62, 5),
        (428, 43, 6), (472, 25, 7)
    ]:
        d.line((x-size, y, x+size, y), fill=0, width=2)
        d.line((x, y-size, x, y+size), fill=0, width=2)

    for _ in range(22):
        x = random.randint(15, W-15)
        y = random.randint(10, 95)
        d.point((x, y), fill=0)

    # Distant mountain
    distant = [
        (20, 160), (85, 118), (135, 148),
        (195, 105), (255, 145),
        (340, 95), (400, 145),
        (460, 120), (492, 160)
    ]
    d.line(distant, fill=0, width=2)

    # Main mountain range
    peaks = [
        (15, 170), (90, 135), (125, 155),
        (195, 115), (235, 140),
        (285, 65), (335, 125),
        (385, 110), (435, 150),
        (475, 130), (500, 170)
    ]
    d.line(peaks, fill=0, width=3)

    # Horizontal engraved-style shading
    for y in range(82, 167, 6):
        for x in range(100, 415, 4):
            # Mountain-shaped shading envelope
            boundary = 65 + abs(x-285)*0.42
            if y > boundary and y < 170:
                if random.random() > 0.15:
                    d.line((x, y, x+3, y), fill=0)

    # Snowcap / ridge details
    d.line([
        (260, 94), (285, 65), (308, 99),
        (297, 93), (287, 106), (278, 90)
    ], fill=0, width=2)

    # Baseline
    d.line((20, 172, 492, 172), fill=0, width=1)

    return img

def to_escpos(img):
    img = img.convert("1")
    width, height = img.size
    row_bytes = (width + 7) // 8
    data = bytearray()

    for y in range(height):
        for xb in range(row_bytes):
            value = 0
            for bit in range(8):
                x = xb * 8 + bit
                if x < width and img.getpixel((x, y)) == 0:
                    value |= 0x80 >> bit
            data.append(value)

    return bytes([
        0x1D, 0x76, 0x30, 0x00,
        row_bytes & 255, row_bytes >> 8,
        height & 255, height >> 8
    ]) + data

img = draw_mountains()
img.save("mountains.png")

with open(PRINTER, "wb") as printer:
    printer.write(b"\x1b@")
    printer.write(b"\x1ba\x01")
    printer.write(to_escpos(img))
    printer.write(b"\n")
    printer.write(b"THE DAILY PRINT\n")
    printer.write(b"\n\n\n")
    printer.write(b"\x1dV\x00")

print("Mountain artwork printed!")
