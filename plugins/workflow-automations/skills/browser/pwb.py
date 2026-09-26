#!/usr/bin/env python3
"""Small, safe wrapper around playwright-cli for the browser skill."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


SESSION = "pwb"
CONFIG_DIR = Path.home() / ".cache/agent-skills-marketplace/browser"
STATE_FILE = CONFIG_DIR / "state.json"
NOTES_DIR = Path(__file__).resolve().parent / "docs/sites"
INSTALL_HINT = "playwright-cli not found; run npm install -g @playwright/cli@latest"


def redact_tokens(text: str) -> str:
    return re.sub(r"token=[^)&\s]*", "token=REDACTED", text)


def rewrite_artifact_paths(text: str, config_dir: Path = CONFIG_DIR) -> str:
    absolute = str(config_dir / ".playwright-cli") + "/"
    return re.sub(r"(?<![\w./-])\.playwright-cli/", lambda _match: absolute, text)


def clean_output(text: str, config_dir: Path = CONFIG_DIR) -> str:
    return rewrite_artifact_paths(redact_tokens(text), config_dir)


def find_site_note(url: str, notes_dir: Path = NOTES_DIR) -> Path | None:
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    labels = host.split(".")
    while len(labels) >= 2:
        candidate = notes_dir / f"{'.'.join(labels)}.md"
        if candidate.is_file():
            return candidate.resolve()
        labels = labels[1:]
    return None


def parse_tab_list(output: str) -> list[dict[str, object]]:
    tabs = []
    pattern = re.compile(r"^- (\d+):( \(current\))? \[(.*)\]\((.*)\)(?: \[crashed\])?$")
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            tabs.append(
                {
                    "index": int(match.group(1)),
                    "current": bool(match.group(2)),
                    "title": match.group(3),
                    "url": match.group(4),
                }
            )
    return tabs


def is_connect_page(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "chrome-extension" and "token=" in parsed.query


def tabs_to_close(tabs: list[dict[str, object]], initial_urls: list[str]) -> list[int]:
    keep = Counter(url for url in initial_urls if not is_connect_page(url))
    close = []
    for tab in tabs:
        url = str(tab["url"])
        if not is_connect_page(url) and keep[url]:
            keep[url] -= 1
        else:
            close.append(int(tab["index"]))
    return sorted(close, reverse=True)


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    CONFIG_DIR.chmod(0o700)


def run_cli(args: list[str], timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["playwright-cli", *args],
        cwd=CONFIG_DIR,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def emit(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(clean_output(result.stdout), end="")
    if result.stderr:
        print(clean_output(result.stderr), end="", file=sys.stderr)


def session_exists(output: str) -> bool:
    return bool(re.search(rf"^- {re.escape(SESSION)}:$", output, re.MULTILINE))


def session_cli(args: list[str], raw: bool = False, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    prefix = ["--raw"] if raw else []
    return run_cli([*prefix, f"-s={SESSION}", *args], timeout=timeout)


def json_value(result: subprocess.CompletedProcess[str]):
    if result.returncode:
        emit(result)
        raise SystemExit(result.returncode)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        emit(result)
        raise SystemExit(result.returncode or 1)


def list_tabs() -> list[dict[str, object]]:
    result = session_cli(["tab-list"])
    if result.returncode:
        emit(result)
        raise SystemExit(result.returncode)
    return parse_tab_list(result.stdout)


def save_initial_tabs(tabs: list[dict[str, object]]) -> None:
    STATE_FILE.write_text(json.dumps({"initial_urls": [tab["url"] for tab in tabs]}) + "\n", encoding="utf-8")
    STATE_FILE.chmod(0o600)


def command_attach() -> int:
    listed = run_cli(["list"])
    if listed.returncode:
        emit(listed)
        return listed.returncode
    if session_exists(listed.stdout):
        print("reusing playwright-cli session pwb")
        if not STATE_FILE.exists():
            save_initial_tabs(list_tabs())
        return 0
    if not os.environ.get("PLAYWRIGHT_MCP_EXTENSION_TOKEN"):
        print("warning: PLAYWRIGHT_MCP_EXTENSION_TOKEN is unset; Chrome will show a tab picker")
    try:
        attached = run_cli(["attach", "--extension=chrome", f"--session={SESSION}"], timeout=60)
    except subprocess.TimeoutExpired:
        print("the Playwright extension did not answer within 60 seconds")
        return 1
    emit(attached)
    if attached.returncode:
        return attached.returncode
    save_initial_tabs(list_tabs())
    return 0


def poll_page():
    expression = "(() => { const text = document.body?.innerText || ''; const lines = text.split(/\\n/).map(s => s.trim()).filter(Boolean); return {readyState: document.readyState, textLength: text.length, lastLine: lines.at(-1) || ''}; })()"
    try:
        result = session_cli(["eval", expression], raw=True, timeout=5)
    except subprocess.TimeoutExpired:
        return None
    if result.returncode:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def settle() -> None:
    deadline = time.monotonic() + 15
    previous_length = None
    # Settled means complete, unchanged text length across two polls, and no trailing Loading placeholder.
    while time.monotonic() < deadline:
        state = poll_page()
        if state:
            loading = state["lastLine"] in {"Loading…", "Loading..."}
            if state["readyState"] == "complete" and state["textLength"] == previous_length and not loading:
                return
            previous_length = state["textLength"]
        time.sleep(0.5)
    print("page did not settle within 15 seconds; continuing")


def command_open(url: str) -> int:
    opened = session_cli(["tab-new", url])
    if opened.returncode:
        emit(opened)
        return opened.returncode
    settle()
    expression = "({url: location.href, title: document.title})"
    page = json_value(session_cli(["eval", expression], raw=True))
    print(f"final URL: {page['url']}")
    print(f"title: {page['title']}")
    note = find_site_note(page["url"])
    if note:
        print(f"site notes: {note}")
    return 0


def page_text(selector: str | None) -> str:
    selector_json = json.dumps(selector)
    expression = f"(() => {{ const selector = {selector_json}; const el = selector ? document.querySelector(selector) : document.querySelector('main') || document.body; return el?.innerText || ''; }})()"
    return str(json_value(session_cli(["eval", expression], raw=True)))


def collapse_blank_lines(text: str) -> str:
    return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", text)


def command_text(args: list[str]) -> int:
    maximum = 8000
    selector = None
    index = 0
    while index < len(args):
        if args[index] == "--max" and index + 1 >= len(args):
            print("usage: pwb text [css] [--max N]", file=sys.stderr)
            return 2
        if args[index] == "--max":
            try:
                maximum = max(0, int(args[index + 1]))
            except ValueError:
                print("pwb text: --max must be an integer", file=sys.stderr)
                return 2
            index += 2
        elif selector is None:
            selector = args[index]
            index += 1
        else:
            print("usage: pwb text [css] [--max N]", file=sys.stderr)
            return 2
    text = page_text(selector)
    if not text:
        settle()
        text = page_text(selector)
    text = collapse_blank_lines(text)
    total = len(text)
    if total > maximum:
        print(text[:maximum])
        print(f"[truncated: showing {maximum} of {total} characters]")
    else:
        print(text)
    return 0


def command_labels(pattern: str) -> int:
    pattern_json = json.dumps(pattern)
    expression = f"(() => {{ const re = new RegExp({pattern_json}, 'i'); const seen = new Set(); const out = []; for (const el of document.querySelectorAll('button, a, [role=button], [role=link], [role=option]')) {{ const raw = el.hasAttribute('aria-label') ? el.getAttribute('aria-label') : el.innerText; const name = (raw || '').replace(/\\s+/g, ' ').trim(); if (name && re.test(name) && !seen.has(name)) {{ seen.add(name); out.push(name); if (out.length === 200) break; }} re.lastIndex = 0; }} return out; }})()"
    labels = json_value(session_cli(["eval", expression], raw=True))
    for label in labels:
        print(label)
    return 0


def load_initial_urls() -> list[str]:
    if not STATE_FILE.exists():
        return []
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))["initial_urls"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def command_done() -> int:
    listed = run_cli(["list"])
    if listed.returncode:
        emit(listed)
        return listed.returncode
    if not session_exists(listed.stdout):
        STATE_FILE.unlink(missing_ok=True)
        return 0
    initial_urls = load_initial_urls()
    if not STATE_FILE.exists():
        initial_urls = [str(tab["url"]) for tab in list_tabs()]
    while True:
        tabs = list_tabs()
        close = tabs_to_close(tabs, initial_urls)
        if not close:
            break
        result = session_cli(["tab-close", str(close[0])])
        if result.returncode:
            emit(result)
            return result.returncode
        # Closing the session's last tab ends the session itself, so there is nothing left to detach.
        if len(tabs) == 1:
            STATE_FILE.unlink(missing_ok=True)
            return 0
    detached = session_cli(["detach"])
    if detached.returncode:
        emit(detached)
        return detached.returncode
    STATE_FILE.unlink(missing_ok=True)
    return 0


def passthrough(args: list[str]) -> int:
    result = session_cli(args)
    emit(result)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    ensure_config_dir()
    if shutil.which("playwright-cli") is None:
        print(INSTALL_HINT)
        return 2
    if not args:
        print("usage: pwb <command> [args...]", file=sys.stderr)
        return 2
    command, rest = args[0], args[1:]
    if command == "attach" and not rest:
        return command_attach()
    if command == "open" and len(rest) == 1:
        return command_open(rest[0])
    if command == "wait" and not rest:
        settle()
        return 0
    if command == "text":
        return command_text(rest)
    if command == "labels" and len(rest) == 1:
        return command_labels(rest[0])
    if command == "done" and not rest:
        return command_done()
    return passthrough(args)


if __name__ == "__main__":
    raise SystemExit(main())
