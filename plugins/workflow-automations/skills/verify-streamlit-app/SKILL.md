---
name: verify-streamlit-app
description: Verify that a locally running Streamlit app actually renders and works, by driving a headless Chromium browser with Playwright - screenshots, JS console and page-error capture, Streamlit-aware selectors, and a tight manual iterate loop. Pairs with create-streamlit-app.
---

# Verify a Streamlit app with Playwright

A running server proves nothing. This drives a real browser against the app, screenshots it, and reads the errors Streamlit only surfaces client-side.

Commands assume macOS or Linux. On Windows, run the Makefile targets' underlying commands directly.

## 1. Scaffold the harness

Copy into the app directory: `assets/helpers.py`, `assets/verify.py`, and `assets/Makefile.tmpl` as `Makefile.verify`.

The name matters: `create-streamlit-app` generates its own `Makefile` in that directory. Run every target below as `make -f Makefile.verify <target>`.

## 2. Install Playwright

```bash
make -f Makefile.verify setup
```

Without uv: `pip install playwright pytest && playwright install chromium`.

## 3. Start the app

```bash
make -f Makefile.verify start-app
```

The target blocks until the port answers, then returns. Never drive the browser before it does.

If it prints that the app did not come up, the app crashed on boot. Read the terminal output of the Streamlit process itself; the browser cannot tell you anything about a server that never started.

## 4. Smoke check

```bash
make -f Makefile.verify verify
```

For an app whose content loads after a query, pass the content selector so the screenshot captures the loaded state rather than an empty shell:

```bash
uv run python verify.py http://localhost:8501 '[data-testid="stDataFrame"]'
```

Exit 0 means clean. Non-zero prints the error markers found in the page text and the JavaScript console and page errors captured during the load.

Then open the screenshot at `tmp/verify.png` and look at it. A page can exit 0 and still be an empty shell, a spinner, or a table of zero rows. The screenshot is the verification; the exit code only gates the obvious failures.

## 5. Drive the flows that matter

Skip only if the app has no interaction. Otherwise write a short script against `assets/helpers.py`: `create_browser()`, `goto(page, url)`, then exercise each filter, selector and button, calling `screenshot(page, "<name>")` and `collect_errors(page)` after each.

Streamlit renders asynchronously and exposes no stable element ids, so target labels and roles, never CSS classes:

- `fill_input(page, "Filter by term", "abc")` fills and presses Enter. A bare `.fill()` does not commit the value: `st.text_input` shows "Press Enter to apply" and does not rerun, so the page stays unchanged and the filter looks broken when it is not.
- `page.get_by_role("button", name=re.compile(r"Run", re.I))` for buttons.
- `pick_multiselect(page, label, value)` for multiselects, which need type-then-Enter rather than a click.
- `wait_for_content(page, '[data-testid="stDataFrame"]')` before asserting on content. Common testids are `stDataFrame`, `stMetric` and `stVegaLiteChart`, but they drift between Streamlit versions and `wait_for_content` returns False rather than raising, so a stale name reads as a missing widget. Print the real ones from the loaded page instead of guessing:

```python
print(sorted(set(page.eval_on_selector_all("[data-testid]", "els => els.map(e => e.dataset.testid)"))))
```

Assert the effect, not just the absence of errors: after filtering, the row-count caption must change. If a selector times out, screenshot first and look at the page before adjusting the selector; the widget is often absent rather than misnamed.

Timeouts are 30 to 60 seconds by default. Raise them for heavy computation rather than lowering them to fail faster.

## 6. Fix and repeat

Every failure found here is a bug in the app, not in the harness. Fix the app, then rerun from step 4. `make watch` in `create-streamlit-app` reruns the app on save, so the loop needs no restart.

## 7. Clean up

Stop the Streamlit process and run `make -f Makefile.verify clean`. Write screenshots and scratch files under `tmp/` in the project and gitignore it; do not commit them.

## 8. Lasting tests, only if asked

Skip unless the user wants regression tests that outlive this session. Steps 4 and 5 are verification, not a test suite; do not merge them into one.

Copy `assets/tests_e2e_example.py` and replace its examples with assertions on the app's real flows, using the same label and role selectors from step 5. Run with `make -f Makefile.verify test`.
