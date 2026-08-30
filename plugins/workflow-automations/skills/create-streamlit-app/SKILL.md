---
name: create-streamlit-app
description: Scaffold and run a local Streamlit and Polars data app over a file, a SQL database, an HTTP endpoint, or an inline snapshot. Use when the user wants a small interactive front end to filter, table, and chart a dataset rather than a one-off script or notebook.
---

# Create a Streamlit data app

Commands assume macOS or Linux. On Windows, run the Makefile targets' underlying commands directly.

## 1. Check uv

```bash
command -v uv
```

If missing, install it: `brew install uv`, or `curl -LsSf https://astral.sh/uv/install.sh | sh`, or `pixi global install uv` without admin rights.

## 2. Settle the dataset and pick the datasource

Ask only what changes the scaffold: what the data is, and where it is read from. Decide the rest yourself.

Pick one asset. It becomes the app's `datasource` module and must expose `load_frame(query) -> pl.DataFrame`.

| Where the data lives | Asset | Configured through |
|---|---|---|
| CSV, TSV, Parquet or JSON on disk | `assets/datasource_file.py` | `DATA_PATH` |
| A queryable SQL database | `assets/datasource_sql.py` | `DATABASE_URL` |
| An API returning JSON or CSV | `assets/datasource_http.py` | `DATA_URL`, `API_TOKEN` |
| A small aggregate already known | `assets/datasource_snapshot.py` | inline records |

Read credentials from the environment only. Never write a token into a file.

## 3. Scaffold the app directory

Default to `app/`, and generate four files there:

- Generate `app.py` from `assets/app_template.py`.
- Generate `datasource.py` from the asset chosen in step 2.
- Generate `pyproject.toml` from `assets/pyproject.toml.tmpl`.
- Generate `Makefile` from `assets/Makefile.tmpl`.

## 4. Wire the datasource

Set the path, URI or records in the generated datasource module, and set `QUERY` in the app entrypoint for the SQL datasource. The file, HTTP and snapshot datasources ignore `QUERY`.

Uncomment the datasource's optional dependency in `pyproject.toml`: `connectorx` for SQL, `requests` for HTTP.

For SQL, aggregate in the query rather than selecting every row. The whole result is held in memory and cached.

## 5. Edit the app

Set `TITLE`, then shape the filters and charts to the data. Keep it to a filter row, a table, and one or two charts.

Three rules the template already follows and that must survive editing:

- `st.set_page_config(...)` stays the first Streamlit call in the file, before any other `st.*`.
- Filter the Polars frame first, then render. Convert to pandas only at the chart boundary.
- Leave the `@st.cache_data(ttl=CACHE_TTL)` load in place so filter reruns do not re-query the source.

If the app grows past the template, into multiple pages, selection state, theming, or cache tuning, read [`docs/streamlit-notes.md`](docs/streamlit-notes.md) first.

## 6. Install and run

```bash
make setup
make run      # make watch to rerun on every save
```

If `uv pip install -e .` reports multiple top-level modules, the generated `pyproject.toml` lost its `[tool.setuptools] py-modules = []` entry. Restore it rather than renaming the app's modules.

If the app starts but the page reports a missing module, the datasource's optional dependency is still commented out in `pyproject.toml`. Uncomment it and rerun `make setup`.

## 7. Verify it renders

Do not hand off on a running server alone. Confirm the app renders through the `verify-streamlit-app` skill.
