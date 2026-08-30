---
name: verify-streamlit-app
description: Verify that a locally running Streamlit app actually renders and works, by driving a headless Chromium browser with Playwright - screenshots, JS console and page-error capture, Streamlit-aware selectors, and a tight manual iterate loop. Pairs with create-streamlit-app.
---

# Verify a Streamlit app with Playwright

Use this skill to confirm a local Streamlit app really works, not merely that the server started. It drives a headless Chromium browser against a running app, screenshots it, captures JavaScript console and page errors, scans the rendered page for error markers, and clicks through key flows with Streamlit-aware selectors. The value is a tight manual loop: launch, look through the browser, fix, repeat.

This is verification, not a CI test suite. Keep it lean. There are three tiers; do not merge them.

## Testing tiers

| Tier | What | When | Files |
|------|------|------|-------|
| 1 - Manual loop (default) | Ad-hoc: screenshot, read page, read console errors, iterate | Active development | none; drive `assets/helpers.py` |
| 2 - Smoke check | One boot and render check: screenshot plus error scan, no behavioural assertions | Quick "does it come up clean?" | `assets/verify.py` |
| 3 - End-to-end (opt-in) | Real assertions on flows: select, click, assert content | The user explicitly wants regression tests | `assets/tests_e2e_example.py` |

Default to tier 1 during development. Add tier 2 as a repeatable smoke gate. Only build tier 3 when the user asks for lasting tests.

## Workflow

Commands below assume macOS or Linux. On Windows, GNU Make is not standard: treat the generated Makefile as a template and run the underlying commands directly.

1. Scaffold the harness next to the app: copy `assets/helpers.py` and `assets/verify.py` into the app directory, and generate `Makefile.verify` from `assets/Makefile.tmpl`. The name avoids clobbering an app `Makefile` produced by `create-streamlit-app`; run its targets with `make -f Makefile.verify <target>`. Copy `assets/tests_e2e_example.py` only for tier 3.
2. Install Playwright: `make -f Makefile.verify setup`, which runs `uv pip install playwright pytest` and `uv run playwright install chromium`. Without uv, use `pip install playwright pytest && playwright install chromium`.
3. Start the app: `make -f Makefile.verify start-app`, which launches `streamlit run app.py --server.headless true` in the background and blocks until the port accepts connections. Never drive the browser before the port answers.
4. Drive the browser through the helpers: `create_browser()`, `goto(page, url)`, `screenshot(page, "name")`, `collect_errors(page)`. The last returns page-text error markers plus captured JavaScript console and page errors.
5. Look at the screenshot and the error output. If the app is broken, fix it and repeat from step 3.
6. Gate repeatably with `make -f Makefile.verify verify`, which exits non-zero when any error is found.
7. Clean up: stop the app process and run `make -f Makefile.verify clean`.

## Streamlit-aware verification

Streamlit renders asynchronously and does not expose stable element ids, so target labels and roles rather than CSS classes.

- Wait for the app shell (`.stApp`) before screenshotting, then for a content selector such as `[data-testid="stDataFrame"]`, `[data-testid="stMetric"]`, or `[data-testid="stArrowVegaLiteChart"]`. A screenshot taken on the shell alone often catches an empty page.
- Address widgets by label or role, which survives reruns: `page.get_by_label("Filter by term").fill("abc")`, `page.get_by_role("button", name=re.compile(r"Run", re.I)).click()`.
- Text inputs need the value committed. `st.text_input` shows "Press Enter to apply" and does not rerun the app until Enter is pressed, so a bare `fill()` leaves the page unchanged and looks like a broken filter. The `fill_input` helper presses Enter and waits for the rerun.
- Multiselect: click the label, `keyboard.type("value")`, then `keyboard.press("Enter")`.
- Dataframe rows are not buttons. Click a pixel offset inside the grid to select a row.
- Capture JavaScript errors through `page.on("console", ...)` and `page.on("pageerror", ...)`. Streamlit surfaces client-side failures there, not always in the body text. `collect_errors` wires both up.
- Use generous timeouts, 30 to 60 seconds, and longer for heavy computation. First paint and reruns are slow.

## Conventions

- Headless Chromium by default. Set `headless=False` locally to watch the run.
- Write screenshots and scratch files under a `tmp/` directory in the project and gitignore it. Do not use the system temp directory.
- Do not commit screenshots or the running app's data.

## Assets

- `assets/helpers.py` - `create_browser`, `goto` (waits for the app shell and for Streamlit to settle), `wait_for_content`, `screenshot`, `collect_errors`, and Streamlit selector helpers.
- `assets/verify.py` - tier 2 smoke check. Boots the app URL, screenshots it, captures console and page errors, and exits non-zero on any error. Pass a content selector as the second argument for data-loading apps so the screenshot captures the loaded state.
- `assets/tests_e2e_example.py` - tier 3 pytest example with real assertions and Streamlit selectors.
- `assets/Makefile.tmpl` - setup, start-app, verify, test, and clean lifecycle.
