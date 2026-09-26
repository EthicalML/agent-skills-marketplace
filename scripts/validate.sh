#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

checks=(
  sync-skill-baseline-block.sh
  check-skill-frontmatter.sh
  check-skill-spec.sh
  check-manifests.sh
  check-skill-refs.sh
  check-clean-content.sh
)
status=0
for check in "${checks[@]}"; do
  echo "==> scripts/$check"
  args=()
  if [ "$check" = "sync-skill-baseline-block.sh" ]; then
    args=(--check)
  fi
  if bash "scripts/$check" "${args[@]}"; then
    echo "PASS scripts/$check"
  else
    echo "FAIL scripts/$check"
    status=1
  fi
done
echo "==> Blender client and job tests"
if python3 -m unittest discover -s plugins/blender/tests -p 'test_*.py'; then
  echo "PASS Blender client and job tests"
else
  echo "FAIL Blender client and job tests"
  status=1
fi
if [ "$status" -eq 0 ]; then
  echo "Validation passed: all seven checks succeeded."
else
  echo "Validation failed: one or more checks did not succeed."
fi
exit "$status"
