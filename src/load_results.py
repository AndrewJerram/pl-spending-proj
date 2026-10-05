"""
Combines the per-season CSVs in data/raw/results/ into a single cleaned
match-results dataset, and derives season-level club standings
(points, goal difference, final position) used later to join against
wage-bill and transfer-spend data.

Usage:
    python src/load_results.py
"""
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "results"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Columns we actually need - the raw files carry ~70 betting-odds columns
# we don't need for this project.
KEEP_COLS = [
    "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
    "HTHG", "HTAG", "HTR", "HS", "AS", "HST", "AST",
    "HC", "AC", "HY", "AY", "HR", "AR",
]


def season_label(code: str) -> str:
    """'1011' -> '2010-11'"""
    start, end = code[:2], code[2:]
    century = "20"
    return f"{century}{start}-{end}"


def load_all_seasons() -> pd.DataFrame:
    frames = []
    for path in sorted(RAW_DIR.glob("*_E0.csv")):
        code = path.stem.split("_")[0]
        df = pd.read_csv(path)
        cols_present = [c for c in KEEP_COLS if c in df.columns]
        df = df[cols_present].copy()
        # football-data.co.uk files occasionally end with a stray row that's
        # just commas (no real match data) - a trailing blank line with no
        # commas gets skipped automatically, but one with empty fields doesn't.
        # Drop any row that isn't a real fixture before it pollutes standings.
        before = len(df)
        df = df.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"])
        dropped = before - len(df)
        if dropped:
            print(f"  {path.name}: dropped {dropped} malformed row(s)")
        df["Season"] = season_label(code)
        # Older seasons use dd/mm/yy, newer ones use dd/mm/yyyy - let pandas
        # infer per-file rather than forcing one format across all seasons.
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed", errors="coerce")
        frames.append(df)
    if not frames:
        raise FileNotFoundError(
            f"No season files found in {RAW_DIR} - run src/fetch_results.py first "
            "(or drop CSVs there manually)."
        )
    return pd.concat(frames, ignore_index=True)


def compute_standings(matches: pd.DataFrame) -> pd.DataFrame:
    """Derive final league table (points, GD, position) per club per season."""
    rows = []
    for season, sdf in matches.groupby("Season"):
        table = {}
        for _, m in sdf.iterrows():
            home, away = m["HomeTeam"], m["AwayTeam"]
            for team in (home, away):
                table.setdefault(team, {"Pld": 0, "W": 0, "D": 0, "L": 0,
                                         "GF": 0, "GA": 0, "Pts": 0})
            hg, ag = m["FTHG"], m["FTAG"]
            table[home]["Pld"] += 1
            table[away]["Pld"] += 1
            table[home]["GF"] += hg
            table[home]["GA"] += ag
            table[away]["GF"] += ag
            table[away]["GA"] += hg
            if hg > ag:
                table[home]["W"] += 1
                table[home]["Pts"] += 3
                table[away]["L"] += 1
            elif hg < ag:
                table[away]["W"] += 1
                table[away]["Pts"] += 3
                table[home]["L"] += 1
            else:
                table[home]["D"] += 1
                table[away]["D"] += 1
                table[home]["Pts"] += 1
                table[away]["Pts"] += 1
        for team, rec in table.items():
            rec["GD"] = rec["GF"] - rec["GA"]
            rows.append({"Season": season, "Team": team, **rec})
    standings = pd.DataFrame(rows)
    standings = standings.sort_values(
        ["Season", "Pts", "GD", "GF"], ascending=[True, False, False, False]
    )
    standings["Position"] = standings.groupby("Season").cumcount() + 1
    return standings.reset_index(drop=True)


def main():
    matches = load_all_seasons()
    matches.to_csv(OUT_DIR / "matches_combined.csv", index=False)
    print(f"Wrote {len(matches):,} matches -> data/processed/matches_combined.csv")

    standings = compute_standings(matches)
    standings.to_csv(OUT_DIR / "standings_by_season.csv", index=False)
    print(f"Wrote {len(standings):,} team-seasons -> data/processed/standings_by_season.csv")


if __name__ == "__main__":
    main()
