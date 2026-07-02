from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Protocol

from .filters import evaluate_snapshot
from .models import FetchResult, StockSnapshot


class DataClient(Protocol):
    def fetch_snapshot(self, symbol: str) -> FetchResult:
        ...


@dataclass(frozen=True)
class ScreenerConfig:
    drop_threshold_pct: float = 15.0
    low_range_min_pct: float = 0.0
    low_range_max_pct: float = 10.0
    high_range_min_pct: float = 0.0
    high_range_max_pct: float = 10.0
    max_retries: int = 2
    retry_delay_seconds: float = 1.0


@dataclass(frozen=True)
class PipelineResult:
    matched_rows: list[dict[str, Any]]
    fetched_rows: list[dict[str, Any]]
    total_symbols: int
    fetched_symbols: int
    skipped_reasons: dict[str, int]


class ScreenerPipeline:
    def __init__(self, data_client: DataClient, config: ScreenerConfig) -> None:
        self.data_client = data_client
        self.config = config

    def run(self, symbols: list[str]) -> PipelineResult:
        matched_rows: list[dict[str, Any]] = []
        fetched_rows: list[dict[str, Any]] = []
        skipped_reasons: dict[str, int] = {}
        fetched_symbols = 0

        for symbol in symbols:
            fetch_result = self._fetch_with_retry(symbol)
            if fetch_result.snapshot is None:
                reason = fetch_result.error or "unknown_fetch_error"
                skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1
                continue

            fetched_symbols += 1
            decision = evaluate_snapshot(
                fetch_result.snapshot,
                drop_threshold_pct=self.config.drop_threshold_pct,
                low_range_min_pct=self.config.low_range_min_pct,
                low_range_max_pct=self.config.low_range_max_pct,
                high_range_min_pct=self.config.high_range_min_pct,
                high_range_max_pct=self.config.high_range_max_pct,
            )

            prev_day_change = abs(decision.metrics.drop_pct) >= self.config.drop_threshold_pct
            fetched_rows.append(self._build_fetched_row(fetch_result.snapshot, prev_day_change, decision.match_rule, decision.metrics))

            if decision.match_rule == "no_match":
                continue

            matched_rows.append(self._build_row(fetch_result.snapshot, decision.match_rule, decision.metrics))

        return PipelineResult(
            matched_rows=matched_rows,
            fetched_rows=fetched_rows,
            total_symbols=len(symbols),
            fetched_symbols=fetched_symbols,
            skipped_reasons=skipped_reasons,
        )

    def _fetch_with_retry(self, symbol: str) -> FetchResult:
        attempts = self.config.max_retries + 1
        last_result: FetchResult | None = None

        for attempt in range(attempts):
            result = self.data_client.fetch_snapshot(symbol)
            if result.snapshot is not None:
                return result
            last_result = result
            if attempt < attempts - 1:
                time.sleep(self.config.retry_delay_seconds)

        return last_result or FetchResult(symbol=symbol, snapshot=None, error="unknown_fetch_error")

    @staticmethod
    def _build_row(snapshot: StockSnapshot, match_rule: str, metrics: Any) -> dict[str, Any]:
        return {
            "symbol": snapshot.symbol,
            "as_of_date": snapshot.as_of_date.isoformat(),
            "current_close": round(snapshot.current_close, 4),
            "previous_close": round(snapshot.previous_close, 4),
            "drop_pct": round(metrics.drop_pct, 4),
            "week52_low": round(snapshot.week52_low, 4),
            "week52_high": round(snapshot.week52_high, 4),
            "distance_from_low_pct": round(metrics.distance_from_low_pct, 4),
            "distance_to_high_pct": round(metrics.distance_to_high_pct, 4),
            "match_rule": match_rule,
        }

    @staticmethod
    def _build_fetched_row(snapshot: StockSnapshot, prev_day_change: bool, match_rule: str, metrics: Any) -> dict[str, Any]:
        return {
            "symbol": snapshot.symbol,
            "as_of_date": snapshot.as_of_date.isoformat(),
            "current_close": round(snapshot.current_close, 4),
            "previous_close": round(snapshot.previous_close, 4),
            "drop_pct": round(metrics.drop_pct, 4),
            "week52_low": round(snapshot.week52_low, 4),
            "week52_high": round(snapshot.week52_high, 4),
            "distance_from_low_pct": round(metrics.distance_from_low_pct, 4),
            "distance_to_high_pct": round(metrics.distance_to_high_pct, 4),
            "prev_day_change": prev_day_change,
            "match_rule": match_rule,
        }
