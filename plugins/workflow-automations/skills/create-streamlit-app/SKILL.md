---
name: create-streamlit-app
description: Scaffold and run a local Streamlit and Polars data app over a file, a SQL database, an HTTP endpoint, or an inline snapshot. Use when the user wants a small interactive front end to filter, table, and chart a dataset rather than a one-off script or notebook.
---

# Create a Streamlit data app

Use this skill when the user wants a local data application: a quick, interactive front end over a dataset, rather than a one-off script or a notebook. Data is read on demand into a Polars DataFrame and rendered. Nothing is persisted to disk by default, which keeps the data-handling posture clean.

Prefer Polars over pandas for the data path; convert to pandas only at the chart boundary. Do not pull in extra engines unless the user explicitly needs local SQL over local files.

## When to use

- "Build me a small app to explore, filter, or chart this data."
- "Wrap this query in a UI I can click through."
- "I want a dashboard-like local tool for this table."

To confirm the app actually renders, use the `verify-streamlit-app` skill.

## Datasources

The app reads through one pluggable function, `load_frame(query) -> pl.DataFrame`. Pick the implementation that matches where the data lives.

| Datasource | Asset | Use when | Notes |
|------------|-------|----------|-------|
| File | `assets/datasource_file.py` | CSV, TSV, Parquet, or JSON on disk | Strong default for local data. Path from `DATA_PATH`. |
| SQL database | `assets/datasource_sql.py` | The data is in a queryable database | `pl.read_database_uri` with `DATABASE_URL`; needs connectorx or SQLAlchemy plus a driver. |
| HTTP endpoint | `assets/datasource_http.py` | The data comes from an API returning JSON or CSV | Token through `API_TOKEN`, never in the file. |
| Snapshot | `assets/datasource_snapshot.py` | A small aggregate is already known | Inline records, no live connection. |

## Workflow

Commands below assume macOS or Linux. On Windows, GNU Make is not standard: treat the generated Makefile as a template and run the underlying commands directly.

1. Check prerequisites. The scaffold runs on uv. Confirm it is present with `command -v uv`. If missing, install it with `brew install uv`, `curl -LsSf https://astral.sh/uv/install.sh | sh`, or `pixi global install uv` without admin rights. The generated Makefile guards this in its `check` target.
2. Clarify the dataset and how it is reached: a file path, a database connection, an HTTP endpoint, or an aggregate already available. Ask only where the answer changes the scaffold.
3. Scaffold a new app directory, `app/` by default, and generate these files from `assets/`: `app.py` from `assets/app_template.py`, `datasource.py` from the chosen datasource module, `pyproject.toml` from `assets/pyproject.toml.tmpl`, and `Makefile` from `assets/Makefile.tmpl`.
4. Wire the query or path into the datasource module and edit the app entrypoint: title, filters, charts. Keep it simple: a filter row, a table, one or two charts.
5. Read credentials from the environment, never from files. Uncomment the datasource's optional dependency in `pyproject.toml`.
6. Install and run: `make setup`, then `make run`. Use `make watch` while iterating; it adds `--server.runOnSave true` so the app reruns on every save.
7. Verify it renders with the `verify-streamlit-app` skill before handing off.

## Streamlit practices

- `st.set_page_config(...)` must be the first Streamlit call in the entrypoint, before any other `st.*`. Use `layout="wide"` for data apps.
- Multi-page apps: use the `st.Page` and `st.navigation` API to control sidebar labels and icons.
- Cache loads with `@st.cache_data(ttl=...)` so filter reruns do not re-query the source. The template exposes `CACHE_TTL`, default one hour. Raise it for slow-changing data, or set `None` to cache until the process restarts.
- For large datasets, the real lever is aggregating in the query so the cached frame stays small. Avoid selecting every column and row.
- `@st.cache_data(persist="disk")` survives restarts but always writes to `~/.streamlit/cache` and is only TTL-bound. The template's opt-in `DISK_CACHE = True` instead caches results as parquet under the OS temp directory, which survives app restarts and is cleared on reboot. Use it for aggregate, non-sensitive results only.
- Keep the selected row or id in `st.session_state`, not in local variables, which reset on every rerun.
- Filter the Polars frame first, then render with `st.dataframe(view, use_container_width=True)`. Convert to pandas only at the chart boundary.
- Apply global CSS once through `st.markdown(CSS, unsafe_allow_html=True)` for light theming.

## Assets

- `assets/app_template.py` - minimal Streamlit skeleton with filters, table, chart, and a cached load with tunable `CACHE_TTL` and opt-in `DISK_CACHE`.
- `assets/datasource_file.py` - local CSV, TSV, Parquet, or JSON file.
- `assets/datasource_sql.py` - SQL database through a connection URI.
- `assets/datasource_http.py` - HTTP endpoint returning JSON or CSV.
- `assets/datasource_snapshot.py` - inline snapshot with no live connection.
- `assets/pyproject.toml.tmpl` - dependencies for the scaffold.
- `assets/Makefile.tmpl` - check, setup, run, watch, and clean lifecycle.
