"""Calm Sky Theme - logo candidate generator (code-drawn, PIL).

Six logo concepts for the Calm Sky theme, drawn on a 1024px master and
exported two ways:

  * mark - transparent, frameless (the shape itself, for README / promo use)
  * tile - the same mark in white on a sky-blue rounded tile (how it looks as
           the Chrome Web Store / chrome://extensions icon)

Every colour is derived from manifest.json (single source of truth); nothing
is hardcoded twice. White-on-tile contrast is asserted (>= 3:1, the WCAG
non-text contrast floor for graphical objects).

Run from the PROJECT ROOT (all paths inside are relative, so PIL never has to
deal with this repo's non-ASCII absolute path - dodges the intermittent
OSError 22 on img.save()):

    python3 scripts/generate-logo-candidates.py
"""

import json
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

S = 1024                      # master canvas, downscaled on export
OUT_DIR = "store-assets/icon-candidates"
SIZES = (512, 128)            # exported sizes (128 is the Chrome theme icon)


# --------------------------------------------------------------------------- #
# palette (from manifest.json)
# --------------------------------------------------------------------------- #
def load_palette():
    with open("manifest.json", "r", encoding="utf-8") as fh:
        colors = json.load(fh)["theme"]["colors"]

    def c(key, fallback):
        return tuple(colors.get(key, fallback))[:3]

    return {
        "ink": c("tab_text", (32, 52, 65)),
        "slate": c("tab_background_text", (75, 91, 102)),
        "sky": c("frame", (147, 191, 220)),          # the theme's sky blue
        "sky_deep": c("frame_incognito", (124, 177, 213)),
        "mist": c("background_tab", (204, 222, 231)),
        "paper": c("toolbar", (229, 234, 239)),
        "snow": c("ntp_background", (215, 232, 236)),
    }


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


def rel_lum(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def contrast(c1, c2):
    l1, l2 = rel_lum(c1), rel_lum(c2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def build_palette():
    p = load_palette()
    ink, sky, sky_deep, paper = p["ink"], p["sky"], p["sky_deep"], p["paper"]
    return {
        # tile (the store icon): deep enough that the white mark clears 3:1
        "tile_top": mix(sky_deep, ink, 0.30),
        "tile_bottom": mix(sky_deep, ink, 0.55),
        # frameless mark drawn on light surfaces (deep > mid > light)
        "deep": mix(sky, ink, 0.42),
        "mid": mix(sky, ink, 0.18),
        "soft": mix(sky, paper, 0.10),
        "pale": mix(sky, (255, 255, 255), 0.62),
        "ink": ink,
        "slate": p["slate"],
        "paper": paper,
        "snow": p["snow"],
        "white": (255, 255, 255),
    }


PAL = build_palette()
GLOW_ALPHA = 24               # soft haze inside the tile, behind the mark
TILE_RADIUS = 0.219           # Chrome-ish rounded square

MONO = None                   # when set, every mark element uses this colour


# --------------------------------------------------------------------------- #
# fonts
# --------------------------------------------------------------------------- #
def font(size, bold=False):
    names = ("arialbd.ttf", "arial.ttf") if bold else ("arial.ttf",)
    for name in names:
        for path in (f"C:/Windows/Fonts/{name}", name):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                                    # very old Pillow
        return ImageFont.load_default()


# --------------------------------------------------------------------------- #
# mask helpers - shapes are drawn as 8-bit masks, then coloured
# --------------------------------------------------------------------------- #
def blank():
    return Image.new("L", (S, S), 0)


def apply_alpha(mask, alpha):
    return mask.point(lambda v: int(round(v * alpha / 255.0)))


def vramp(a_top, a_bot):
    """Vertical alpha ramp: a_top at the top edge, a_bot at the bottom."""
    g = Image.linear_gradient("L").resize((S, S), Image.BILINEAR)
    return g.point(lambda v: int(round(a_top + (a_bot - a_top) * v / 255)))


def paint(img, mask, color, blur=0, fades=()):
    """Multiply the mask with optional fades, blur it, composite `color`."""
    m = mask
    for f in fades:
        m = ImageChops.multiply(m, f)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGBA", (S, S), (MONO or color) + (255,))
    layer.putalpha(m)
    img.alpha_composite(layer)


def disc(cx, cy, r, fill=255):
    m = blank()
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    return m


def half_disc(cx, cy, r):
    """Upper half of a disc - a sun resting on a horizon."""
    cut = blank()
    ImageDraw.Draw(cut).rectangle([0, cy, S, S], fill=255)
    return ImageChops.subtract(disc(cx, cy, r), cut)


def dilate(mask, px):
    return mask.filter(ImageFilter.MaxFilter(px * 2 + 1))


def rot_pt(p, center, deg):
    """Rotate a point the same way Image.rotate() rotates the canvas."""
    th = math.radians(deg)
    dx, dy = p[0] - center[0], p[1] - center[1]
    return (center[0] + dx * math.cos(th) + dy * math.sin(th),
            center[1] - dx * math.sin(th) + dy * math.cos(th))


def cloud(cx, cy, w, h):
    """Classic puffy cloud: a rounded base bar plus four lobes."""
    m = blank()
    d = ImageDraw.Draw(m)
    bw, bh = w * 0.80, h * 0.44
    d.rounded_rectangle([cx - bw / 2, cy + h * 0.50 - bh, cx + bw / 2, cy + h * 0.50],
                        radius=bh / 2, fill=255)
    for dx, dy, r in ((-0.020, -0.080, 0.340),
                      (-0.260, 0.020, 0.270),
                      (0.275, 0.070, 0.240)):
        rr = r * h
        ImageDraw.Draw(m).ellipse([cx + dx * w - rr, cy + dy * h - rr,
                                   cx + dx * w + rr, cy + dy * h + rr], fill=255)
    return m


def rot_band(cx, cy, w, h, angle):
    """Rounded bar rotated by `angle` degrees - drifting air, not a burger."""
    pad = int(h) + 16
    tmp = Image.new("L", (int(w) + 2 * pad, int(h) + 2 * pad), 0)
    ImageDraw.Draw(tmp).rounded_rectangle([pad, pad, pad + w, pad + h],
                                          radius=int(h / 2), fill=255)
    tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=False)
    out = blank()
    out.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)
    return out


