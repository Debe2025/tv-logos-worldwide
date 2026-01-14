#!/usr/bin/env python3
"""
build.py
--------
Unified IPTV build script.

Responsibilities:
- Fetch IPTV playlists (iptv-org)
- Aggregate TV logos (URLs only, no conversion)
- Inject tvg-logo into M3U
- Output Kodi-ready assets into dist/

NO binary dependencies.
NO SVG conversion.
NO Cairo.
NO Pillow.
"""

import sys
import json
import re
import requests
from pathlib import Path
from datetime import datetime

# -------------------------
# Paths (build vs dist)
# -------------------------
ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DIST_LOGOS = DIST / "logos"
DIST_PLAYLISTS = DIST / "playlists"

DIST.mkdir(exist_ok=True)
DIST_LOGOS.mkdir(parents=True, exist_ok=True)
DIST_PLAYLISTS.mkdir(parents=True, exist_ok=True)

# -------------------------
# Sources
# -------------------------
IPTV_COUNTRIES = "https://iptv-org.github.io/iptv/countries"
IPTV_LANG = "https://iptv-org.github.io/iptv/languages/eng.m3u"
IPTV_MOVIES = "https://iptv-org.github.io/iptv/categories/movies.m3u"
IPTV_SPORTS = "https://iptv-org.github.io/iptv/categories/sports.m3u"

LOGO_SOURCES = [
    "https://iptv-org.github.io/iptv/logos.json",
    "https://raw.githubusercontent.com/tv-logo/tv-logos/main/tv-logos.json"
]

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "tv-logos-worldwide-build/1.0"})

# -------------------------
# Helpers
# -------------------------
def fetch(url: str) -> str:
    r = SESSION.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def fetch_json(url: str) -> dict:
    r = SESSION.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


# -------------------------
# Logo aggregation (URL-only)
# -------------------------
def build_logo_map() -> dict:
    logo_map = {}

    for src in LOGO_SOURCES:
        try:
            data = fetch_json(src)
        except Exception:
            continue

        for entry in data:
            name = entry.get("name") or entry.get("channel")
            logo = entry.get("logo") or entry.get("url")
            if not name or not logo:
                continue

            logo_map[normalize(name)] = logo

    # Save for transparency/debug
    with open(DIST / "logo-map.json", "w", encoding="utf-8") as f:
        json.dump(logo_map, f, indent=2)

    return logo_map


# -------------------------
# M3U processing
# -------------------------
def inject_logos(m3u_text: str, logos: dict) -> str:
    out = []
    last_extinf = ""

    for line in m3u_text.splitlines():
        if line.startswith("#EXTINF"):
            name_match = re.search(r",(.*)$", line)
            if name_match:
                name = normalize(name_match.group(1))
                logo = logos.get(name)
                if logo and 'tvg-logo=' not in line:
                    line = line.replace(
                        "#EXTINF:",
                        f'#EXTINF:tvg-logo="{logo}",'
                    )
            last_extinf = line
            out.append(line)
        else:
            out.append(line)

    return "\n".join(out) + "\n"


# -------------------------
# Playlist build
# -------------------------
def build_playlist(name: str, url: str, logos: dict):
    print(f"[+] Fetching {name}")
    raw = fetch(url)
    final = inject_logos(raw, logos)

    out_file = DIST_PLAYLISTS / f"{name}.m3u8"
    out_file.write_text(final, encoding="utf-8")


# -------------------------
# Main
# -------------------------
def main():
    print("=== IPTV BUILD START ===")
    print(datetime.utcnow().isoformat(), "UTC")

    logos = build_logo_map()
    print(f"[+] Logos mapped: {len(logos)}")

    build_playlist("english", IPTV_LANG, logos)
    build_playlist("movies", IPTV_MOVIES, logos)
    build_playlist("sports", IPTV_SPORTS, logos)

    print("=== BUILD COMPLETE ===")
    print(f"Output: {DIST}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
