"""Datasource: SQL database via a connection URI, read into Polars.

Works with any database Polars can reach through connectorx or SQLAlchemy,
for example postgresql://, mysql://, sqlite://.

Env: DATABASE_URL. Never hardcode credentials in this file.
Install the matching driver, for example `connectorx` or `sqlalchemy` plus a DBAPI.
"""
import os

import polars as pl


def load_frame(query: str) -> pl.DataFrame:
    uri = os.environ["DATABASE_URL"]
    return pl.read_database_uri(query=query, uri=uri)
