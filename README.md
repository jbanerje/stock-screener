# Stock Screener (Yahoo Finance)

    This project screens S&P 500 stocks using Yahoo Finance data and writes two CSV outputs.

For screener matches output, a stock is included when match_rule is not no_match.
This means current close is 0-10% above the 52-week low OR 0-10% below the 52-week high.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Default run (loads S&P 500 symbols, writes CSV files in output/):

```bash
python main.py
```

Quick smoke run with a symbol limit:

```bash
python main.py --limit 10
```

Use your own symbol file (CSV with a symbol column):

```bash
python3 main.py --symbols-csv config/sp500_fallback.csv --output output/custom.csv
```

## Output files

- Matches file: output/screener_matches_<timestamp>.csv
- Fetched data file: output/fetched_data_<timestamp>.csv

If you pass --output output/custom.csv, the second file is written as output/custom_fetched_data.csv.

## Matches file columns

- symbol
- as_of_date
- current_close
- previous_close
- drop_pct
- week52_low
- week52_high
- distance_from_low_pct
- distance_to_high_pct
- match_rule

## Fetched data file columns

- symbol
- as_of_date
- current_close
- previous_close
- drop_pct
- week52_low
- week52_high
- distance_from_low_pct
- distance_to_high_pct
- prev_day_change
- match_rule

`prev_day_change` is true when absolute day-over-day change is at least 15% and is independent of the 52-week low/high proximity rules.

## Tests

```bash
pytest -q
```

## Notes

- Yahoo Finance data can be delayed and occasionally missing for symbols.
- S&P 500 list is loaded from Wikipedia; if unavailable, fallback symbols are read from config/sp500_fallback.csv.
