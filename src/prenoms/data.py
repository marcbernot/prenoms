"""Bundled sample data.

Files under src/prenoms/data/ ship in the wheel, so they exist in the browser too.
"""

import importlib.util
from importlib.resources import files

import pandas as pd


def load_example() -> pd.DataFrame:
    """Return the small bundled example table (date, series, value)."""
    with files("prenoms").joinpath("data/example.csv").open() as f:
        return pd.read_csv(f, parse_dates=["date"])


def _read_parquet(path, engine=None) -> pd.DataFrame:
    """Read a Parquet file with pyarrow when it is installed, else with DuckDB.

    The xeus-python browser environment has no pyarrow (its emscripten-forge build hangs when
    converting to pandas); DuckDB reads Parquet there. ``engine`` forces "pyarrow" or "duckdb".
    """
    if engine is None:
        engine = "pyarrow" if importlib.util.find_spec("pyarrow") else "duckdb"
    if engine == "pyarrow":
        return pd.read_parquet(path)
    import duckdb

    df = duckdb.read_parquet(str(path)).df()
    text = df.select_dtypes(include=["object", "string"]).columns
    return df.astype({c: "str" for c in text})


def load_nat2020(path="nat2020.pq") -> pd.DataFrame:
    """Load the INSEE national first-names file (births per first name, sex and year).

    Columns: ``sexe`` (1 = boy, 2 = girl), ``preusuel`` (first name), ``annais`` (year of birth,
    nullable Int; INSEE's "XXXX" = unknown year becomes <NA>), ``nombre`` (births).
    Rows ``_PRENOMS_RARES`` aggregate the rare names of each year.
    """
    df = _read_parquet(path)
    df["annais"] = pd.to_numeric(df["annais"], errors="coerce").astype("Int16")
    return df
