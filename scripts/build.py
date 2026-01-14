#!/usr/bin/env python3
"""
Unified IPTV builder:
- Fetch channels (iptv-org)
- Aggregate logos (iptv-org + Wikipedia)
- Convert SVG → PNG (NO Cairo)
- Inject tvg-logo into M3U
- Output static files for Kodi
"""

import os
import re
import gzip
import shutil
import requests
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# -------------------------
# CONFIG
# -------------------------

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LOGOS = DIST / "logos"
PLAYLISTS = DIST / "playlists"

IPTV_ORG_BASE = "https://iptv-org.github.io/iptv/countries"
COUNTRIES = ["us", "gb", "ca", "fr", "de", "ng"]  # extend freely

LOGO_REPOS = [
    "https://raw.githubusercontent.com/iptv-org/logos/master/logos",
    "https://upload.wikimedia.org/wikipedia/commons"
]

USER_AGENT = {"User-Agent": "tv-logos-worldwide-builder"}

# -------------------------
# HELPERS
# -------------------------

def safe_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", name)

def fetch(url: str) -> str:
    r = requests.get(url, headers=USER_AGENT, timeout=30)
    r.raise_for_status()
    return r.text

def ensure_dirs():
    for p in [LOGOS, PLAYLISTS]:
        p.mkdir(parents=True, exist_ok=True)

# -------------------------
# LOGO HANDLING
# -------------------------

def svg_to_png(svg_bytes: bytes, out_path: Path):
    drawing = svg2rlg(svg_bytes)
    renderPM.drawToFile(drawing, str(out_path), fmt="PNG")

def fetch_logo(channel: str, country: str) -> str | None:
    filename = safe_name(channel)

    out_dir = LOGOS / country.upper()
    out_dir.mkdir(parents=True, exist_ok=True)

    png_path = out_dir / f"{filename}.png"
    if png_path.exists():
        return png_path.as_posix()

    for repo in LOGO_REPOS:
        svg_url = f"{repo}/{filename}.svg"
        try:
            r = requests.get(svg_url, headers=USER_AGENT, timeout=15)
            if r.status_code == 200:
                svg_to_png(r.content, png_path)
                return png_path.as_posix()
        except Exception:
            continue

    return None

# -------------------------
# M3U PROCESSING
# -------------------------

def build_playlist():
    out_m3u = PLAYLISTS / "tv.m3u"
    with out_m3u.open("w", encoding="utf-8") as out:
        out.write("#EXTM3U\n")

        for cc in COUNTRIES:
            url = f"{IPTV_ORG_BASE}/{cc}.m3u"
            try:
                data = fetch(url)
            except Exception:
                continue

            lines = data.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("#EXTINF"):
                    name = line.split(",")[-1].strip()
                    logo = fetch_logo(name, cc)

                    if logo:
                        line = re.sub(
                            r'tvg-logo="[^"]*"',
                            '',
                            line
                        ).replace(
                            "#EXTINF",
                            f'#EXTINF tvg-logo="{logo}"'
                        )

                    out.write(line + "\n")
                    out.write(lines[i + 1] + "\n")

# -------------------------
# MAIN
# -------------------------

def main():
    ensure_dirs()
    build_playlist()

if __name__ == "__main__":
    main()
