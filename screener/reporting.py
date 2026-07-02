from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


MATCHES_COLUMNS = [
    "symbol",
    "as_of_date",
    "current_close",
    "previous_close",
    "drop_pct",
    "week52_low",
    "week52_high",
    "distance_from_low_pct",
    "distance_to_high_pct",
    "match_rule",
]

FETCHED_COLUMNS = [
    "symbol",
    "as_of_date",
    "current_close",
    "previous_close",
    "drop_pct",
    "week52_low",
    "week52_high",
    "distance_from_low_pct",
    "distance_to_high_pct",
    "prev_day_change",
    "match_rule",
]


def resolve_output_path(output_arg: str | None) -> Path:
    if output_arg:
        return Path(output_arg)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("output") / f"screener_matches_{timestamp}.csv"


def resolve_fetched_output_path(matches_output_path: Path) -> Path:
    suffix = matches_output_path.suffix or ".csv"
    stem = matches_output_path.stem
    if stem.startswith("screener_matches_"):
        fetched_stem = stem.replace("screener_matches_", "fetched_data_", 1)
    else:
        fetched_stem = f"{stem}_fetched_data"
    return matches_output_path.with_name(f"{fetched_stem}{suffix}")


def write_matches_csv(rows: list[dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)

    if frame.empty:
        frame = pd.DataFrame(columns=MATCHES_COLUMNS)

    frame.to_csv(output_path, index=False)
    return output_path


def write_fetched_csv(rows: list[dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)

    if frame.empty:
        frame = pd.DataFrame(columns=FETCHED_COLUMNS)

    frame.to_csv(output_path, index=False)
    return output_path
