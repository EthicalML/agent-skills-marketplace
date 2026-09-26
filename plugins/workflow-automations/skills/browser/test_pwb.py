"""Tests for the browser skill playwright-cli wrapper."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PWB_PATH = Path(__file__).resolve().parent / "pwb.py"
SPEC = importlib.util.spec_from_file_location("browser_pwb", PWB_PATH)
assert SPEC and SPEC.loader
pwb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pwb)


class BrowserPwbTests(unittest.TestCase):
    def test_redacts_tokens(self):
        text = "open chrome-extension://abcdefghijkl/connect.html?token=top-secret&foo=bar) token=second value"
        self.assertEqual(
            pwb.redact_tokens(text),
            "open chrome-extension://abcdefghijkl/connect.html?token=REDACTED&foo=bar) token=REDACTED value",
        )

    def test_rewrites_relative_artifact_paths(self):
        output = "[Snapshot](.playwright-cli/page-123.yml)\n.playwright-cli/screenshot.png\n"
        self.assertEqual(
            pwb.rewrite_artifact_paths(output, Path("/config/browser")),
            "[Snapshot](/config/browser/.playwright-cli/page-123.yml)\n/config/browser/.playwright-cli/screenshot.png\n",
        )

    def test_site_note_lookup_strips_www_and_falls_back_through_subdomains(self):
        with tempfile.TemporaryDirectory() as temporary:
            notes = Path(temporary)
            github = notes / "github.com.md"
            github.write_text("notes", encoding="utf-8")
            self.assertEqual(pwb.find_site_note("https://www.github.com/inbox", notes), github.resolve())
            self.assertEqual(pwb.find_site_note("https://a.b.github.com/path", notes), github.resolve())
            self.assertIsNone(pwb.find_site_note("https://example.org", notes))

    def test_parses_tab_list(self):
        output = "- 0: [Connect](chrome-extension://abc/connect.html?token=secret)\n- 1: (current) [Example](https://example.com/a_(b))\n"
        self.assertEqual(
            pwb.parse_tab_list(output),
            [
                {
                    "index": 0,
                    "current": False,
                    "title": "Connect",
                    "url": "chrome-extension://abc/connect.html?token=secret",
                },
                {"index": 1, "current": True, "title": "Example", "url": "https://example.com/a_(b)"},
            ],
        )

    def test_done_selection_closes_connect_and_created_tabs_but_keeps_shared_initial_tab(self):
        connect = "chrome-extension://abc/connect.html?token=secret"
        shared = "https://mail.example.com/inbox"
        tabs = [
            {"index": 0, "url": connect},
            {"index": 1, "url": shared},
            {"index": 2, "url": "https://news.ycombinator.com/"},
            {"index": 3, "url": "https://linear.app/workspace/inbox"},
        ]
        self.assertEqual(pwb.tabs_to_close(tabs, [connect, shared]), [3, 2, 0])

    def test_missing_playwright_cli_exits_two_with_exact_hint(self):
        env = os.environ.copy()
        env["PATH"] = str(Path(sys.executable).parent)
        with tempfile.TemporaryDirectory() as home:
            env["HOME"] = home
            result = subprocess.run(
                [sys.executable, str(PWB_PATH), "attach"],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, pwb.INSTALL_HINT + "\n")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