def ribbon(curve, y_from, y_to, thickness, steps=180):
    """Filled band following x = curve(y) - clean edges, no line joints."""
    top, bottom = [], []
    for i in range(steps + 1):
        y = y_from + (y_to - y_from) * i / steps
        t = thickness(y)
        x = curve(y)
        top.append((x - t / 2, y))
        bottom.insert(0, (x + t / 2, y))
    m = blank()
    ImageDraw.Draw(m).polygon(top + bottom, fill=255)
    return m


def gull():
    """One gliding gull: two crescents that meet in a soft notch."""
    cx, y_mid, y_tip = S / 2, 372.0, 686.0
    half = 386.0
    m = blank()
    top, bottom = [], []
    for i in range(0, 361, 4):
        d = min(abs(i - 180) / 180.0, 1.0)
        y = y_mid + (y_tip - y_mid) * (d ** 2.1)
        t = 104.0 * math.sin(math.pi * d) ** 0.62
        x = cx - half + i * (half / 180.0)
        top.append((x, y))
        bottom.insert(0, (x, y + t))
    ImageDraw.Draw(m).polygon(top + bottom, fill=255)
    return m


# --------------------------------------------------------------------------- #
# the six concepts (each returns a master RGBA image)
# --------------------------------------------------------------------------- #
def opt_cloud():
    """01 - one soft cloud, plus a faint distant cloud for depth."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    far = cloud(0.365 * S, 0.290 * S, 0.300 * S, 0.165 * S)
    paint(img, apply_alpha(far, 84), PAL["mid"])
    paint(img, cloud(0.500 * S, 0.545 * S, 0.660 * S, 0.360 * S), PAL["deep"],
          fades=(vramp(255, 190),))
    return img


def opt_sun_cloud():
    """02 - sun peeking out behind a calm cloud."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sun = disc(0.635 * S, 0.360 * S, 0.148 * S)
    body = cloud(0.465 * S, 0.590 * S, 0.620 * S, 0.340 * S)
    paint(img, ImageChops.subtract(sun, dilate(body, 15)), PAL["pale"])
    paint(img, body, PAL["deep"], fades=(vramp(255, 205),))
    return img


