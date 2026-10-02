"""Build the Chrome Web Store upload zip for Calm Sky.

The zip contains only what Chrome needs: manifest.json and logo/logo.png.
The finished zip is written to dist/ inside the project and copied to the
default upload folder next to the project root. All copying is done in Python
so the non-ASCII project path never passes through a shell (the shell would
decode it as GBK and silently do nothing).

Run from the project root:  python3 scripts/package-zip.py
"""

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
# <vibe coding>/Chrome-themes/<theme> -> the default upload folder is two up
DEFAULT_OUT = ROOT.parent.parent
INCLUDE = ["manifest.json", "logo/logo.png"]


def main():
    if DEFAULT_OUT.name != "vibe coding":
        raise SystemExit(f"unexpected default output folder: {DEFAULT_OUT}")
    version = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["version"]
    name = f"calm-sky-theme-{version}"
    DIST.mkdir(parents=True, exist_ok=True)
    out = DIST / f"{name}.zip"

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in INCLUDE:
            src = ROOT / rel
            if not src.exists():
                raise SystemExit(f"missing required file: {rel}")
            z.write(src, rel)

    copy = DEFAULT_OUT / out.name
    shutil.copyfile(out, copy)

    for path in (out, copy):
        print(f"{path}  {path.stat().st_size} bytes")
    with zipfile.ZipFile(out) as z:
        print("contents:", ", ".join(z.namelist()))


if __name__ == "__main__":
    main()
