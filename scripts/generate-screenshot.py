"""Calm Sky Theme - 1280x800 store screenshots (headless browser render).

Screenshot 1 is a faithful mock-up of the user's real Chrome capture
(1080x643) with this theme installed: same layer heights, same proportions
(scaled by 1280/1080) and the same colours.

Theme-controlled surfaces come from manifest.json. Browser-owned details are
the values sampled from that real capture:

  Google NTP wordmark    #7BB3C0   (ntp_logo_alternate: 1 -> tinted wordmark)
  caption-button strip   #BFCCDA   (the lighter strip that carries - [] x)
  caption glyphs         #626970
  omnibox placeholder    #70757A
  toolbar icon grey      #5F6368
  Customize pill         #202124   (dark pill, light text, blue pencil #89B3F6)
  shortcut tile discs    #9AC5CF   (the tinted disc behind each favicon)
  shortcut labels        #5F7381

Layer heights measured on that capture: tab strip 29, toolbar 33, bookmark bar
30 -> 34 / 39 / 36 at 1280 wide. The capture had a focused omnibox with a caret;
the mock-up shows the steady unfocused state instead, which is what a store shot
wants.

All copy is English (store assets must be English).

Run from the project root:  python3 scripts/generate-screenshot.py
Outputs: store-assets/screenshots/en/screenshot-{1-browser,2-introduction}.png
         store-assets/references/screenshot-*.{html,png}
"""

import json
import shutil
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = Path("store-assets") / "screenshots" / "en"
REFS = Path("store-assets") / "references"
W, H = 1280, 800

# --- geometry measured on the real capture, scaled by 1280/1080 -------------
TAB_STRIP_H = 34
TOOLBAR_H = 39
BOOKMARK_H = 36
NTP_TOP = TAB_STRIP_H + TOOLBAR_H + BOOKMARK_H
OMNIBOX_L, OMNIBOX_W, OMNIBOX_H = 152, 769, 33
WORDMARK_TOP, WORDMARK_SIZE = 111, 78       # relative to the NTP strip
SEARCH_TOP, SEARCH_L, SEARCH_W, SEARCH_H = 231, 325, 630, 45
SHORTCUT_TOP = 293                          # relative to the NTP strip
TAB_H, TAB_TOP, TAB_GAP = 25, 4, 13
CAPTION_W = 127

# --- browser-owned colours sampled from the real capture --------------------
WORDMARK = "#7BB3C0"
CAPTION_BG = "#BFCCDA"
CAPTION_DIVIDER = "#B3C1D1"
CAPTION_GLYPH = "#626970"
PLACEHOLDER = "#70757A"
ICON_GRAY = "#5F6368"
LENS_BLUE = "#4285F4"
PILL_BG = "#202124"
PILL_TEXT = "#FFFFFF"
PILL_PENCIL = "#89B3F6"
SHORTCUT_DISC = "#9AC5CF"
LABEL = "#5F7381"

# title, width, favicon kind - the user's real tabs, in English
TABS = (
    ("Excel for Data Analy", 195, "sheet"),
    ("ThemeBake \u2014 Create", 160, "theme"),
    ("Chrome Web Store", 160, "store"),
    ("Extensions", 160, "ext"),
    ("New Tab", 160, "globe"),
    ("New Tab", 160, "globe"),          # active
)
ACTIVE = 5
BOOKMARKS = ("Tools", "Design", "AI", "UI", "Google", "Nav", "Temp", "API", "Dev")


def hexof(c):
    return "#%02X%02X%02X" % tuple(c)


