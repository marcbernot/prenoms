from pathlib import Path

import pytest

import prenoms


def test_example_data():
    df = prenoms.load_example()
    assert list(df.columns) == ["date", "series", "value"]
    assert sorted(df["series"].unique()) == ["alpha", "beta", "gamma"]


def test_runtime_flag():
    assert prenoms.IN_BROWSER is False


NAT2020 = Path(__file__).parents[1] / "notebooks" / "nat2020.pq"


@pytest.mark.skipif(not NAT2020.exists(), reason="run `pixi run get-data` first")
def test_nat2020():
    df = prenoms.load_nat2020(NAT2020)
    assert list(df.columns) == ["sexe", "preusuel", "annais", "nombre"]
    assert df["annais"].min() == 1900 and df["annais"].max() == 2020


@pytest.mark.skipif(not NAT2020.exists(), reason="run `pixi run get-data` first")
def test_duckdb_reader_matches_pyarrow():
    from pandas.testing import assert_frame_equal

    from prenoms.data import _read_parquet

    assert_frame_equal(_read_parquet(NAT2020, "duckdb"), _read_parquet(NAT2020, "pyarrow"))
