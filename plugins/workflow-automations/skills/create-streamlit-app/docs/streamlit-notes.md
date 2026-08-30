# Streamlit notes for a growing app

Read this only when the app outgrows the scaffold in `assets/app_template.py`.

## Multiple pages

Use the `st.Page` and `st.navigation` API to control sidebar labels, icons and order:

```python
st.navigation([
    st.Page("pages/overview.py", title="Overview", default=True),
    st.Page("pages/detail.py", title="Detail"),
]).run()
```

## Selection state

Every widget interaction reruns the script from the top, so local variables reset. Keep a selected row or id in `st.session_state`.

Dataframe rows are not clickable widgets. To select a row, either render an explicit selector (`st.selectbox` over the key column) or use `st.dataframe(..., on_select="rerun", selection_mode="single-row")` and read the selection from the returned object.

## Cache tuning

`CACHE_TTL` in the template controls the in-memory cache: `3600` for hourly data, `86400` for daily, `None` to cache until the process restarts.

`@st.cache_data(persist="disk")` survives restarts but always writes to `~/.streamlit/cache` and is only TTL-bound; it cannot target another directory. The template's `DISK_CACHE = True` instead writes the result as parquet under the OS temp directory, which survives app restarts and is cleared on reboot. Use it for aggregate, non-sensitive results only.

Clear a stale cache from the app menu, or delete the parquet file when `DISK_CACHE` is on.

## Large datasets

The cache does not make a large frame cheap; it only avoids re-querying. Aggregate in the query so the cached frame stays small. A table of more than a few tens of thousands of rows should be aggregated or paginated before rendering.

## Theming

Apply global CSS once, near the top of the entrypoint:

```python
st.markdown("<style>...</style>", unsafe_allow_html=True)
```

Prefer `.streamlit/config.toml` for colours and fonts; reserve CSS for what the config cannot express.
