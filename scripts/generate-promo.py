"""Calm Sky Theme - store promo tiles + the short store description.

Code-drawn with PIL, colours read from manifest.json (single source of truth),
the SUNRISE mark reused from logo_mark.py. English only, as store assets must be.

Outputs (relative ASCII paths):
  store-assets/promo/440x280.png
  store-assets/promo/1400x560.png
  store-assets/store-description.txt

Run from the project root:  python3 scripts/generate-promo.py
"""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from logo_mark import load_colors, mix, sunrise_tile

PROMO = Path("store-assets") / "promo"
DESC = Path("store-assets") / "store-description.txt"
SS = 2  # supersample factor back to 1x
FONT_DIR = "C:/Windows/Fonts"


def font(name, size):
    try:
        return ImageFont.truetype(f"{FONT_DIR}/{name}", size * SS)
    except OSError:
        return ImageFont.load_default()


def grad(w, h, c1, c2, angle=118):
    n = 96
    sm = Image.new("RGB", (n, n))
    px = sm.load()
    ax, ay = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    span = abs(ax) + abs(ay)
    for y in range(n):
        for x in range(n):
            px[x, y] = mix(c1, c2, ((x / (n - 1)) * ax + (y / (n - 1)) * ay) / span)
    return sm.resize((w, h), Image.BICUBIC)


def glow(img, cx, cy, r, color, alpha, blur):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([cx - r, cy - r, cx + r, cy + r],
                                fill=tuple(color) + (alpha,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))


def swatch(img, x, y, size, radius, color, label=None, txt=None):
    # No outline on purpose: PIL writes RGBA outline pixels straight into the
    # layer instead of blending them, which turns into a hard dark ring once the
    # image is flattened to RGB.
    ImageDraw.Draw(img).rounded_rectangle(
        [x, y, x + size, y + size], radius=radius, fill=tuple(color))
    if label:
        txt.text((x + size + 16 * SS, y + (size - 15 * SS) / 2 - 2 * SS),
                 label, font=txt, fill=(99, 99, 99))


def promo_tile(c):
    W, H = 440, 280
    img = Image.new("RGBA", (W * SS, H * SS), (255, 255, 255, 255))
    img.paste(grad(W * SS, H * SS, c["ntp_background"],
                   mix(c["frame"], c["ntp_background"], 0.30)))
    glow(img, 372 * SS, 42 * SS, 210 * SS, c["frame"], 120, 96 * SS)

    ink, muted = tuple(c["tab_text"]), tuple(c["toolbar_button_icon"])
    img.alpha_composite(sunrise_tile(104, c), (40 * SS, 56 * SS))

    d = ImageDraw.Draw(img)
    d.text((166 * SS, 70 * SS), "Calm Sky", font=font("arialbd.ttf", 40), fill=ink)
    d.text((170 * SS, 128 * SS), "Chrome Theme", font=font("arial.ttf", 19), fill=muted)

    x = 170
    for col in (c["frame"], c["background_tab"], c["toolbar"], c["tab_text"]):
        swatch(img, x * SS, 174 * SS, 32 * SS, 10 * SS, col)
        x += 46
    assert x - 14 <= W - 32, "promo swatch row overflows"

    out = PROMO / "440x280.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.resize((W, H), Image.LANCZOS).convert("RGB").save(out, "PNG")
    print("wrote", out)


def marquee(c):
    W, H = 1400, 560
    img = Image.new("RGBA", (W * SS, H * SS), (255, 255, 255, 255))
    img.paste(grad(W * SS, H * SS, c["ntp_background"],
                   mix(c["frame"], c["ntp_background"], 0.26)))
    glow(img, 1160 * SS, 110 * SS, 320 * SS, c["frame"], 96, 150 * SS)

    margin, right = 64, W - 64
    ink, muted = tuple(c["tab_text"]), tuple(c["toolbar_button_icon"])

    img.alpha_composite(sunrise_tile(220, c), (margin * SS, 142 * SS))

    d = ImageDraw.Draw(img)
    d.text(((margin + 264) * SS, 158 * SS), "Calm Sky",
           font=font("arialbd.ttf", 86), fill=ink)
    d.text(((margin + 268) * SS, 280 * SS), "Chrome Theme",
           font=font("arial.ttf", 28), fill=muted)
    d.text(((margin + 268) * SS, 322 * SS), "Airy blues for calm, unhurried browsing",
           font=font("arial.ttf", 23), fill=muted)

    x = margin + 268
    for col in (c["frame"], c["background_tab"], c["toolbar"], c["tab_text"]):
        swatch(img, x * SS, 396 * SS, 84 * SS, 22 * SS, col)
        x += 102
    assert x - 18 <= right, "marquee swatch row overflows"

    # palette card, right-aligned to the same right baseline as everything else
    card_w, card_h = 430, 336
    cx, cy = right - card_w, 142
    d.rounded_rectangle([cx * SS, cy * SS, right * SS, (cy + card_h) * SS],
                        radius=30 * SS, fill=(255, 255, 255, 242))
    d.text(((cx + 32) * SS, (cy + 26) * SS), "Palette",
           font=font("arialbd.ttf", 22), fill=ink)
    rows = [("Sky", c["frame"]), ("Tab", c["background_tab"]),
            ("Paper", c["toolbar"]), ("Haze", c["ntp_background"])]
    f_hex = font("arial.ttf", 16)
    y = cy + 78
    for label, col in rows:
        swatch(img, (cx + 32) * SS, y * SS, 36 * SS, 12 * SS, col)
        d.text(((cx + 84) * SS, (y + 2) * SS), label, font=f_hex, fill=ink)
        d.text(((cx + 250) * SS, (y + 2) * SS), "#%02X%02X%02X" % tuple(col),
               font=f_hex, fill=muted)
        y += 58
    assert y - 22 <= cy + card_h - 20, "palette rows overflow the card"
    assert cy + card_h <= H - 12, "palette card breaks the bottom margin"

    out = PROMO / "1400x560.png"
    img.resize((W, H), Image.LANCZOS).convert("RGB").save(out, "PNG")
    print("wrote", out)


DESCRIPTION = """Calm Sky is a light, airy Chrome theme for quiet, unhurried browsing. A soft \
sky-blue window frame wraps pale blue-grey tabs, a near-white toolbar sits under them, and \
the new-tab page opens onto a calm, washed-blue expanse. Deep slate text keeps every label \
and icon crisp on all of those light surfaces. The design is flat colour throughout - no \
wallpaper, no patterns, no gradients - and the icon distills it into a sun resting on a \
still horizon."""


def main():
    c = load_colors()
    promo_tile(c)
    marquee(c)
    DESC.parent.mkdir(parents=True, exist_ok=True)
    DESC.write_text(DESCRIPTION + "\n", encoding="utf-8")
    print("wrote", DESC)


if __name__ == "__main__":
    main()
