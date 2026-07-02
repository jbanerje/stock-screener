from __future__ import annotations

from dataclasses import dataclass
from math import isnan

from .models import StockSnapshot


@dataclass(frozen=True)
class FilterMetrics:
    drop_pct: float
    distance_from_low_pct: float
    distance_to_high_pct: float
    is_drop_15pct_or_more: bool
    is_near_52w_low: bool
    is_near_52w_high: bool


@dataclass(frozen=True)
class FilterDecision:
    is_match: bool
    match_rule: str
    metrics: FilterMetrics


def compute_drop_pct(previous_close: float, current_close: float) -> float:
    if previous_close <= 0:
        raise ValueError("previous_close must be greater than zero")
    return ((current_close - previous_close) / previous_close) * 100.0


def compute_distance_from_low_pct(current_close: float, week52_low: float) -> float:
    if week52_low <= 0:
        raise ValueError("week52_low must be greater than zero")
    return ((current_close - week52_low) / week52_low) * 100.0


def compute_distance_to_high_pct(current_close: float, week52_high: float) -> float:
    if week52_high <= 0:
        raise ValueError("week52_high must be greater than zero")
    return ((week52_high - current_close) / week52_high) * 100.0


def _is_finite_number(value: float) -> bool:
    return not isnan(value) and value != float("inf") and value != float("-inf")


def evaluate_snapshot(
    snapshot: StockSnapshot,
    drop_threshold_pct: float = 15.0,
    low_range_min_pct: float = 0.0,
    low_range_max_pct: float = 10.0,
    high_range_min_pct: float = 0.0,
    high_range_max_pct: float = 10.0,
) -> FilterDecision:
    drop_pct = compute_drop_pct(snapshot.previous_close, snapshot.current_close)
    distance_from_low_pct = compute_distance_from_low_pct(snapshot.current_close, snapshot.week52_low)
    distance_to_high_pct = compute_distance_to_high_pct(snapshot.current_close, snapshot.week52_high)

    values = [drop_pct, distance_from_low_pct, distance_to_high_pct]
    if not all(_is_finite_number(value) for value in values):
        raise ValueError("Metrics contain non-finite values")

    is_drop_15pct_or_more = drop_pct <= -drop_threshold_pct
    is_near_52w_low = low_range_min_pct <= distance_from_low_pct <= low_range_max_pct
    is_near_52w_high = high_range_min_pct <= distance_to_high_pct <= high_range_max_pct

    is_match = is_drop_15pct_or_more and (is_near_52w_low or is_near_52w_high)

    if is_near_52w_low and is_near_52w_high:
        match_rule = "near_52w_low_and_high"
    elif is_near_52w_low:
        match_rule = "near_52w_low"
    elif is_near_52w_high:
        match_rule = "near_52w_high"
    else:
        match_rule = "no_match"

    return FilterDecision(
        is_match=is_match,
        match_rule=match_rule,
        metrics=FilterMetrics(
            drop_pct=drop_pct,
            distance_from_low_pct=distance_from_low_pct,
            distance_to_high_pct=distance_to_high_pct,
            is_drop_15pct_or_more=is_drop_15pct_or_more,
            is_near_52w_low=is_near_52w_low,
            is_near_52w_high=is_near_52w_high,
        ),
    )
