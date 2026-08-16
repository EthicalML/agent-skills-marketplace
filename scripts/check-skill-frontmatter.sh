#!/usr/bin/env bash
# Copilot drops a skill whose frontmatter fails to parse, silently. A common
# cause is an unquoted description containing a colon followed by a space.
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
for f in plugins/*/skills/*/SKILL.md; do
  python3 - "$f" <<'PY' || status=1
import re
import sys

import yaml

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
if not text.startswith("---\n"):
    sys.exit(f"FAIL {path}: no frontmatter block")
parts = text.split("---", 2)
if len(parts) < 3:
    sys.exit(f"FAIL {path}: unterminated frontmatter block")
block = parts[1]
try:
    data = yaml.safe_load(block)
except yaml.YAMLError as error:
    sys.exit(f"FAIL {path}: frontmatter does not parse\n  {error}")
if not isinstance(data, dict):
    sys.exit(f"FAIL {path}: frontmatter is not a mapping")
for key in ("name", "description"):
    if not data.get(key):
        sys.exit(f"FAIL {path}: missing or empty '{key}'")
description = data["description"]
if not isinstance(description, str):
    sys.exit(f"FAIL {path}: description must parse as a string (quote values containing ': ')")
raw_match = re.search(r"(?m)^description:\s*(.*)$", block)
if not raw_match:
    sys.exit(f"FAIL {path}: description source line is missing")
raw_value = raw_match.group(1)
if raw_value[:1] in {'"', "'"} and raw_value[-1:] != raw_value[:1]:
    sys.exit(f"FAIL {path}: description starts with an unmatched quote")
if description not in block:
    sys.exit(f"FAIL {path}: parsed description does not appear verbatim in raw frontmatter")
print(f"PASS {path}: valid frontmatter")
PY
done
exit "$status"
