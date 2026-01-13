import re
import json
from pathlib import Path

M3U_INPUT = Path("input.m3u")
M3U_OUTPUT = Path("output_with_logos.m3u")
LOGO_MAP = Path("tv-logos-worldwide/iptv/m3u-mapping.json")


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


def main():
    logos = json.loads(LOGO_MAP.read_text(encoding="utf-8"))
    lines = M3U_INPUT.read_text(encoding="utf-8", errors="ignore").splitlines()

    output = []
    last_extinf = None

    for line in lines:
        if line.startswith("#EXTINF"):
            last_extinf = line

            # extract tvg-name
            match = re.search(r'tvg-name="([^"]+)"', line)
            name = match.group(1) if match else line.split(",")[-1]

            key = normalize(name)

            if key in logos and 'tvg-logo=' not in line:
                line = line.replace(
                    "#EXTINF",
                    f'#EXTINF tvg-logo="{logos[key]}"',
                    1
                )

        output.append(line)

    M3U_OUTPUT.write_text("\n".join(output), encoding="utf-8")
    print("M3U logo injection complete.")


if __name__ == "__main__":
    main()
