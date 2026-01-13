🌍 TV Logos Worldwide – Auto IPTV Logo & M3U Manager

A fully automated system that fetches global TV channel logos, organizes them by country, converts SVG → PNG without Cairo/DLL issues, matches them to IPTV channels, and injects logos directly into M3U playlists.

Designed to run daily via GitHub Actions with zero manual intervention.

✨ Features

🌐 Worldwide TV logo aggregation

IPTV-ORG

Wikipedia / Wikimedia Commons

Fallback public logo sources

🗂 Country-by-country logo organization

🔁 SVG → PNG conversion using svglib (no Cairo, no DLLs)

📺 Automatic IPTV channel fetching

🧠 Smart logo matching to channel names

🧩 Auto-inject tvg-logo directly into M3U

⏱ Daily auto-update via GitHub Actions

🧼 Smart commits (only pushes when changes exist)

📁 Repository Structure
tv-logos-worldwide/
│
├── tv-logos-worldwide.py        # Unified daily runner (logos + M3U)
├── tv-logos/
│   └── countries/
│       └── CA/
│           └── CBC.png
│
├── playlists/
│   └── output.m3u               # Auto-generated playlist with logos
│
├── .github/
│   └── workflows/
│       └── daily-update.yml     # GitHub Actions automation
│
├── requirements.txt
└── README.md

🚀 How It Works (Daily Flow)

Fetch IPTV channels automatically

Download logos from multiple public sources

Normalize & group logos by country

Convert SVG → PNG safely

Match channels ↔ logos intelligently

Inject logos into M3U

Commit & push only if changes exist

▶️ Run Locally (Optional)
1️⃣ Install Python dependencies
pip install -r requirements.txt

2️⃣ Run the unified script
python tv-logos-worldwide.py


Output:

Logos saved under tv-logos/countries/

Playlist saved to playlists/output.m3u

🤖 GitHub Actions (Recommended)

The system is designed to run entirely in GitHub Actions.

Daily schedule:

⏰ 02:00 UTC

🖱 Manual trigger available

Workflow file:

.github/workflows/daily-update.yml


No local execution required.

🛡 Why This Project Avoids Cairo

Many logo tools fail on Windows due to:

Missing cairo.dll

Broken binary dependencies

This project uses:

svglib

reportlab

✔ Pure Python
✔ Works on Windows, Linux, GitHub Actions
✔ No system libraries required

📌 Use Cases

IPTV apps (Kodi, Tivimate, OTT platforms)

IPTV playlist maintainers

TV metadata aggregation

Logo hosting for M3U providers

📜 License

MIT License
Free to use, modify, and distribute.

🤝 Contributions

Pull requests are welcome for:

New logo sources

Better channel matching logic

Additional playlist formats

⚠️ Disclaimer

This project does not host streams.
It only manages logos and metadata for publicly available IPTV playlists.
