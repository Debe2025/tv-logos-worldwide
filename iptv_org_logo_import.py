import requests
import json
from pathlib import Path

IPTV_ORG_JSON = "https://raw.githubusercontent.com/iptv-org/iptv/master/channels.json"
OUTPUT = Path("tv-logos-worldwide/iptv/iptv-org.json")

def normalize(name):
    return (
        name.lower()
        .replace("&", "and")
        .replace("tv", "")
        .replace("-", "")
        .replace(" ", "")
    )

def main():
    data = requests.get(IPTV_ORG_JSON, timeout=30).json()
    logos = {}

    for ch in data:
        if "logo" in ch and ch["logo"]:
            key = normalize(ch["name"])
            logos[key] = ch["logo"]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(logos, indent=2), encoding="utf-8")
    print("iptv-org logos imported")

if __name__ == "__main__":
    main()
