from pathlib import Path

from screener.reporting import resolve_fetched_output_path


def test_resolve_fetched_output_path_for_default_name() -> None:
    path = Path("output/screener_matches_20260701_215345.csv")

    fetched_path = resolve_fetched_output_path(path)

    assert fetched_path == Path("output/fetched_data_20260701_215345.csv")


def test_resolve_fetched_output_path_for_custom_name() -> None:
    path = Path("output/custom.csv")

    fetched_path = resolve_fetched_output_path(path)

    assert fetched_path == Path("output/custom_fetched_data.csv")
