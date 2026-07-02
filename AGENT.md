# AGENT.md

This document defines required project details for contributors and coding agents working in this repository.

## Project Objective
Create and maintain a Python stock screener that:
- pulls a symbol universe from Yahoo-compatible sources,
- evaluates strict downside and 52-week proximity criteria,
- exports matching symbols to CSV for manual review.

## Non-Negotiable Business Rules
A stock is a match only if:
1. current close is at least 15% lower than previous close, and
2. (current close is 1-5% above 52-week low) OR (current close is 1-2% below 52-week high).

Use inclusive boundaries for all thresholds.

## Repository Structure
- main.py: root CLI entrypoint.
- screener/cli.py: argument parsing and run orchestration.
- screener/data_client.py: Yahoo history fetch and snapshot normalization.
- screener/universe.py: S&P 500 loading and fallback handling.
- screener/filters.py: formulas and match decision logic.
- screener/pipeline.py: retry, screening loop, and row assembly.
- screener/reporting.py: output path resolution and CSV writing.
- tests/: unit and pipeline tests.
- config/sp500_fallback.csv: backup symbol list.

## Runtime and Commands
Environment:
- Python 3.14 virtual environment under .venv

Setup:
- pip install -r requirements.txt

Run:
- python main.py
- python main.py --limit 10
- python main.py --symbols-csv config/sp500_fallback.csv --output output/custom.csv

Test:
- pytest -q

## Output Contract
CSV columns must include:
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

## Data and Reliability Guidelines
- Prefer resilience over hard-fail on individual symbol errors.
- Track skipped symbols with reason counts.
- Keep fallback universe available for upstream parsing failures.
- Do not silently alter threshold semantics.

## Coding Guidelines
- Keep changes minimal and localized.
- Preserve CLI behavior and output schema unless explicitly requested.
- Add/adjust tests for every rule or behavioral change.
- Avoid introducing unnecessary dependencies.

## Completion Criteria for Changes
A change is complete when:
1. tests pass,
2. CLI smoke run succeeds,
3. output schema and business rules remain correct,
4. README and this file reflect any user-visible behavior changes.
