"""Datasource: inline snapshot, no live connection.

Use when the data is a small aggregate the agent or the user already holds.
Replace _ROWS with the actual records. Nothing hits the network.
"""
import polars as pl

_ROWS = [
    {"label": "a", "value": 1},
    {"label": "b", "value": 2},
]


def load_frame(query: str | None = None) -> pl.DataFrame:
    return pl.DataFrame(_ROWS)
