# tv-logos-worldwide

Automated aggregation of worldwide TV channel logos with IPTV playlist generation and Kodi-compatible M3U output.

This repository fetches IPTV channels, downloads TV logos from multiple public sources, converts SVG logos to PNG without Cairo dependencies, matches logos to channels, and injects `tvg-logo` entries directly into an M3U playlist.

The system is designed to run unattended via GitHub Actions.

---

## Features

- Automatic IPTV channel fetching
- Multi-source logo aggregation (iptv-org, Wikimedia, public broadcasters)
- Country-based logo organization
- SVG → PNG conversion using svglib (no Cairo / DLLs)
- Automatic `tvg-logo` injection into M3U playlists
- Daily scheduled updates via GitHub Actions
- Kodi IPTV Simple Client compatible

---

## Repository Structure

tv-logos-worldwide/
├── tv-logos-worldwide.py # Main automation script
├── tv-logos/
│ └── countries/
│ └── US/
│ └── CNN.png
├── playlists/
│ └── output.m3u # Generated M3U with logos
├── .github/workflows/
│ └── daily-update.yml
├── requirements.txt
└── README.md

yaml
Copy code

---

## Requirements

- Python 3.10+
- Internet connection

Python dependencies:
- requests
- svglib
- reportlab

---

## Usage

### Local execution (optional)

```bash
pip install -r requirements.txt
python tv-logos-worldwide.py
Output:

bash
Copy code
playlists/output.m3u
Automated Execution (Recommended)
This repository is intended to run via GitHub Actions.

Executes daily at 02:00 UTC

Can be triggered manually

Commits changes only when updates are detected

Workflow file:

bash
Copy code
.github/workflows/daily-update.yml
Kodi Configuration
Playlist URL
perl
Copy code
https://raw.githubusercontent.com/<USERNAME>/tv-logos-worldwide/main/playlists/output.m3u
Kodi Steps
Open Kodi

Go to Settings → Add-ons

Install PVR IPTV Simple Client

Configure:

Location: Remote path (Internet address)

M3U playlist URL: paste the URL above

Logos:

Enable Channel logos from M3U

Enable the add-on and restart Kodi

Notes
Kodi caches logos aggressively; initial logo loading may take time

Clear Kodi cache if logo updates do not appear immediately

No local logo directories are required in Kodi

License
MIT License

Disclaimer
This repository does not provide or host IPTV streams.
It manages logos and metadata for publicly available playlists only.
