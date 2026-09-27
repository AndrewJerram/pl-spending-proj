"""
Joins data/processed/standings_by_season.csv (from load_results.py) with
data/processed/spend_by_club_season.csv (from load_transfers.py) into one
analysis-ready table: one row per club-season, with final position, points,
and transfer spend/income/net.

Run load_results.py and load_transfers.py first.

Usage:
    python src/build_analysis_table.py
"""
import pandas as pd
from pathlib import Path

PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def main():
    standings = pd.read_csv(PROC_DIR / "standings_by_season.csv")
    spend = pd.read_csv(PROC_DIR / "spend_by_club_season.csv")

    merged = standings.merge(
        spend[["Season", "Team", "gross_spend_eur", "gross_income_eur", "net_spend_eur"]],
        on=["Season", "Team"],
        how="left",
    )

    missing = merged[merged["net_spend_eur"].isna()]
    if len(missing):
        print(
            f"WARNING: {len(missing)} club-seasons in standings have no matching "
            "transfer data (check CLUB_NAME_MAP in load_transfers.py, or these "
            "are promoted clubs whose season isn't in the transfer files):"
        )
        print(missing[["Season", "Team"]].to_string(index=False))

    merged.to_csv(PROC_DIR / "analysis_table.csv", index=False)
    print(f"\nWrote {len(merged):,} rows -> data/processed/analysis_table.csv")


if __name__ == "__main__":
    main()
