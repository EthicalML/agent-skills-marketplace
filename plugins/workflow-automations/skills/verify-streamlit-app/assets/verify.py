"""Tier 2 smoke check: boot the app URL, screenshot, capture errors.

No behavioral assertions - just "does it come up clean?". Captures rendered error
markers AND JS console/page errors. Exits non-zero if anything is found so it can
gate `make verify`.

`goto` already waits for Streamlit to settle. For a data-loading app whose content
appears after a query, pass a content selector as the 2nd arg (e.g.
'[data-testid=\"stDataFrame\"]') so the screenshot captures the loaded state.

Usage: python verify.py [url] [content_selector]   (default http://localhost:8501)
"""
import sys

from helpers import collect_errors, create_browser, goto, screenshot, wait_for_content


def main(url: str, content_selector: str | None = None) -> int:
    pw, browser, page = create_browser(headless=True)
    try:
        goto(page, url)
        if content_selector and not wait_for_content(page, content_selector):
            print(f"WARNING: content selector never appeared: {content_selector}")
        shot = screenshot(page, "verify")
        errors = collect_errors(page)
        print(f"screenshot: {shot}")
        if errors:
            print("ERRORS FOUND:")
            for e in errors:
                print("  -", e)
            return 1
        print("OK: page rendered with no error markers")
        return 0
    finally:
        browser.close()
        pw.stop()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
    selector = sys.argv[2] if len(sys.argv) > 2 else None
    raise SystemExit(main(url, selector))
