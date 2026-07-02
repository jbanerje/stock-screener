from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf

from .models import FetchResult, StockSnapshot


@dataclass(frozen=True)
class YahooDataClient:
    history_period: str = "1y"
    interval: str = "1d"

    def fetch_snapshot(self, symbol: str) -> FetchResult:
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(
                period=self.history_period,
                interval=self.interval,
                auto_adjust=False,
                actions=False,
            )
        except (OSError, RuntimeError, ValueError, TypeError, KeyError, AttributeError) as exc:  # pragma: no cover - network/remote error path
            return FetchResult(symbol=symbol, snapshot=None, error=f"request_failed: {exc}")

        if history is None or history.empty:
            return FetchResult(symbol=symbol, snapshot=None, error="empty_history")

        close_series = history.get("Close")
        if close_series is None:
            return FetchResult(symbol=symbol, snapshot=None, error="missing_close_column")

        close_series = close_series.dropna()
        if len(close_series) < 2:
            return FetchResult(symbol=symbol, snapshot=None, error="insufficient_close_history")

        current_close = float(close_series.iloc[-1])
        previous_close = float(close_series.iloc[-2])

        lookback = close_series.tail(252)
        week52_low = float(lookback.min())
        week52_high = float(lookback.max())

        if week52_low <= 0 or week52_high <= 0:
            return FetchResult(symbol=symbol, snapshot=None, error="invalid_52w_values")

        if week52_high < week52_low:
            return FetchResult(symbol=symbol, snapshot=None, error="inverted_52w_range")

        as_of_index = history.index[-1]
        as_of_date = pd.Timestamp(as_of_index).date()

        snapshot = StockSnapshot(
            symbol=symbol,
            as_of_date=as_of_date,
            current_close=current_close,
            previous_close=previous_close,
            week52_low=week52_low,
            week52_high=week52_high,
        )
        return FetchResult(symbol=symbol, snapshot=snapshot, error=None)
