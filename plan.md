## Plan: Python Stock Screener

Build a Python CLI screener that pulls the S&P 500 universe, computes daily drop and 52-week distance metrics from Yahoo Finance data, and exports only matching symbols to CSV.

### Scope Decisions
- Universe: S&P 500 (with local fallback file).
- Run mode: manual CLI.
- Output: CSV only.
- Rule: stock must satisfy 15% drop AND at least one 52-week proximity condition.

### Screening Rules
A symbol is a match when all are true:
1. Close drop from previous close is at least 15%.
2. Either:
   - current close is 0-10% above 52-week low, or
   - current close is 0-10% below 52-week high.

### Implementation Phases
1. Scaffold and tooling.
- Create package, tests, config, output folders.
- Add requirements and baseline project docs.

2. Data ingestion and normalization.
- Load S&P 500 symbols from Wikipedia constituents table.
- Fallback to local CSV if remote fetch/parsing fails.
- Fetch daily history from Yahoo via yfinance.
- Derive latest close, previous close, 52-week low/high.

3. Screening logic.
- Compute drop percentage and 52-week distance percentages.
- Apply inclusive thresholds and boolean composition.
- Guard invalid denominators and missing values.

4. Reporting and CLI UX.
- Generate CSV with match rows only.
- Print concise run summary (processed, fetched, matched, skipped reasons).
- Use timestamped output path when not explicitly provided.

5. Verification.
- Unit tests for threshold boundaries.
- Mock-based tests for data fetch behavior.
- Pipeline test for match and skip accounting.
- Smoke run with symbol limit.

### Current File Map
- main entry point: main.py
- package: screener/
- tests: tests/
- fallback symbols: config/sp500_fallback.csv
- docs: README.md

### Verification Checklist
1. Install dependencies.
2. Run tests: pytest -q
3. Run smoke CLI: python main.py --limit 10
4. Review generated CSV under output/

### Known Risks and Notes
- Yahoo data can be delayed and occasionally incomplete.
- Wikipedia table schema can change; fallback CSV remains available.
- Use raw values for filtering and rounded values for reporting.
