"""Datasource: local file (CSV, Parquet, NDJSON) read into Polars.

Set DATA_PATH in the environment or edit the default below. The `query`
argument is ignored; filtering happens in the app.
"""
import os
import pathlib

import polars as pl

DATA_PATH = os.environ.get("DATA_PATH", "data.csv")

_READERS = {
    ".csv": pl.read_csv,
    ".tsv": lambda p: pl.read_csv(p, separator="\t"),
    ".parquet": pl.read_parquet,
    ".ndjson": pl.read_ndjson,
    ".jsonl": pl.read_ndjson,
    ".json": pl.read_json,
}


def load_frame(query: str | None = None) -> pl.DataFrame:
    path = pathlib.Path(DATA_PATH)
    reader = _READERS.get(path.suffix.lower())
    if reader is None:
        raise ValueError(f"unsupported data file extension: {path.suffix}")
    return reader(path)