def favicon(kind, frame):
    """14px tab favicon / 26px shortcut icon, drawn as inline SVG."""
    return {
        "sheet": f'<svg viewBox="0 0 16 16" width="100%" height="100%">'
                 f'<rect width="16" height="16" rx="3" fill="#217346"/>'
                 f'<path d="M5 5h6M5 8h6M5 11h6M8 5v6" stroke="#fff" '
                 f'stroke-width="1.2" fill="none"/></svg>',
        "theme": f'<svg viewBox="0 0 16 16" width="100%" height="100%">'
                 f'<rect width="16" height="16" rx="3" fill="#6C5CE7"/>'
                 f'<path d="M8 3.6l1.2 2.8 2.8 1.2-2.8 1.2L8 11.6 6.8 8.8 4 7.6l2.8-1.2z" '
                 f'fill="#fff"/></svg>',
        "store": f'<svg viewBox="0 0 16 16" width="100%" height="100%">'
                 f'<circle cx="8" cy="8" r="6.4" fill="#fff"/>'
                 f'<path fill="#EA4335" d="M8 1.6A6.4 6.4 0 0 1 13.5 4.8H8z"/>'
                 f'<path fill="#34A853" d="M13.5 4.8A6.4 6.4 0 0 1 8 14.4V8z"/>'
                 f'<path fill="#FBBC05" d="M8 14.4A6.4 6.4 0 0 1 2.5 4.8L8 8z"/>'
                 f'<circle cx="8" cy="8" r="2.7" fill="#4285F4"/>'
                 f'<circle cx="8" cy="8" r="3.7" fill="none" stroke="#fff" stroke-width="1"/></svg>',
        "ext": f'<svg viewBox="0 0 16 16" width="100%" height="100%">'
               f'<rect width="16" height="16" rx="3" fill="#4285F4"/>'
               f'<circle cx="8" cy="8" r="3.4" fill="none" stroke="#fff" stroke-width="1.6"/></svg>',
        "globe": f'<svg viewBox="0 0 16 16" width="100%" height="100%">'
                 f'<rect width="16" height="16" rx="3" fill="#E3EAF0"/>'
                 f'<circle cx="8" cy="8" r="4.6" fill="none" stroke="#7E8F9C" stroke-width="1.1"/>'
                 f'<path d="M3.4 8h9.2M8 3.4c1.6 2.6 1.6 6.6 0 9.2-1.6-2.6-1.6-6.6 0-9.2z" '
                 f'fill="none" stroke="#7E8F9C" stroke-width="1"/></svg>',
        "youtube": f'<svg viewBox="0 0 24 24" width="100%" height="100%">'
                   f'<rect x="1.5" y="5" width="21" height="14" rx="4" fill="#FF0033"/>'
                   f'<path d="M10 9l6 3-6 3z" fill="#fff"/></svg>',
        "plus": f'<svg viewBox="0 0 24 24" width="100%" height="100%" fill="none" '
                f'stroke="{ICON_GRAY}" stroke-width="2.2" stroke-linecap="round">'
                f'<path d="M12 6v12M6 12h12"/></svg>',
    }[kind]


