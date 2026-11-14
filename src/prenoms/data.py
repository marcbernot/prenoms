"""Bundled sample data.

Files under src/prenoms/data/ ship in the wheel, so they exist in the browser too.
"""

from importlib.resources import files

import pandas as pd


def load_example() -> pd.DataFrame:
    """Return the small bundled example table (date, series, value)."""
    with files("prenoms").joinpath("data/example.csv").open() as f:
        return pd.read_csv(f, parse_dates=["date"])


def load_nat2020(path="nat2020.pq") -> pd.DataFrame:
    """Load the INSEE national first-names file (births per first name, sex and year).

    Columns: ``sexe`` (1 = boy, 2 = girl), ``preusuel`` (first name), ``annais`` (year of birth,
    nullable Int; INSEE's "XXXX" = unknown year becomes <NA>), ``nombre`` (births).
    Rows ``_PRENOMS_RARES`` aggregate the rare names of each year.
    """
    df = pd.read_parquet(path)
    df["annais"] = pd.to_numeric(df["annais"], errors="coerce").astype("Int16")
    return df
