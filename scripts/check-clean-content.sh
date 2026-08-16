#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

denylist=()
while IFS= read -r term; do
  [ -n "$term" ] && denylist+=("$term")
done < scripts/denylist.txt

status=0
while IFS= read -r file; do
  failed=0
  for term in "${denylist[@]}"; do
    if grep -Eiq "$term" "$file"; then
      failed=1
      status=1
    fi
  done
  if [ "$failed" -eq 1 ]; then
    echo "FAIL $file: contains denied public-content text"
  else
    echo "PASS $file: clean public content"
  fi
done < <(git ls-files --cached --others --exclude-standard | grep -Ev '^(scripts/denylist\.txt|tmp/)' | sort)
exit "$status"
