from dataclasses import dataclass
from datetime import date

from screener.models import FetchResult, StockSnapshot  # type: ignore[reportMissingImports]
from screener.pipeline import ScreenerConfig, ScreenerPipeline  # type: ignore[reportMissingImports]


@dataclass
class FakeDataClient:
    responses: dict[str, FetchResult]

    def fetch_snapshot(self, symbol: str) -> FetchResult:
        return self.responses.get(symbol, FetchResult(symbol=symbol, snapshot=None, error="missing_symbol"))


def _snapshot(symbol: str, current: float, previous: float, low: float, high: float) -> StockSnapshot:
    return StockSnapshot(
        symbol=symbol,
        as_of_date=date(2026, 1, 1),
        current_close=current,
        previous_close=previous,
        week52_low=low,
        week52_high=high,
    )


def test_pipeline_collects_matches_and_skips() -> None:
    responses = {
        "AAA": FetchResult(symbol="AAA", snapshot=_snapshot("AAA", 187.0, 220.0, 170.0, 300.0), error=None),
        "BBB": FetchResult(symbol="BBB", snapshot=_snapshot("BBB", 95.0, 100.0, 90.0, 100.0), error=None),
        "CCC": FetchResult(symbol="CCC", snapshot=None, error="empty_history"),
    }

    pipeline = ScreenerPipeline(data_client=FakeDataClient(responses), config=ScreenerConfig(max_retries=0))
    result = pipeline.run(["AAA", "BBB", "CCC", "DDD"])

    assert result.total_symbols == 4
    assert result.fetched_symbols == 2
    assert len(result.fetched_rows) == 2
    assert [row["symbol"] for row in result.fetched_rows] == ["AAA", "BBB"]
    assert result.fetched_rows[0]["prev_day_change"] is True
    assert result.fetched_rows[1]["prev_day_change"] is False
    assert len(result.matched_rows) == 2
    assert [row["symbol"] for row in result.matched_rows] == ["AAA", "BBB"]
    assert result.skipped_reasons["empty_history"] == 1
    assert result.skipped_reasons["missing_symbol"] == 1
