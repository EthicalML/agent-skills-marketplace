#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
for f in plugins/*/skills/*/SKILL.md; do
  python3 - "$f" <<'PY' || status=1
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
spans = re.findall(r"`([^`\n]+)`", text)
spans += re.findall(r"\]\(([^)]+)\)", text)
pattern = re.compile(r"(?<![A-Za-z0-9_])(?:\.\./|\./|assets/|docs/|scripts/|references/)[A-Za-z0-9._/-]+")
references = set()
for span in spans:
    for match in pattern.findall(span):
        candidate = match.rstrip(".,:;)")
        if "*" in candidate or "<" in candidate or candidate.startswith("/"):
            continue
        if candidate in {"./", "../"}:
            continue
        references.add(candidate)

# Bare executable filenames are references unless their line clearly instructs the
# agent to create the file. Documentation examples and generated outputs stay ignored.
for line in text.splitlines():
    for candidate in re.findall(r"`([A-Za-z0-9_.-]+\.(?:mjs|py|sh))`", line):
        if re.search(r"\b(?:create|write|generate|output)\b", line, re.IGNORECASE):
            continue
        references.add(candidate)

missing = []
for reference in sorted(references):
    if not (path.parent / reference).exists():
        missing.append(reference)
if missing:
    sys.exit(f"FAIL {path}: missing relative references: {', '.join(missing)}")
print(f"PASS {path}: {len(references)} relative reference(s) exist")
PY
done
exit "$status"
