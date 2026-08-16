#!/usr/bin/env bash
# Shared quick freshness check for marketplace plugins (~1s).
# Usage: check-plugin-freshness.sh <plugin-name> [installed-plugin-dir]
set -euo pipefail
plugin="${1:?usage: check-plugin-freshness.sh <plugin-name> [installed-plugin-dir]}"
installed_dir="${2:-}"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
stale=0
if ! git -C "$repo_root" fetch --quiet origin 2>/dev/null; then
  echo "WARN: could not fetch origin (offline or auth issue); checking local state only"
fi
remote_head="$(git -C "$repo_root" rev-parse origin/HEAD 2>/dev/null || git -C "$repo_root" rev-parse origin/master 2>/dev/null || echo HEAD)"
if ! git -C "$repo_root" merge-base --is-ancestor "$remote_head" HEAD 2>/dev/null; then
  echo "STALE: marketplace clone is behind origin — run: git -C $repo_root pull --ff-only"; stale=1
fi
if [ -n "$installed_dir" ] && ! diff -rq "$repo_root/plugins/$plugin" "$installed_dir" >/dev/null 2>&1; then
  echo "STALE: installed copy differs from the marketplace clone — run the CLI plugin update for $plugin, then re-read its SKILL.md"; stale=1
fi
[ "$stale" -eq 0 ] && echo "UP-TO-DATE: skip refresh and continue"
exit 0