def opt_kite():
    """03 - a kite with a gentle tail: light, unhurried."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    top_p, right_p, bot_p, left_p = ((512, 190), (704, 418), (512, 632), (320, 418))
    upper = blank()
    ImageDraw.Draw(upper).polygon([top_p, right_p, bot_p], fill=255)
    lower = blank()
    ImageDraw.Draw(lower).polygon([top_p, left_p, bot_p], fill=255)
    body = ImageChops.lighter(upper, lower)
    spine = blank()
    ImageDraw.Draw(spine).line([top_p, bot_p], fill=255, width=16)
    body = ImageChops.subtract(body, ImageChops.multiply(spine, body))
    paint(img, body, PAL["deep"], fades=(vramp(255, 200),))

    def curve(y):
        u = (y - 632) / 316.0
        return 512 - 170 * u * u - 40 * u

    tail = ribbon(curve, 628, 944, lambda y: 22 - 13 * (y - 628) / 316.0)
    paint(img, tail, PAL["mid"])
    for u, r in ((0.38, 26), (0.66, 21), (0.90, 15)):
        y = 628 + 316 * u
        paint(img, disc(curve(y), y, r), PAL["mid"])
    return img


def opt_plane():
    """04 - a paper plane gliding up-right, with a shrinking trail."""
    sx, sy = 0.74, 0.93
    tail_top = (130 * sx, 206 * sy)
    nose = (880 * sx, 512 * sy)
    notch = (665 * sx, 512 * sy)
    tail_bot = (130 * sx, 818 * sy)

    upper = blank()
    ImageDraw.Draw(upper).polygon([tail_top, nose, notch], fill=255)
    lower = blank()
    ImageDraw.Draw(lower).polygon([notch, nose, tail_bot], fill=255)
    plane = ImageChops.lighter(upper, lower)

    crease = blank()
    ImageDraw.Draw(crease).line([notch, nose], fill=255, width=24)
    plane = ImageChops.subtract(plane, ImageChops.multiply(crease, plane))

    angle, margin = 14.0, 72.0
    c = (S / 2, S / 2)
    plane = plane.rotate(angle, resample=Image.BICUBIC, center=c)

    # park the rotated plane in the top-right, leaving the lower-left for the trail
    bbox = plane.getbbox()
    dx, dy = (S - margin) - bbox[2], margin - bbox[1]
    moved = blank()
    moved.paste(plane, (int(dx), int(dy)), plane)
    assert moved.getbbox()[3] <= S - 24, "rotated plane leaves the canvas"

    nose_r = rot_pt(nose, c, angle)
    rear_r = rot_pt(tail_bot, c, angle)
    rear = (rear_r[0] + dx, rear_r[1] + dy)
    vx, vy = rear[0] - (nose_r[0] + dx), rear[1] - (nose_r[1] + dy)
    n = math.hypot(vx, vy)
    ux, uy = vx / n, vy / n

    # how far the trail can run before it reaches the safe margin
    edge = 96.0
    cand = [t for t in (((edge - rear[0]) / ux if ux < -1e-6 else 1e9),
                        ((S - edge - rear[0]) / ux if ux > 1e-6 else 1e9),
                        ((edge - rear[1]) / uy if uy < -1e-6 else 1e9),
                        ((S - edge - rear[1]) / uy if uy > 1e-6 else 1e9)) if t > 0]
    span = max(0.0, min(cand))

    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    paint(img, moved, PAL["deep"], fades=(vramp(215, 255),))
    for frac, r in ((0.30, 25), (0.58, 18), (0.86, 12)):
        cx, cy = rear[0] + ux * span * frac, rear[1] + uy * span * frac
        assert r + 24 < cx < S - r - 24 and r + 24 < cy < S - r - 24, "plane trail hits the edge"
        paint(img, disc(cx, cy, r), PAL["mid"])
    return img


def opt_sunrise():
    """05 - a sun resting on a still horizon, one cloud drifting past."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    base = 0.588 * S
    sun = half_disc(0.510 * S, base, 0.205 * S)
    puff = cloud(0.270 * S, 0.395 * S, 0.245 * S, 0.132 * S)
    paint(img, ImageChops.subtract(sun, dilate(puff, 13)), PAL["pale"])
    paint(img, puff, PAL["deep"], fades=(vramp(255, 205),))
    paint(img, rot_band(0.500 * S, base + 16, 0.660 * S, 0.031 * S, 0), PAL["deep"])
    return img


