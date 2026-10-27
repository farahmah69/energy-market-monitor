# Energy Market Monitor

A Python automation project that downloads Brent crude oil prices from FRED (`DCOILBRENTEU`, sourced from EIA), cleans historical observations, calculates percentage returns, 7- and 30-observation moving averages, and 30-observation return volatility. It exports a four-panel PNG dashboard, CSV data, and a plain-text analytical summary.

## Run locally

```bash
python -m pip install -r requirements.txt
python energy_monitor.py
```

Outputs appear in `output/`. Internet access is required.

## Automated schedule

GitHub Actions runs on weekdays at 05:00 UTC (09:00 Dubai), and can also be started manually from **Actions → Energy Market Monitor → Run workflow**. Download the `energy-market-report` artifact from a completed workflow run. Scheduled runs may be delayed or skipped by GitHub, and published data may lag the run date.

## Interpretation

Moving averages are calculated over available observations, not calendar days. Volatility is the rolling standard deviation of 30 percentage returns, not annualized. The moving-average signal is descriptive and not a trading recommendation.

## Data source

[FRED Brent Crude Oil Prices: Europe (DCOILBRENTEU)](https://fred.stlouisfed.org/series/DCOILBRENTEU)