def build_browser(c):
    frame = hexof(c["frame"])
    toolbar = hexof(c["toolbar"])
    inactive = hexof(c["background_tab"])
    ink = hexof(c["tab_text"])
    inactive_text = hexof(c["tab_background_text"])
    toolbar_icon = hexof(c["toolbar_button_icon"])
    omnibox = hexof(c["omnibox_background"])
    ntp = hexof(c["ntp_background"])

    tab_html, x = "", 8
    for i, (title, tw, kind) in enumerate(TABS):
        active = i == ACTIVE
        bg = toolbar if active else inactive
        col = ink if active else inactive_text
        h = TAB_H + 5 if active else TAB_H
        tab_html += f"""
      <div class="tab{' active' if active else ''}"
           style="left:{x}px;width:{tw}px;height:{h}px;background:{bg};color:{col}">
        <span class="favicon">{favicon(kind, frame)}</span>
        <span class="tab-title">{title}</span>
        <svg class="close" viewBox="0 0 16 16" width="10" height="10" stroke="{col}"
             stroke-width="1.6" stroke-linecap="round"><path d="M5 5l6 6M11 5l-6 6"/></svg>
      </div>"""
        x += tw + TAB_GAP
    sliver_x = x + 3

    def tool(d, size=20, color=None):
        return f"""<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none"
           stroke="{color or toolbar_icon}" stroke-width="1.8" stroke-linecap="round"
           stroke-linejoin="round">{d}</svg>"""

    folder = f"""<svg viewBox="0 0 24 24" width="15" height="15" fill="none"
        stroke="{toolbar_icon}" stroke-width="1.8" stroke-linejoin="round">
        <path d="M3 6.5h6l2 2.5h10v9.5H3z"/></svg>"""

    bookmark = "".join(f'<span class="bm">{folder}{name}</span>' for name in BOOKMARKS)

    caption = "".join(
        f"""<div>{glyph}</div>""" for glyph in (
            f'<svg viewBox="0 0 12 12" width="11" height="11" stroke="{CAPTION_GLYPH}" '
            f'stroke-width="1.1"><path d="M1 6h10"/></svg>',
            f'<svg viewBox="0 0 12 12" width="11" height="11" fill="none" '
            f'stroke="{CAPTION_GLYPH}" stroke-width="1.1"><rect x="2" y="2.5" width="8" '
            f'height="7" rx="1"/><path d="M3.5 2.5V1.4h8v7h-1.1"/></svg>',
            f'<svg viewBox="0 0 12 12" width="11" height="11" stroke="{CAPTION_GLYPH}" '
            f'stroke-width="1.2" stroke-linecap="round"><path d="M2.5 2.5l7 7M9.5 2.5l-7 7"/>'
            f'</svg>',
        ))

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:{W}px; height:{H}px; overflow:hidden; background:{frame};
         font-family:'Segoe UI', Arial, sans-serif; }}
  .tabstrip {{ position:absolute; left:0; right:0; top:0; height:{TAB_STRIP_H}px;
              background:{frame}; }}
  .tab {{ position:absolute; top:{TAB_TOP}px; border-radius:9px 9px 0 0;
         display:flex; align-items:center; gap:8px; padding:0 11px; font-size:12.5px; }}
  .tab.active {{ box-shadow:none; }}
  .favicon {{ width:14px; height:14px; border-radius:4px; flex:none; }}
  .tab-title {{ flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
               opacity:.94; }}
  .close {{ flex:none; opacity:.5; }}
  .sliver {{ position:absolute; top:{TAB_TOP}px; height:{TAB_H}px; width:16px;
            border-radius:9px 9px 0 0; background:{inactive}; }}
  .caption {{ position:absolute; right:0; top:0; width:{CAPTION_W}px;
             height:{TAB_STRIP_H}px; display:flex; background:{CAPTION_BG}; }}
  .caption div {{ flex:1; display:flex; align-items:center; justify-content:center;
                 border-left:1px solid {CAPTION_DIVIDER}; }}
  .toolbar {{ position:absolute; left:0; right:0; top:{TAB_STRIP_H}px;
             height:{TOOLBAR_H}px; background:{toolbar}; }}
  .nav {{ position:absolute; left:14px; top:0; height:{TOOLBAR_H}px; display:flex;
         align-items:center; gap:18px; }}
  .omnibox {{ position:absolute; left:{OMNIBOX_L}px; top:{(TOOLBAR_H - OMNIBOX_H) // 2}px;
             width:{OMNIBOX_W}px; height:{OMNIBOX_H}px; border-radius:{OMNIBOX_H // 2}px;
             background:{omnibox}; display:flex; align-items:center; gap:10px;
             padding:0 14px; }}
  .omni-right {{ margin-left:auto; display:flex; align-items:center; gap:10px; }}
  .placeholder {{ flex:1; font-size:13.5px; color:{PLACEHOLDER};
                 white-space:nowrap; overflow:hidden; }}
  .tools-right {{ position:absolute; right:12px; top:0; height:{TOOLBAR_H}px;
                 display:flex; align-items:center; gap:13px; }}
  .ext {{ width:19px; height:19px; border-radius:5px; display:flex;
         align-items:center; justify-content:center; font-size:10.5px; color:#fff; }}
  .avatar {{ width:23px; height:23px; border-radius:50%; background:#7B61FF;
            color:#fff; font-size:11.5px; display:flex; align-items:center;
            justify-content:center; }}
  .bookmarks {{ position:absolute; left:0; right:0; top:{TAB_STRIP_H + TOOLBAR_H}px;
               height:{BOOKMARK_H}px; background:{toolbar}; display:flex;
               align-items:center; padding:0 12px; gap:6px; font-size:12.5px;
               color:{toolbar_icon}; }}
  .apps {{ display:grid; grid-template-columns:repeat(3,1fr); gap:2px; width:16px; }}
  .apps span {{ width:4px; height:4px; border-radius:1px; background:{toolbar_icon}; }}
  .sep {{ width:1px; height:16px; background:{CAPTION_DIVIDER}; margin:0 6px; }}
  .bm {{ display:flex; align-items:center; gap:5px; padding:0 4px; }}
  .ntp {{ position:absolute; left:0; right:0; top:{NTP_TOP}px; bottom:0;
         background:{ntp}; }}
  .wordmark {{ position:absolute; left:0; right:0; top:{WORDMARK_TOP}px;
              text-align:center; font-size:{WORDMARK_SIZE}px; font-weight:700;
              letter-spacing:-3px; color:{WORDMARK}; font-family:Arial, sans-serif; }}
  .searchbox {{ position:absolute; left:{SEARCH_L}px; top:{SEARCH_TOP}px;
               width:{SEARCH_W}px; height:{SEARCH_H}px; border-radius:{SEARCH_H // 2}px;
               background:#FFFFFF; box-shadow:0 1px 6px rgba(32,33,36,.18);
               display:flex; align-items:center; gap:12px; padding:0 18px; }}
  .shortcuts {{ position:absolute; left:0; right:0; top:{SHORTCUT_TOP}px;
               display:flex; justify-content:center; }}
  .shortcut {{ width:108px; text-align:center; }}
  .sdisc {{ width:47px; height:47px; margin:0 auto 10px; border-radius:50%;
           background:{SHORTCUT_DISC}; display:flex; align-items:center;
           justify-content:center; }}
  .slabel {{ font-size:12.5px; color:{LABEL}; white-space:nowrap; overflow:hidden;
            text-overflow:ellipsis; }}
  .pill {{ position:absolute; right:12px; bottom:14px; height:26px;
          border-radius:13px; background:{PILL_BG}; display:flex;
          align-items:center; gap:8px; padding:0 13px; font-size:13px;
          color:{PILL_TEXT}; }}
</style></head><body>
  <div class="tabstrip">
    {tab_html}
    <div class="sliver" style="left:{sliver_x}px"></div>
    <div class="caption">{caption}</div>
  </div>
  <div class="toolbar">
    <div class="nav">
      {tool('<path d="M15 5l-7 7 7 7"/>')}
      {tool('<path d="M9 5l7 7-7 7"/>')}
      {tool('<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v4h-4"/>')}
      {tool('<path d="M4 11l8-6 8 6v9H4z"/>')}
    </div>
    <div class="omnibox">
      <svg viewBox="0 0 48 48" width="17" height="17">
        <path fill="#4285F4" d="M45 24c0-1.6-.1-2.7-.4-3.9H24v7.1h11.9c-.2 2-.1 3.4-1 4.7l-5.1 3.9c2.6-2.4 6.3-6.3 6.3-11.8z"/>
        <path fill="#34A853" d="M24 45c3.2 0 6-.9 8-2.5l-6.3-4.9c-1 .7-2.3 1.1-3.7 1.1-4 0-7.4-2.7-8.6-6.3l-6.5 5C9.5 41.1 16.2 45 24 45z"/>
        <path fill="#FBBC05" d="M15.4 32.4c-.3-.9-.5-1.9-.5-3s.2-2 .5-3l-6.5-5C7.3 24 6.7 26 6.7 29.4s.9 5.4 2.2 7.9l6.5-4.9z"/>
        <path fill="#EA4335" d="M24 12.4c2.2 0 4.1.8 5.6 2.2l5.6-5.6C32 6 28.2 4.6 24 4.6 16.2 4.6 9.5 8.5 8.9 12.5l6.5 5c1.2-3.6 4.6-5.1 8.6-5.1z"/>
      </svg>
      <div class="placeholder">Search Google or type a URL</div>
      <div class="omni-right">
        <svg viewBox="0 0 24 24" width="17" height="17" fill="{ICON_GRAY}">
          <path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z"/>
          <path d="M18 12a6 6 0 0 1-12 0" fill="none" stroke="{ICON_GRAY}" stroke-width="1.8"/>
          <path d="M12 18v3" fill="none" stroke="{ICON_GRAY}" stroke-width="1.8"/></svg>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
             stroke="{LENS_BLUE}" stroke-width="1.9"><circle cx="11" cy="11" r="6.2"/>
          <path d="M16 16l4.5 4.5"/></svg>
      </div>
    </div>
    <div class="tools-right">
      {tool('<path d="M12 4l2.6 5.6 6 .8-4.4 4.2 1.1 6-5.3-3-5.3 3 1.1-6L3.4 10.4l6-.8z"/>', 19)}
      <div class="ext" style="background:#4285F4">
        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="#fff"
             stroke-width="2.2"><rect x="4" y="6" width="16" height="14" rx="2.5"/>
          <path d="M8 3.5h9.5V6"/></svg>
      </div>
      <div class="ext" style="background:#EA4335;border-radius:50%">
        <svg viewBox="0 0 24 24" width="12" height="12" fill="#fff">
          <path d="M3 7l9 6 9-6v11H3z" opacity=".95"/><path d="M3 6h18v2l-9 6-9-6z"/></svg>
      </div>
      <div class="ext" style="background:#202124">18</div>
      <div class="ext" style="background:#9AA0A6;border-radius:50%">
        <svg viewBox="0 0 24 24" width="12" height="12" fill="#fff">
          <path d="M4 5h16v11H9l-5 4z"/></svg>
      </div>
      <div class="sep"></div>
      <div class="avatar">S</div>
      <svg viewBox="0 0 24 24" width="18" height="18" fill="{toolbar_icon}">
        <circle cx="12" cy="5" r="1.7"/><circle cx="12" cy="12" r="1.7"/>
        <circle cx="12" cy="19" r="1.7"/></svg>
    </div>
  </div>
  <div class="bookmarks">
    <span class="apps"><span></span><span></span><span></span><span></span>
      <span></span><span></span><span></span><span></span><span></span></span>
    <div class="sep"></div>
    {bookmark}
  </div>
  <div class="ntp">
    <div class="wordmark">Google</div>
    <div class="searchbox">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
           stroke="{PLACEHOLDER}" stroke-width="2" stroke-linecap="round">
        <circle cx="11" cy="11" r="6"/><path d="M16 16l4 4"/></svg>
      <div class="placeholder">Search Google or type a URL</div>
      <svg viewBox="0 0 24 24" width="18" height="18" fill="{ICON_GRAY}">
        <path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z"/>
        <path d="M18 12a6 6 0 0 1-12 0" fill="none" stroke="{ICON_GRAY}" stroke-width="1.8"/>
        <path d="M12 18v3" fill="none" stroke="{ICON_GRAY}" stroke-width="1.8"/></svg>
      <svg viewBox="0 0 24 24" width="19" height="19" fill="none"
           stroke="{LENS_BLUE}" stroke-width="1.9"><circle cx="11" cy="11" r="6.2"/>
        <path d="M16 16l4.5 4.5"/></svg>
    </div>
    <div class="shortcuts">
      <div class="shortcut">
        <div class="sdisc">{favicon('youtube', frame)}</div>
        <div class="slabel">YouTube</div>
      </div>
      <div class="shortcut">
        <div class="sdisc">{favicon('store', frame)}</div>
        <div class="slabel">Chrome Web Store</div>
      </div>
      <div class="shortcut">
        <div class="sdisc">{favicon('plus', frame)}</div>
        <div class="slabel">Add shortcut</div>
      </div>
    </div>
    <div class="pill">
      <svg viewBox="0 0 24 24" width="14" height="14" fill="none"
           stroke="{PILL_PENCIL}" stroke-width="1.9" stroke-linecap="round">
        <path d="M4 20h4L20 8l-4-4L4 16z"/></svg>
      Customize Chrome
    </div>
  </div>
</body></html>"""


def build_intro(c):
    """Screenshot 2: the palette card, same visual language as screenshot 1."""
    bg = hexof(c["frame"])
    ink = hexof(c["tab_text"])
    cards = [
        ("Tab", hexof(c["background_tab"]), "Inactive tabs"),
        ("Paper", hexof(c["toolbar"]), "Toolbar &amp; active tab"),
        ("Haze", hexof(c["ntp_background"]), "New tab page"),
        ("Deep Ink", hexof(c["tab_text"]), "Text, icons &amp; links"),
    ]
    card_html = ""
    for i, (name, col, use) in enumerate(cards):
        x = 76 + (i % 2) * 576
        y = 244 + (i // 2) * 208
        txt = "#FFFFFF" if i == 3 else ink
        card_html += f"""
    <div class="card" style="left:{x}px;top:{y}px;background:{col};color:{txt}">
      <div class="cname">{name}</div>
      <div class="cuse">{col} &middot; {use}</div>
    </div>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:{W}px; height:{H}px; background:{bg}; position:relative;
         font-family:'Segoe UI', Arial, sans-serif; }}
  .eyebrow {{ position:absolute; left:76px; top:60px; font-size:13px;
             letter-spacing:3.2px; color:{ink}; opacity:.68;
             text-transform:uppercase; }}
  h1 {{ position:absolute; left:76px; top:84px; font-weight:400;
        font-family:Georgia,'Times New Roman',serif; font-size:60px;
        letter-spacing:-.5px; color:{ink}; }}
  .sub {{ position:absolute; left:76px; top:176px; font-size:22px; color:{ink};
          opacity:.78; }}
  .card {{ position:absolute; width:552px; height:184px; border-radius:14px;
          padding:0 34px 32px; display:flex; flex-direction:column;
          justify-content:flex-end; border:1px solid rgba(20,22,24,.16); }}
  .cname {{ font-size:27px; font-weight:700; margin-bottom:8px; }}
  .cuse {{ font-size:17px; opacity:.82; }}
  .foot {{ position:absolute; left:76px; top:664px; font-size:18px; color:{ink};
          opacity:.7; }}
  .framenote {{ position:absolute; right:76px; top:64px; font-size:15px;
               color:{ink}; opacity:.72; display:flex; align-items:center; gap:10px; }}
  .framenote i {{ width:15px; height:15px; border-radius:4px;
                 background:{bg}; border:1px solid rgba(20,22,24,.28); }}
</style></head><body>
  <div class="eyebrow">A quiet, open sky</div>
  <h1>Calm Sky Theme</h1>
  <div class="sub">Four airy blues. One calm, unhurried browser.</div>
  <div class="framenote"><i></i>Frame &middot; {bg} &middot; window frame</div>{card_html}
  <div class="foot">Solid colours &middot; Minimal design &middot; No wallpaper
    &middot; No permissions required</div>
</body></html>"""


def main():
    data = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    colors = data["theme"]["colors"]
    shots = [("screenshot-1-browser", build_browser(colors)),
             ("screenshot-2-introduction", build_intro(colors))]
    SHOTS.mkdir(parents=True, exist_ok=True)
    REFS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, html in shots:
            page = browser.new_page(viewport={"width": W, "height": H},
                                    device_scale_factor=1)
            page.set_content(html, wait_until="load")
            # Playwright's own path handling chokes (OSError 22) on this
            # project's non-ASCII folder name: render to temp, copy in Python.
            tmp = Path(tempfile.gettempdir()) / f"calm-sky-{name}.png"
            page.screenshot(path=str(tmp))
            out = SHOTS / f"{name}.png"
            shutil.copyfile(tmp, out)
            page.close()
            (REFS / f"{name}.html").write_text(html, encoding="utf-8")
            shutil.copyfile(out, REFS / f"{name}.png")
            print("wrote", out, W, H)
        browser.close()


if __name__ == "__main__":
    main()
