#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

checks=(
  check-skill-frontmatter.sh
  check-skill-spec.sh
  check-manifests.sh
  check-skill-refs.sh
  check-clean-content.sh
)
status=0
for check in "${checks[@]}"; do
  echo "==> scripts/$check"
  if bash "scripts/$check"; then
    echo "PASS scripts/$check"
  else
    echo "FAIL scripts/$check"
    status=1
  fi
done
if [ "$status" -eq 0 ]; then
  echo "Validation passed: all five checks succeeded."
else
  echo "Validation failed: one or more checks did not succeed."
fi
exit "$status"
