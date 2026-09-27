# Does Spending Buy Success?
Premier League wage bills, transfer spend, and league performance, 2010-11 to present.

## Research questions
1. **Primary:** How strongly does wage bill correlate with final league position,
   and does that relationship hold across the whole table or only at the extremes
   (top-six vs. rest)?
2. How strongly does wage bill correlate with points compared to net transfer spend?
   (Treated as a secondary, caveated question - wage bill and transfer spend are
   likely collinear, so "which matters more" is a harder claim to make cleanly.)
3. Supporting: how much does spending efficiency (points per £m of wage bill) vary
   between clubs?
4. Future work (not in v1): has the strength of the spend-performance relationship
   changed over time as broadcast revenue has grown? Flagged as risky with ~15
   seasons of data - would need a proper structural-break test, not just eyeballing
   a trend line.

## Data sources
- **Results / points / goals:** [football-data.co.uk](https://www.football-data.co.uk/englandm.php)
  - `src/fetch_results.py` downloads one CSV per season into `data/raw/results/`.
  - `data/raw/results/1011_E0.csv` in this repo is a small **sample** (a handful of
    matches) just to keep the schema pinned down for development - run
    `fetch_results.py` on a machine with normal internet access to pull full seasons.
- **Transfer spend / squad market value:** [Transfermarkt](https://www.transfermarkt.com),
  via the [transfermarkt-datasets](https://github.com/dcaribou/transfermarkt-datasets)
  project or direct scraping - not yet implemented, see "Next steps" below.
- **Wage bills:** no clean free bulk source exists. Plan is to hand-compile a season-
  by-season table from club annual accounts / Companies House filings for the clubs
  and seasons in scope, since this is inherently a manual, source-by-source task.
  Not yet implemented.

## Project layout
```
data/
  raw/results/        one CSV per season from football-data.co.uk
  raw/transfers/       (empty - transfer spend data goes here)
  raw/wages/           (empty - hand-compiled wage bill data goes here)
  processed/          cleaned, combined datasets ready for analysis
src/
  fetch_results.py     downloads season results CSVs
  load_results.py      combines seasons, derives final league tables
notebooks/             exploratory analysis (to be added)
```

## Setup
```
pip install -r requirements.txt
python src/fetch_results.py   # needs real internet access - see note above
python src/load_results.py
```

## Status
- [x] Results data pipeline (fetch + combine + derive standings)
- [ ] Transfer spend data pipeline
- [ ] Wage bill data (manual compilation)
- [ ] Join spend/wages onto standings, inflation-adjust to real terms
- [ ] EDA: scatter plots, correlation by table tier
- [ ] Linear regression baseline + random forest comparison
- [ ] Robustness checks (exclude relegated clubs, check for outlier-driven results)
- [ ] Write-up

## Notes / caveats to keep in the final write-up
- Wage bill and transfer spend are likely collinear - check correlation between
  them before making any claim about which one "matters more."
- Watch for one big-spending underperformer driving the whole correlation - check
  robustness with and without outliers.
- Scope is 2010-11 onward because reliable wage bill data gets hard to source
  before then.
