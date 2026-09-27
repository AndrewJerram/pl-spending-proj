"""
Downloads Premier League match results + betting-odds CSVs from football-data.co.uk
for every season in the project's date range (2010-11 through the most recently
completed season) and saves them to data/raw/results/.

Run this on a machine with normal internet access - the URLs below are not
reachable from within some sandboxed/offline environments.

Usage:
    python src/fetch_results.py
"""
import requests
from pathlib import Path
import time

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "results"
RAW_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.football-data.co.uk/mmz4281/{code}/E0.csv"

# Season codes as used by football-data.co.uk, e.g. "1011" = 2010-11 season.
# Update the end of this list each summer once a new season starts.
SEASON_CODES = [
    "1011", "1112", "1213", "1314", "1415",
    "1516", "1617", "1718", "1819", "1920",
    "2021", "2122", "2223", "2324", "2425", "2526",
]


def fetch_season(code: str) -> None:
    url = BASE_URL.format(code=code)
    out_path = RAW_DIR / f"{code}_E0.csv"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    print(f"Saved {out_path} ({len(resp.content):,} bytes)")


def main():
    for code in SEASON_CODES:
        try:
            fetch_season(code)
        except requests.RequestException as e:
            print(f"Failed to fetch season {code}: {e}")
        time.sleep(1)  # be polite to the server


if __name__ == "__main__":
    main()
