from __future__ import annotations

import argparse
from pathlib import Path

from .data_client import YahooDataClient
from .pipeline import ScreenerConfig, ScreenerPipeline
from .reporting import resolve_fetched_output_path, resolve_output_path, write_fetched_csv, write_matches_csv
from .universe import load_sp500_symbols, load_symbols_from_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stock screener using Yahoo Finance data")
    parser.add_argument(
        "--symbols-csv",
        type=str,
        default=None,
        help="Optional CSV with a 'symbol' column. If omitted, S&P 500 is loaded.",
    )
    parser.add_argument(
        "--fallback-csv",
        type=str,
        default="config/sp500_fallback.csv",
        help="Fallback CSV used when S&P 500 loading fails.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output CSV path. Defaults to output/screener_matches_<timestamp>.csv",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional symbol limit for quick smoke runs")
    parser.add_argument("--max-retries", type=int, default=2, help="Retries per symbol when fetch fails")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="Seconds between retries")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.symbols_csv:
        symbols = load_symbols_from_csv(Path(args.symbols_csv))
    else:
        symbols = load_sp500_symbols(Path(args.fallback_csv))

    if args.limit is not None and args.limit > 0:
        symbols = symbols[: args.limit]

    config = ScreenerConfig(max_retries=args.max_retries, retry_delay_seconds=args.retry_delay)
    pipeline = ScreenerPipeline(data_client=YahooDataClient(), config=config)
    result = pipeline.run(symbols)

    output_path = resolve_output_path(args.output)
    write_matches_csv(result.matched_rows, output_path)
    fetched_output_path = resolve_fetched_output_path(output_path)
    write_fetched_csv(result.fetched_rows, fetched_output_path)

    print(f"Processed symbols: {result.total_symbols}")
    print(f"Fetched symbols: {result.fetched_symbols}")
    print(f"Matched symbols: {len(result.matched_rows)}")
    if result.skipped_reasons:
        print("Skipped reasons:")
        for reason, count in sorted(result.skipped_reasons.items()):
            print(f"  - {reason}: {count}")
    print(f"Matches CSV written to: {output_path}")
    print(f"Fetched data CSV written to: {fetched_output_path}")


if __name__ == "__main__":
    main()
