"""Minimal local data app: filter, table, chart. Data is loaded on demand.

By default nothing is persisted; set DISK_CACHE = True to also cache the query
result as parquet under the OS temp directory (aggregate, non-sensitive data
only). Edit TITLE, QUERY, and the filter and chart columns for your data.
"""
import hashlib
import tempfile
from pathlib import Path

import polars as pl
import streamlit as st

from datasource import load_frame

TITLE = "Data App"
QUERY = "SELECT 1 AS n, 'example' AS label"  # ignored by file/snapshot datasources

# In-memory cache lifetime. The query runs once and every rerun (filtering, chart
# changes) reads the cached frame. Raise this for slow-changing data: 3600 = 1h,
# 86400 = 1 day, None = cache until the app process restarts.
CACHE_TTL = 3600

# Opt-in disk cache. Streamlit's built-in persist="disk" always writes to
# ~/.streamlit/cache and is only TTL-bound. To get "survives app restarts, cleared
# on machine reboot", cache the result as parquet under the OS temp directory.
DISK_CACHE = False

st.set_page_config(page_title=TITLE, layout="wide")
st.title(TITLE)


def _load_query() -> pl.DataFrame:
    if not DISK_CACHE:
        return load_frame(QUERY)
    key = hashlib.sha1(QUERY.encode()).hexdigest()[:16]
    fp = Path(tempfile.gettempdir()) / f"dataapp_{key}.parquet"
    if fp.exists():
        return pl.read_parquet(fp)
    df = load_frame(QUERY)
    df.write_parquet(fp)
    return df


@st.cache_data(ttl=CACHE_TTL)
def get_data() -> pl.DataFrame:
    return _load_query()


df = get_data()

with st.sidebar:
    st.header("Filters")
    search = st.text_input("Filter by term")

view = df
if search:
    mask = pl.any_horizontal(
        pl.col(c).cast(pl.Utf8).str.contains(f"(?i){search}") for c in df.columns
    )
    view = df.filter(mask)

st.caption(f"{view.height} rows")
st.dataframe(view, use_container_width=True)

num_cols = [c for c, t in zip(df.columns, df.dtypes) if t.is_numeric()]
if num_cols:
    with st.expander("Chart", expanded=True):
        col = st.selectbox("Numeric column", num_cols)
        st.bar_chart(view.to_pandas().set_index(view.columns[0])[col])
