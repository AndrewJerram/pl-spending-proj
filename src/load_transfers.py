"""
Combines the per-season transfer CSVs in data/raw/transfers/ (sourced from
github.com/eordo/transfermarkt-data, itself built from the transfermarkt-datasets
/ Transfermarkt project - see README) into one per-club, per-season summary of
gross spend, gross income, and net spend, in euros.

These files use the Transfermarkt club names ("Arsenal FC", "Manchester United",
"Nottingham Forest", ...) which don't match football-data.co.uk's abbreviated
names ("Arsenal", "Man United", "Nott'm Forest", ...) used in the results data.
CLUB_NAME_MAP below reconciles the two so this can later be joined onto
standings_by_season.csv - add to it if a club/season is missing after joining.

Usage:
    python src/load_transfers.py
"""
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "transfers"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Transfermarkt club name -> football-data.co.uk club name.
# Only covers clubs appearing in the transfer files for 2010-11 onward;
# extend this if load_results.py reports an unmatched team after joining.
CLUB_NAME_MAP = {
    "Arsenal FC": "Arsenal",
    "Aston Villa": "Aston Villa",
    "AFC Bournemouth": "Bournemouth",
    "Brentford FC": "Brentford",
    "Brighton & Hove Albion": "Brighton",
    "Burnley FC": "Burnley",
    "Cardiff City": "Cardiff",
    "Chelsea FC": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "Everton FC": "Everton",
    "Fulham FC": "Fulham",
    "Huddersfield Town": "Huddersfield",
    "Hull City": "Hull",
    "Leeds United": "Leeds",
    "Leicester City": "Leicester",
    "Liverpool FC": "Liverpool",
    "Manchester City": "Man City",
    "Manchester United": "Man United",
    "Middlesbrough FC": "Middlesbrough",
    "Newcastle United": "Newcastle",
    "Norwich City": "Norwich",
    "Nottingham Forest": "Nott'm Forest",
    "Sheffield United": "Sheffield United",
    "Southampton FC": "Southampton",
    "Stoke City": "Stoke",
    "Sunderland AFC": "Sunderland",
    "Swansea City": "Swansea",
    "Tottenham Hotspur": "Tottenham",
    "Watford FC": "Watford",
    "West Bromwich Albion": "West Brom",
    "West Ham United": "West Ham",
    "Wigan Athletic": "Wigan",
    "Wolverhampton Wanderers": "Wolves",
    "Blackburn Rovers": "Blackburn",
    "Blackpool FC": "Blackpool",
    "Bolton Wanderers": "Bolton",
    "Birmingham City": "Birmingham",
    "Queens Park Rangers": "QPR",
    "Reading FC": "Reading",
    "Luton Town": "Luton",
    "Ipswich Town": "Ipswich",
}


def season_label(year: int) -> str:
    """2022 -> '2022-23'"""
    return f"{year}-{str(year + 1)[-2:]}"


def load_all_seasons() -> pd.DataFrame:
    frames = []
    for path in sorted(RAW_DIR.glob("*.csv")):
        year = int(path.stem)
        df = pd.read_csv(path)
        df["Season"] = season_label(year)
        frames.append(df)
    if not frames:
        raise FileNotFoundError(
            f"No transfer files found in {RAW_DIR} - copy season CSVs there first."
        )
    return pd.concat(frames, ignore_index=True)


def compute_spend_summary(transfers: pd.DataFrame) -> pd.DataFrame:
    transfers = transfers.copy()
    transfers["fee"] = transfers["fee"].fillna(0)

    spend = (
        transfers[transfers["movement"] == "in"]
        .groupby(["Season", "club"])["fee"].sum()
        .rename("gross_spend_eur")
    )
    income = (
        transfers[transfers["movement"] == "out"]
        .groupby(["Season", "club"])["fee"].sum()
        .rename("gross_income_eur")
    )
    summary = pd.concat([spend, income], axis=1).fillna(0).reset_index()
    summary["net_spend_eur"] = summary["gross_spend_eur"] - summary["gross_income_eur"]
    summary["Team"] = summary["club"].map(CLUB_NAME_MAP)

    unmapped = summary[summary["Team"].isna()]["club"].unique()
    if len(unmapped):
        print(
            "WARNING: these Transfermarkt club names have no entry in CLUB_NAME_MAP "
            f"and will not join onto results data: {sorted(unmapped)}"
        )
    return summary


def main():
    transfers = load_all_seasons()
    transfers.to_csv(OUT_DIR / "transfers_combined.csv", index=False)
    print(f"Wrote {len(transfers):,} transfer records -> data/processed/transfers_combined.csv")

    summary = compute_spend_summary(transfers)
    summary.to_csv(OUT_DIR / "spend_by_club_season.csv", index=False)
    print(f"Wrote {len(summary):,} club-seasons -> data/processed/spend_by_club_season.csv")


if __name__ == "__main__":
    main()
