"""Playwright helpers for manual verification of a local Streamlit app.

Headless Chromium by default. Screenshots go under ./tmp (gitignore it).
collect_errors() captures both rendered error markers AND JS console/page errors,
which is where Streamlit surfaces many client-side failures.
"""
from __future__ import annotations

import pathlib

from playwright.sync_api import Page, sync_playwright

TMP = pathlib.Path("./tmp")

# Markers that indicate the page rendered an error rather than content.
ERROR_MARKERS = [
    "Traceback (most recent call last)",
    "ModuleNotFoundError",
    "NameError",
    "KeyError",
    "AttributeError",
    "RecursionError",
    "maximum recursion depth",
    "streamlit.errors",
    "Uncaught",
    "TypeError:",
    "ValueError:",
]

# Populated by create_browser via page listeners.
_DIAGNOSTICS: list[str] = []


def create_browser(headless: bool = True):
    """Return (playwright, browser, page). Caller closes playwright when done.

    Wires console + pageerror listeners so JS-side failures are captured.
    """
    _DIAGNOSTICS.clear()
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.set_default_timeout(60_000)
    page.on("console", lambda m: _DIAGNOSTICS.append(f"console:{m.type}:{m.text}"))
    page.on("pageerror", lambda e: _DIAGNOSTICS.append(f"pageerror:{e}"))
    return pw, browser, page


def goto(page: Page, url: str, wait_selector: str = ".stApp") -> None:
    """Navigate, wait for the Streamlit app shell, then wait for it to settle.

    Streamlit paints .stApp instantly but data-loading apps render their content
    later, so a screenshot taken on .stApp alone can catch an empty page. We also
    wait for the "running" status widget to clear. When you need a specific widget
    (table/chart) present before asserting, call wait_for_content().
    """
    page.goto(url, wait_until="domcontentloaded")
    try:
        page.wait_for_selector(wait_selector, timeout=30_000)
    except Exception:
        pass  # let the caller screenshot / error-scan whatever rendered
    _wait_until_idle(page)


def _wait_until_idle(page: Page, timeout: int = 60_000) -> None:
    """Best-effort wait for Streamlit's running indicator to disappear, then settle."""
    try:
        page.wait_for_selector(
            '[data-testid="stStatusWidget"]', state="detached", timeout=timeout
        )
    except Exception:
        pass
    page.wait_for_timeout(1_000)  # settle


def wait_for_content(page: Page, selector: str, timeout: int = 30_000) -> bool:
    """Wait for a specific content widget; return True if it appeared.

    Common selectors: '[data-testid="stDataFrame"]',
    '[data-testid="stArrowVegaLiteChart"]', '[data-testid="stMetric"]'.
    """
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:
        return False


def screenshot(page: Page, name: str) -> pathlib.Path:
    TMP.mkdir(parents=True, exist_ok=True)
    path = TMP / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    return path


def collect_errors(page: Page) -> list[str]:
    """Return error markers in the page text plus captured console/page errors.

    Empty list means clean. Console diagnostics are filtered to error/warning.
    """
    body = page.inner_text("body")
    found = [m for m in ERROR_MARKERS if m in body]
    js = [d for d in _DIAGNOSTICS if d.startswith("pageerror") or ":error:" in d]
    return found + js


# ── Streamlit selector helpers ──────────────────────────────────────────

def fill_input(page: Page, label: str, value: str) -> None:
    """Fill a text input and commit it.

    st.text_input shows "Press Enter to apply" and does not rerun the app until
    the value is committed, so filling alone leaves the page unchanged.
    """
    page.get_by_label(label).fill(value)
    page.keyboard.press("Enter")
    _wait_until_idle(page)


def pick_multiselect(page: Page, label: str, value: str) -> None:
    page.get_by_label(label).click()
    page.keyboard.type(value, delay=20)
    page.wait_for_timeout(500)
    page.keyboard.press("Enter")


def click_button(page: Page, name_regex: str) -> None:
    import re

    page.get_by_role("button", name=re.compile(name_regex, re.I)).click()
