from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class StockSnapshot:
    symbol: str
    as_of_date: date
    current_close: float
    previous_close: float
    week52_low: float
    week52_high: float


@dataclass(frozen=True)
class FetchResult:
    symbol: str
    snapshot: Optional[StockSnapshot]
    error: Optional[str] = None
