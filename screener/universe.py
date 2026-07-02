from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

SP500_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def _normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper().replace(".", "-")


def _dedupe_keep_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def load_sp500_symbols(fallback_csv_path: Path) -> list[str]:
    try:
        table = pd.read_html(SP500_WIKI_URL, attrs={"id": "constituents"})[0]
        symbols = [_normalize_symbol(symbol) for symbol in table["Symbol"].astype(str).tolist()]
        symbols = _dedupe_keep_order(symbols)
        if symbols:
            return symbols
    except (ValueError, ImportError, OSError):
        pass

    return load_symbols_from_csv(fallback_csv_path)


def load_symbols_from_csv(csv_path: Path) -> list[str]:
    frame = pd.read_csv(csv_path)
    if "symbol" not in frame.columns:
        raise ValueError("CSV file must contain a 'symbol' column")

    symbols = [_normalize_symbol(symbol) for symbol in frame["symbol"].astype(str).tolist()]
    symbols = [symbol for symbol in symbols if symbol]
    return _dedupe_keep_order(symbols)
