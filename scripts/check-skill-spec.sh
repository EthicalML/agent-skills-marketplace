#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
for f in plugins/*/skills/*/SKILL.md; do
  python3 - "$f" <<'PY' || status=1
import pathlib
import re
import sys

import yaml

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
try:
    block = text.split("---", 2)[1]
    data = yaml.safe_load(block)
except (IndexError, yaml.YAMLError) as error:
    sys.exit(f"FAIL {path}: cannot validate frontmatter: {error}")
allowed = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
unexpected = sorted(set(data or {}) - allowed)
if unexpected:
    sys.exit(f"FAIL {path}: unsupported frontmatter keys: {', '.join(unexpected)}")
name = data.get("name") if isinstance(data, dict) else None
description = data.get("description") if isinstance(data, dict) else None
if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
    sys.exit(f"FAIL {path}: name must be kebab-case")
if len(name) > 64:
    sys.exit(f"FAIL {path}: name exceeds 64 characters")
if name != path.parent.name:
    sys.exit(f"FAIL {path}: name '{name}' does not equal directory '{path.parent.name}'")
if not isinstance(description, str) or len(description) > 1024:
    sys.exit(f"FAIL {path}: description must be a string of at most 1024 characters")
if "<" in description or ">" in description:
    sys.exit(f"FAIL {path}: description must not contain angle brackets")
compatibility = data.get("compatibility")
if compatibility is not None and (not isinstance(compatibility, str) or len(compatibility) > 500):
    sys.exit(f"FAIL {path}: compatibility must be a string of at most 500 characters")
print(f"PASS {path}: skill specification valid")
PY
done
exit "$status"
