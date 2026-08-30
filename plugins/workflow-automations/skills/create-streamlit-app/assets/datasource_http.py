"""Datasource: HTTP endpoint returning JSON or CSV, read into Polars.

Set DATA_URL in the environment. Pass any auth token through the environment
(API_TOKEN) rather than writing it into this file.
"""
import io
import os

import polars as pl
import requests

DATA_URL = os.environ.get("DATA_URL", "https://example.invalid/data.json")


def load_frame(query: str | None = None) -> pl.DataFrame:
    headers = {}
    token = os.environ.get("API_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(DATA_URL, headers=headers, timeout=60)
    response.raise_for_status()
    if "csv" in response.headers.get("content-type", ""):
        return pl.read_csv(io.StringIO(response.text))
    return pl.DataFrame(response.json())
