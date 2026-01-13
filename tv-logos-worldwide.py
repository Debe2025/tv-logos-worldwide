import requests
import json
import time
import re
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from bs4 import BeautifulSoup

# ---------------- CONFIG ---------------- #
GITHUB_TVLOGOS_API = "https://api.github.com/repos/tv-logo/tv-logos/contents/countries"
RAW_TVLOGOS_BASE = "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries"
IPTV_ORG_JSON_URL = "https://raw.githubusercontent.com/iptv-org/iptv/master/channels.json"

# Add additional public M3U sources here if desired
MULTI_M3U_SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/channels.m3u",
    # "https://example.com/another-regional.m3u"
]

ROOT = Path("tv-logos-worldwide")
COUNTRIES = ROOT / "countries"
IPTV_DIR = ROOT / "iptv"
M3U_FILE = ROOT / "output_with_logos.m3u"
INDEX_FILE = ROOT / "index.json"
MAPPING_FILE = IPTV_DIR / "m3u-mapping.json"

DELAY = 0.2

# ---------------- HELPERS ---------------- #

def github_json(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def download(url, path):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    path.write_bytes(r.content)

def convert_svg(svg_path, png_path):
    drawing = svg2rlg(str(svg_path))
    renderPM.drawToFile(drawing, str(png_path), fmt="PNG")

def normalize(name):
    return (
        name.lower()
        .replace("&", "and")
        .replace("tv", "")
        .replace("channel", "")
        .replace("-", "")
        .replace("_", "")
        .replace(" ", "")
    )

def fetch_wikipedia_logo(channel_name):
    """Try to fetch logo from Wikipedia infobox if exists"""
    try:
        search_url = f"https://en.wikipedia.org/w/index.php?search={channel_name.replace(' ', '+')}"
        r = requests.get(search_url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        img = soup.select_one("table.infobox img")
        if img and img.get("src"):
            src = img["src"]
            if src.startswith("//"):
                src = "https:" + src
            return src
    except:
        return None
    return None

# ---------------- FETCH TV LOGOS ---------------- #

def fetch_tvlogos():
    COUNTRIES.mkdir(parents=True, exist_ok=True)
    index = {}
    logo_lookup = {}

    countries = github_json(GITHUB_TVLOGOS_API)
    for country in countries:
        if country["type"] != "dir":
            continue
        code = country["name"]
        folder = COUNTRIES / code
        folder.mkdir(exist_ok=True)
        index[code] = []

        files = github_json(country["url"])
        for f in files:
            if f["type"] != "file":
                continue
            name = f["name"]
            raw_url = f"{RAW_TVLOGOS_BASE}/{code}/{name}"
            path = folder / name
            download(raw_url, path)
            index[code].append(name)

            if name.lower().endswith(".svg"):
                png_path = path.with_suffix(".png")
                if not png_path.exists():
                    convert_svg(path, png_path)
                key = normalize(path.stem)
                logo_lookup[key] = str(png_path).replace("\\", "/")

            time.sleep(DELAY)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    return logo_lookup

# ---------------- FETCH IPTV-ORG LOGOS ---------------- #

def fetch_iptv_org_logos(logo_lookup):
    IPTV_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(IPTV_ORG_JSON_URL, timeout=30)
    r.raise_for_status()
    data = r.json()
    channels = []
    for ch in data:
        if "logo" in ch and ch["logo"]:
            key = normalize(ch["name"])
            if key not in logo_lookup:
                logo_lookup[key] = ch["logo"]
        if "url" in ch and ch["url"]:
            channels.append(ch)
    return logo_lookup, channels

# ---------------- WIKIPEDIA + FALLBACK ---------------- #

def fetch_missing_logos(logo_lookup, channels):
    for ch in channels:
        key = normalize(ch["name"])
        if key not in logo_lookup:
            wiki_logo = fetch_wikipedia_logo(ch["name"])
            if wiki_logo:
                logo_lookup[key] = wiki_logo
                print(f"Fallback Wikipedia logo found for {ch['name']}")
    return logo_lookup

# ---------------- MERGE MULTIPLE M3U SOURCES ---------------- #

def fetch_m3u(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    lines = r.text.splitlines()
    channels = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            info = line
            stream = lines[i + 1].strip() if (i + 1) < len(lines) else ""
            match = re.search(r'tvg-name="([^"]+)"', info)
            name = match.group(1) if match else re.sub(r"#EXTINF:-1,", "", info)
            channels.append({"name": name, "url": stream})
            i += 1
        i += 1
    return channels

def merge_m3u_sources(sources):
    all_channels = []
    seen = set()
    for url in sources:
        try:
            channels = fetch_m3u(url)
            for ch in channels:
                key = normalize(ch["name"])
                if key not in seen:
                    all_channels.append(ch)
                    seen.add(key)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
    return all_channels

# ---------------- SAVE LOGO MAPPING ---------------- #

def save_mapping(logo_lookup):
    IPTV_DIR.mkdir(parents=True, exist_ok=True)
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(logo_lookup, f, indent=2)

# ---------------- GENERATE M3U ---------------- #

def generate_m3u(logo_lookup, channels):
    m3u_lines = ["#EXTM3U"]
    for ch in channels:
        name = ch.get("name", "Unknown")
        stream_url = ch.get("url")
        if not stream_url:
            continue
        key = normalize(name)
        logo = logo_lookup.get(key, "")
        extinf = f'#EXTINF:-1 tvg-id="{key}" tvg-name="{name}"'
        if logo:
            extinf += f' tvg-logo="{logo}"'
        extinf += f',{name}'
        m3u_lines.append(extinf)
        m3u_lines.append(stream_url)

    M3U_FILE.write_text("\n".join(m3u_lines), encoding="utf-8")
    print(f"Generated M3U with logos: {M3U_FILE}")

# ---------------- MAIN ---------------- #

def main():
    print("Step 1: Fetch TV logos and convert SVG → PNG...")
    logo_lookup = fetch_tvlogos()

    print("Step 2: Fetch iptv-org channels + logos...")
    logo_lookup, iptv_channels = fetch_iptv_org_logos(logo_lookup)

    print("Step 3: Fetch missing logos from Wikipedia...")
    logo_lookup = fetch_missing_logos(logo_lookup, iptv_channels)

    print("Step 4: Merge additional M3U sources...")
    extra_channels = merge_m3u_sources(MULTI_M3U_SOURCES[1:])
    all_channels = iptv_channels + extra_channels

    print("Step 5: Save logo mapping...")
    save_mapping(logo_lookup)

    print("Step 6: Generate master M3U with logos injected...")
    generate_m3u(logo_lookup, all_channels)

    print("All steps completed successfully.")

if __name__ == "__main__":
    main()
