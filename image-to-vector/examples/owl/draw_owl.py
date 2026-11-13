"""Draws the bundled example: an original flat owl mascot with a caption.

Usage: python -I draw_owl.py [out.png]

Drawn at 4x and scaled down, so its edges are anti-aliased like real artwork.
The caption is there to show the trace config's `ignore` rectangles.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

S = 4  # supersampling factor
W, H = 400, 440
LINE = (28, 22, 30)
BODY = (232, 122, 46)
BELLY = (250, 226, 180)
FACE = (252, 238, 214)
EYE = (255, 255, 255)
IRIS = (38, 166, 154)
BEAK = (250, 196, 40)
WING = (184, 84, 34)

image = Image.new("RGB", (W * S, H * S), (255, 255, 255))
draw = ImageDraw.Draw(image)
w = 5 * S  # outline width


def box(x0, y0, x1, y1):
    return [x0 * S, y0 * S, x1 * S, y1 * S]


def poly(points):
    return [(x * S, y * S) for x, y in points]


# Ear tufts, then the body over them.
draw.polygon(poly([(110, 120), (96, 40), (170, 95)]), fill=BODY, outline=LINE, width=w)
draw.polygon(poly([(290, 120), (304, 40), (230, 95)]), fill=BODY, outline=LINE, width=w)
draw.ellipse(box(80, 70, 320, 380), fill=BODY, outline=LINE, width=w)
# Wings.
draw.chord(box(66, 190, 150, 350), 90, 270, fill=WING, outline=LINE, width=w)
draw.chord(box(250, 190, 334, 350), 270, 90, fill=WING, outline=LINE, width=w)
# Belly with three feather marks.
draw.ellipse(box(135, 215, 265, 360), fill=BELLY, outline=LINE, width=w)
for cx, cy in [(175, 265), (225, 265), (200, 305)]:
    draw.arc(box(cx - 16, cy - 10, cx + 16, cy + 14), 20, 160, fill=LINE, width=4 * S)
# Face disc and eyes.
draw.ellipse(box(110, 100, 200, 205), fill=FACE, outline=LINE, width=w)
draw.ellipse(box(200, 100, 290, 205), fill=FACE, outline=LINE, width=w)
for cx in (155, 245):
    draw.ellipse(box(cx - 30, 122, cx + 30, 182), fill=EYE, outline=LINE, width=w)
    draw.ellipse(box(cx - 17, 135, cx + 17, 169), fill=IRIS)
    draw.ellipse(box(cx - 9, 143, cx + 9, 161), fill=LINE)
    draw.ellipse(box(cx - 2, 141, cx + 6, 149), fill=EYE)
# Beak.
draw.polygon(poly([(184, 196), (216, 196), (200, 232)]), fill=BEAK, outline=LINE, width=w)

out = image.resize((W, H), Image.LANCZOS)
ImageDraw.Draw(out).text((W // 2, 412), "HOOT", fill=LINE, anchor="mm", font=ImageFont.load_default(size=26))
out.save(sys.argv[1] if len(sys.argv) > 1 else "owl.png")
