"""Tier 3 (opt-in) e2e example with real assertions. Run with pytest.

Assumes the app is already running at APP_URL. This is a *starting point* - add
assertions specific to your app's flows using Streamlit-aware selectors. Do not
merge this with verify.py.

    pip install pytest playwright && playwright install chromium
    pytest tests_e2e_example.py
"""
import os
import re

import pytest
from playwright.sync_api import expect, sync_playwright

BASE_URL = os.environ.get("APP_URL", "http://localhost:8501")


@pytest.fixture
def page():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        pg = browser.new_page()
        pg.set_default_timeout(60_000)
        yield pg
        browser.close()


def test_app_loads(page):
    page.goto(BASE_URL, wait_until="domcontentloaded")
    expect(page.locator(".stApp")).to_be_visible()


def test_table_renders(page):
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_selector(".stDataFrame", timeout=30_000)
    expect(page.locator(".stDataFrame")).to_be_visible()


def test_filter_flow(page):
    """Example: type into a text filter and assert the app reruns cleanly."""
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.get_by_label("Filter by term").fill("a")
    # button lookup by role/name regex is robust across reruns
    # page.get_by_role("button", name=re.compile(r"run", re.I)).click()
    expect(page.locator(".stApp")).to_be_visible()
