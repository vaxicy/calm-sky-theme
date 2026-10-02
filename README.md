<p align="center">
  <img src="https://raw.githubusercontent.com/vaxicy/calm-sky-theme/main/logo/logo.png?rev=786b821e" width="128" alt="Calm Sky Theme icon">
</p>

<h1 align="center">Calm Sky Theme</h1>

<p align="center">A light, airy blue theme for calm, unhurried browsing.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Chrome%20Web%20Store-theme-blue?logo=googlechrome" alt="Chrome Web Store">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="version">
  <img src="https://img.shields.io/badge/license-Non--Commercial-lightgrey" alt="license">
</p>

## About

Calm Sky opens the browser onto a wide, quiet sky. A soft sky-blue window frame wraps pale blue-grey tabs, a near-white toolbar sits underneath, and the new-tab page fills with a calm, washed blue, so the page you are reading stays the brightest thing on screen. Deep slate text carries every label, icon and bookmark, keeping contrast comfortable across all of those light surfaces. The design is flat colour throughout — no wallpaper, no textures, no gradients — and the icon distills it into a single sun resting on a still horizon.

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Sky | `#93BFDC` | Window frame |
| Tab | `#CCDEE7` | Inactive tabs |
| Paper | `#E5EAEF` | Toolbar and active tab |
| Haze | `#D7E8EC` | New tab page |
| White | `#FFFFFF` | Omnibox (address bar) field |
| Deep Ink | `#203441` | Tab and new-tab text |
| Slate | `#5F7381` | Toolbar icons and secondary text |

## Features

- Airy sky-blue palette with a soft, matte finish.
- Solid colour design with no images, textures or gradients.
- Deep slate text tuned for contrast on every light surface.
- Matching incognito colours.
- Calm, distraction-free new-tab page.
- Pure theme: no scripts, no permissions, nothing collected.

## Install

### From source (unpacked)

1. Download or clone this repository.
2. Open Chrome and navigate to `chrome://extensions`.
3. Enable **Developer mode** in the top-right corner.
4. Click **Load unpacked** and select this folder.

### From Chrome Web Store

Search for **Calm Sky Theme** in the Chrome Web Store and install it.

## Preview

![Calm Sky Theme browser preview](https://raw.githubusercontent.com/vaxicy/calm-sky-theme/main/store-assets/screenshots/en/screenshot-1-browser.png?rev=786b821e)

![Calm Sky Theme palette](https://raw.githubusercontent.com/vaxicy/calm-sky-theme/main/store-assets/screenshots/en/screenshot-2-introduction.png?rev=786b821e)

### Store promo tiles

![Calm Sky Theme marquee](https://raw.githubusercontent.com/vaxicy/calm-sky-theme/main/store-assets/promo/1400x560.png?rev=786b821e)

<p align="center">
  <img src="https://raw.githubusercontent.com/vaxicy/calm-sky-theme/main/store-assets/promo/440x280.png?rev=786b821e" width="440" alt="Calm Sky Theme promo tile">
</p>

## Files

| File | Description |
|------|-------------|
| `manifest.json` | Chrome theme manifest (MV3) with inline `theme` config — single source of truth for every colour |
| `logo/logo.png` | Chrome Web Store icon (128x128) |
| `store-assets/screenshots/en/` | Store listing screenshots (1280x800) |
| `store-assets/promo/` | Promo tiles (440x280 and 1400x560) |
| `store-assets/references/` | The browser mock-up HTML and its PNG render |
| `store-assets/store-description.txt` | Store listing detailed description (English) |
| `store-assets/icon-candidates/` | The six logo concepts that were explored before the final mark |
| `scripts/` | Generators: logo, promo, screenshots, upload zip |

## Packaging

```
python3 scripts/package-zip.py
```

Writes `dist/calm-sky-theme-<version>.zip` containing only `manifest.json` and `logo/logo.png`, and copies it to the default upload folder.

## License

Non-Commercial License — personal use permitted, commercial use requires permission. See [LICENSE](LICENSE).
