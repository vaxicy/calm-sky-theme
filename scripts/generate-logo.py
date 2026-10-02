"""Calm Sky Theme - the final store icon.

The chosen mark is SUNRISE: a sun resting on a still horizon with one cloud
drifting past, in white on a sky-blue rounded tile.

Chrome themes only need 128 px, and the file is called plain `logo.png` so it is
easy to find when uploading to the Chrome Web Store.

Run from the project root:  python3 scripts/generate-logo.py
Output: logo/logo.png (128x128)
"""

from pathlib import Path

from logo_mark import load_colors, sunrise_tile

ICON = 128
OUT = Path("logo") / "logo.png"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    icon = sunrise_tile(ICON, load_colors())
    icon.save(OUT, "PNG")
    print("wrote", OUT, icon.size, icon.mode)


if __name__ == "__main__":
    main()
