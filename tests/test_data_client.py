from __future__ import annotations

import pandas as pd

from screener.data_client import YahooDataClient


class _FakeTicker:
    def __init__(self, history_frame: pd.DataFrame) -> None:
        self._history_frame = history_frame

    def history(self, **_: object) -> pd.DataFrame:
        return self._history_frame


def test_fetch_snapshot_success(monkeypatch) -> None:
    index = pd.to_datetime(["2026-06-30", "2026-07-01"])
    frame = pd.DataFrame({"Close": [100.0, 85.0]}, index=index)

    monkeypatch.setattr("screener.data_client.yf.Ticker", lambda symbol: _FakeTicker(frame))

    result = YahooDataClient().fetch_snapshot("TEST")

    assert result.error is None
    assert result.snapshot is not None
    assert result.snapshot.previous_close == 100.0
    assert result.snapshot.current_close == 85.0


def test_fetch_snapshot_insufficient_history(monkeypatch) -> None:
    index = pd.to_datetime(["2026-07-01"])
    frame = pd.DataFrame({"Close": [85.0]}, index=index)

    monkeypatch.setattr("screener.data_client.yf.Ticker", lambda symbol: _FakeTicker(frame))

    result = YahooDataClient().fetch_snapshot("TEST")

    assert result.snapshot is None
    assert result.error == "insufficient_close_history"