def opt_gull():
    """06 - one gull gliding: the calmest thing in the sky."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    paint(img, gull(), PAL["deep"], fades=(vramp(255, 205),))
    return img


OPTIONS = (
    ("01-cloud", "CLOUD", "one soft cloud", opt_cloud),
    ("02-sun-cloud", "SUN & CLOUD", "sun behind a calm cloud", opt_sun_cloud),
    ("03-kite", "KITE", "kite with a gentle tail", opt_kite),
    ("04-paper-plane", "PAPER PLANE", "gliding up-right", opt_plane),
    ("05-sunrise", "SUNRISE", "sun on a still horizon", opt_sunrise),
    ("06-gull", "GULL", "one gull, wide wings", opt_gull),
)


def render(fn, mono=None):
    global MONO
    MONO = mono
    try:
        return fn()
    finally:
        MONO = None


# --------------------------------------------------------------------------- #
# the tile (what the store icon actually looks like)
# --------------------------------------------------------------------------- #
def tile(art, size=S):
    radius = int(size * TILE_RADIUS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)

    top = Image.new("RGB", (size, size), PAL["tile_top"])
    bottom = Image.new("RGB", (size, size), PAL["tile_bottom"])
    ramp = Image.linear_gradient("L").resize((size, size), Image.BILINEAR)
    body = Image.composite(bottom, top, ramp).convert("RGBA")

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(body, (0, 0), mask)

    glow = Image.composite(Image.new("L", (size, size), GLOW_ALPHA),
                           Image.new("L", (size, size), 0),
                           Image.linear_gradient("L").resize((size, size), Image.BILINEAR))
    out.alpha_composite(_layer((size, size), (255, 255, 255), ImageChops.multiply(glow, mask)))

    out.alpha_composite(art.resize((size, size), Image.LANCZOS))
    return out


def _layer(size, color, mask):
    lay = Image.new("RGBA", size, color + (255,))
    lay.putalpha(mask)
    return lay


# --------------------------------------------------------------------------- #
# contact sheet
# --------------------------------------------------------------------------- #
def contact_sheet(marks, tiles):
    margin, gap, head = 48, 32, 92
    cols, rows, cell_w, cell_h = 3, 2, 352, 460
    sheet_w = margin * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = margin * 2 + head + rows * cell_h + (rows - 1) * gap
    assert sheet_w == 1216 and sheet_h == 1140, (sheet_w, sheet_h)

    sheet = Image.new("RGB", (sheet_w, sheet_h), (236, 237, 238))
    d = ImageDraw.Draw(sheet)
    d.text((margin, margin - 6), "CALM SKY - LOGO OPTIONS", font=font(40, True), fill=PAL["ink"])
    d.text((margin, margin + 46),
           "tile = store icon (white on sky) - mark = frameless - colours from manifest.json",
           font=font(22), fill=PAL["slate"])

    tile_px, mark_px, sm_px = 196, 104, 44
    grid_top = margin + head
    for idx, (slug, name, note, _fn) in enumerate(OPTIONS):
        col, row = idx % cols, idx // cols
        x = margin + col * (cell_w + gap)
        y = grid_top + row * (cell_h + gap)
        assert x + cell_w <= sheet_w - margin, "column overflows the right margin"
        assert y + cell_h <= sheet_h - margin, "row overflows the bottom margin"

        d.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], fill=PAL["snow"],
                    outline=(214, 216, 218))
        d.text((x + 22, y + 14), f"{idx + 1:02d}", font=font(26, True), fill=PAL["ink"])
        d.text((x + 64, y + 18), name, font=font(23), fill=PAL["slate"])
        d.text((x + 22, y + 52), note, font=font(19), fill=(146, 150, 154))

        big = tiles[idx].resize((tile_px, tile_px), Image.LANCZOS)
        sheet.paste(big, (x + (cell_w - tile_px) // 2, y + 78), big.getchannel("A"))

        mark = marks[idx].resize((mark_px, mark_px), Image.LANCZOS)
        sheet.paste(mark, (x + 30, y + 318), mark.getchannel("A"))
        small = tiles[idx].resize((sm_px, sm_px), Image.LANCZOS)
        sheet.paste(small, (x + 168, y + 336), small.getchannel("A"))
        tiny = tiles[idx].resize((22, 22), Image.LANCZOS)
        sheet.paste(tiny, (x + 238, y + 347), tiny.getchannel("A"))

        d.text((x + 30, y + 430), "mark", font=font(17), fill=(146, 150, 154))
        d.text((x + 168, y + 392), "44 / 22 px", font=font(16), fill=(146, 150, 154))
        assert y + cell_h - 12 >= y + 430 + 17, "caption does not fit the cell"
    return sheet


# --------------------------------------------------------------------------- #
def main():
    if not os.path.exists("manifest.json"):
        raise SystemExit("run this script from the project root (manifest.json not found)")

    lightest = mix(PAL["tile_top"], (255, 255, 255), GLOW_ALPHA / 255.0)
    ratio = contrast(lightest, (255, 255, 255))
    assert ratio >= 3.0, f"white mark vs lightest tile pixel = {ratio:.2f}:1 (< 3:1)"

    os.makedirs(OUT_DIR, exist_ok=True)
    marks, tiles = [], []
    for slug, name, _note, fn in OPTIONS:
        mark = render(fn)
        tile_img = tile(render(fn, mono=(255, 255, 255)))
        assert mark.size == (S, S) and tile_img.size == (S, S)
        marks.append(mark)
        tiles.append(tile_img)

        for size in SIZES:
            mark.resize((size, size), Image.LANCZOS).save(f"{OUT_DIR}/option-{slug}-mark-{size}.png")
            tile_img.resize((size, size), Image.LANCZOS).save(f"{OUT_DIR}/option-{slug}-tile-{size}.png")
        print(f"  {slug:<16} {name}")

    contact_sheet(marks, tiles).save(f"{OUT_DIR}/contact-sheet.png")
    print(f"white-on-tile contrast {ratio:.2f}:1  ->  {OUT_DIR}/contact-sheet.png")


if __name__ == "__main__":
    main()
