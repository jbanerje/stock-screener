from datetime import date

import pytest

from screener.filters import evaluate_snapshot  # type: ignore[reportMissingImports]
from screener.models import StockSnapshot  # type: ignore[reportMissingImports]


def _snapshot(current: float, previous: float, low: float, high: float) -> StockSnapshot:
    return StockSnapshot(
        symbol="TEST",
        as_of_date=date(2026, 1, 1),
        current_close=current,
        previous_close=previous,
        week52_low=low,
        week52_high=high,
    )


def test_matches_on_exact_boundaries() -> None:
    # 15% drop: 220 -> 187, 10% above low: 187 vs 170
    snapshot = _snapshot(current=187.0, previous=220.0, low=170.0, high=300.0)
    decision = evaluate_snapshot(snapshot)

    assert decision.is_match is True
    assert decision.metrics.is_drop_15pct_or_more is True


def test_matches_when_within_low_range_not_exact_10pct() -> None:
    # 15% drop: 220 -> 187, 4.6403% above low: 187 vs 178.67
    snapshot = _snapshot(current=187.0, previous=220.0, low=178.67, high=300.0)
    decision = evaluate_snapshot(snapshot)

    assert decision.is_match is True
    assert decision.metrics.is_near_52w_low is True


def test_rejects_below_drop_threshold() -> None:
    snapshot = _snapshot(current=85.01, previous=100.0, low=84.2, high=86.0)
    decision = evaluate_snapshot(snapshot)

    assert decision.metrics.is_drop_15pct_or_more is False
    assert decision.is_match is False


def test_rejects_if_not_near_low_or_high() -> None:
    snapshot = _snapshot(current=85.0, previous=100.0, low=70.0, high=120.0)
    decision = evaluate_snapshot(snapshot)

    assert decision.metrics.is_drop_15pct_or_more is True
    assert decision.metrics.is_near_52w_low is False
    assert decision.metrics.is_near_52w_high is False
    assert decision.is_match is False


def test_invalid_denominator_raises() -> None:
    snapshot = _snapshot(current=10.0, previous=0.0, low=9.0, high=11.0)
    with pytest.raises(ValueError):
        evaluate_snapshot(snapshot)
