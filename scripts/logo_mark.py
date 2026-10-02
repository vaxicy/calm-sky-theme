"""Calm Sky Theme - the SUNRISE mark, drawn with code (PIL).

Single source for the store icon and the promo tiles: a sun resting on a still
horizon with one cloud drifting past, in white on a sky-blue rounded tile - the
same tile shape the rest of the theme series uses, so the icon reads on the
white Chrome Web Store page.

Every colour is derived from manifest.json; nothing is hardcoded twice.

    from logo_mark import sunrise_tile, load_colors
    sunrise_tile(128)      # -> RGBA image, 128x128
"""

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent

S = 1024                      # master canvas, downscaled on export
GLOW_ALPHA = 24               # soft haze inside the tile, behind the mark
TILE_RADIUS = 0.219           # Chrome-ish rounded square


def load_colors():
    data = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    return data["theme"]["colors"]


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def palette(colors=None):
    c = colors or load_colors()
    sky = tuple(c["frame"])
    sky_deep = tuple(c["frame_incognito"])
    ink = tuple(c["tab_text"])
    return {
        "tile_top": mix(sky_deep, ink, 0.30),
        "tile_bottom": mix(sky_deep, ink, 0.55),
        "deep": mix(sky, ink, 0.42),
        "mid": mix(sky, ink, 0.18),
        "pale": mix(sky, (255, 255, 255), 0.62),
    }


# --------------------------------------------------------------------------- #
# mask helpers
# --------------------------------------------------------------------------- #
def blank():
    return Image.new("L", (S, S), 0)


def disc(cx, cy, r, fill=255):
    m = blank()
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    return m


def half_disc(cx, cy, r):
    """Upper half of a disc - a sun resting on a horizon."""
    cut = blank()
    ImageDraw.Draw(cut).rectangle([0, cy, S, S], fill=255)
    return ImageChops.subtract(disc(cx, cy, r), cut)


def cloud(cx, cy, w, h):
    """Classic puffy cloud: a rounded base bar plus three lobes."""
    m = blank()
    d = ImageDraw.Draw(m)
    bw, bh = w * 0.80, h * 0.44
    d.rounded_rectangle([cx - bw / 2, cy + h * 0.50 - bh, cx + bw / 2, cy + h * 0.50],
                        radius=bh / 2, fill=255)
    for dx, dy, r in ((-0.020, -0.080, 0.340),
                      (-0.260, 0.020, 0.270),
                      (0.275, 0.070, 0.240)):
        rr = r * h
        d.ellipse([cx + dx * w - rr, cy + dy * h - rr,
                   cx + dx * w + rr, cy + dy * h + rr], fill=255)
    return m


def rot_band(cx, cy, w, h, angle):
    """Rounded bar rotated by `angle` degrees."""
    pad = int(h) + 16
    tmp = Image.new("L", (int(w) + 2 * pad, int(h) + 2 * pad), 0)
    ImageDraw.Draw(tmp).rounded_rectangle([pad, pad, pad + w, pad + h],
                                          radius=int(h / 2), fill=255)
    tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=False)
    out = blank()
    out.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)
    return out


def dilate(mask, px):
    return mask.filter(ImageFilter.MaxFilter(px * 2 + 1))


def vramp(a_top, a_bot):
    """Vertical alpha ramp: a_top at the top edge, a_bot at the bottom."""
    g = Image.linear_gradient("L").resize((S, S), Image.BILINEAR)
    return g.point(lambda v: int(round(a_top + (a_bot - a_top) * v / 255)))


def paint(img, mask, color, blur=0, fades=()):
    m = mask
    for f in fades:
        m = ImageChops.multiply(m, f)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGBA", (S, S), tuple(color) + (255,))
    layer.putalpha(m)
    img.alpha_composite(layer)


def layer(size, color, mask):
    lay = Image.new("RGBA", size, tuple(color) + (255,))
    lay.putalpha(mask)
    return lay


# --------------------------------------------------------------------------- #
# the mark
# --------------------------------------------------------------------------- #
def sunrise_mark(colors=None, mono=None):
    """The SUNRISE mark: white (mono) or palette-coloured, on transparency."""
    pal = palette(colors)
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    base = 0.588 * S
    sun = half_disc(0.510 * S, base, 0.205 * S)
    puff = cloud(0.270 * S, 0.395 * S, 0.245 * S, 0.132 * S)
    paint(img, ImageChops.subtract(sun, dilate(puff, 13)), mono or pal["pale"])
    paint(img, puff, mono or pal["deep"], fades=(vramp(255, 205),))
    paint(img, rot_band(0.500 * S, base + 16, 0.660 * S, 0.031 * S, 0), mono or pal["deep"])
    return img


def tile(art, size, colors=None):
    """Sky-blue rounded tile with the mark on it - how the icon looks in store."""
    pal = palette(colors)
    radius = int(size * TILE_RADIUS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)

    top = Image.new("RGB", (size, size), pal["tile_top"])
    bottom = Image.new("RGB", (size, size), pal["tile_bottom"])
    ramp = Image.linear_gradient("L").resize((size, size), Image.BILINEAR)
    body = Image.composite(bottom, top, ramp).convert("RGBA")

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(body, (0, 0), mask)

    glow = Image.composite(Image.new("L", (size, size), GLOW_ALPHA),
                           Image.new("L", (size, size), 0),
                           Image.linear_gradient("L").resize((size, size), Image.BILINEAR))
    out.alpha_composite(layer((size, size), (255, 255, 255), ImageChops.multiply(glow, mask)))
    out.alpha_composite(art.resize((size, size), Image.LANCZOS))
    return out


def sunrise_tile(size, colors=None):
    """The final icon: sky tile + white sunrise. One call, any size."""
    return tile(sunrise_mark(colors, mono=(255, 255, 255)), size, colors)
