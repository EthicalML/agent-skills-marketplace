#!/usr/bin/env bash
# Read-only disk usage scan. Prints plain-text sections for the agent to classify.
# Usage: scan.sh [projects-root]   (default: $HOME)
set -uo pipefail
ROOT="${1:-$HOME}"
MAC=0; [ "$(uname)" = "Darwin" ] && MAC=1
gb() { du -sk "$1" 2>/dev/null | awk '{printf "%.1f", $1/1048576}'; }

echo "## Disk (use this line for used/free)"
if [ $MAC -eq 1 ]; then df -h /System/Volumes/Data 2>/dev/null | tail -1; else df -h / 2>/dev/null | tail -1; fi
[ $MAC -eq 1 ] && { echo "local snapshots: $(tmutil listlocalsnapshots / 2>/dev/null | grep -c com.apple)"; echo "vm swap GB: $(gb /private/var/vm)"; }

echo; echo "## Home top level (GB)"
for p in "$HOME"/* "$HOME"/.[!.]*; do [ -e "$p" ] && echo "$(gb "$p") $p"; done | sort -rn | awk '$1>=0.5'

if [ $MAC -eq 1 ]; then
  echo; echo "## ~/Library subfolders >= 1 GB"
  for p in "$HOME"/Library/{Containers,"Application Support",Caches,"Group Containers",Developer}/*; do
    [ -e "$p" ] && echo "$(gb "$p") $p"
  done | sort -rn | awk '$1>=1'
  echo; echo "## System level (GB)"
  C=$(getconf DARWIN_USER_CACHE_DIR); T=$(getconf DARWIN_USER_TEMP_DIR)
  for p in /Applications /opt/homebrew /usr/local /Library /nix "$C" "$T"; do [ -e "$p" ] && echo "$(gb "$p") $p"; done
  echo "user temp/cache entries >= 1 GB:"
  for p in "$C"* "$T"*; do echo "$(gb "$p") $p"; done | sort -rn | awk '$1>=1'
fi

# Known locations: tier|path|clean command|note. Tiers: quick, easy, choice.
echo; echo "## Known locations (GB | tier | path | command | note)"
known() { [ -e "$2" ] && printf '%s | %s | %s | %s | %s\n' "$(gb "$2")" "$1" "$2" "$3" "$4"; }
UVC=$(uv cache dir 2>/dev/null || echo "$HOME/.cache/uv")
known quick "$UVC" "uv cache clean" "Python package cache"
known quick "$HOME/.npm/_cacache" "npm cache clean --force" ""
known quick "$HOME/.cache/pre-commit" "pre-commit clean" ""
known quick "$HOME/.cache/puppeteer" "rm -rf" "re-downloads on next run"
known easy "$HOME/go/pkg/mod" "go clean -modcache" "Go module cache"
known easy "$HOME/.cargo/registry" "rm -rf" "Cargo download cache"
known easy "$HOME/.gradle/caches" "rm -rf" ""
known easy "$HOME/.m2/repository" "rm -rf" "Maven cache"
known choice "$HOME/.cache/huggingface" "huggingface-cli delete-cache" "downloaded models; list models before deleting"
known choice "$HOME/.ollama/models" "ollama rm <model>" "local LLMs; list with ollama list"
known choice "$HOME/.pyenv/versions" "pyenv uninstall <version>" "keep the pyenv global version"
known choice "$HOME/.colima" "colima delete <profile>" "VM disks; images inside are lost"
known choice "$HOME/.lima" "limactl delete <name>" "VM disks"
known easy "$HOME/.copilot/otel" "find <path> -type f -mtime +30 -delete" "agent telemetry logs; trim by age"
known easy "$HOME/.copilot/pkg" "keep newest version only" "old CLI builds"
if [ $MAC -eq 1 ]; then
  L="$HOME/Library"
  known quick "$(getconf DARWIN_USER_CACHE_DIR)com.apple.dt.Instruments" "rm -rf" "Xcode Instruments traces, often stale"
  known quick "$L/Developer/Xcode/DerivedData" "rm -rf" "Xcode build output"
  known easy "$L/Developer/Xcode/iOS DeviceSupport" "rm -rf" "re-created when a device connects"
  known easy "$L/Developer/CoreSimulator" "xcrun simctl delete unavailable" ""
  known choice "$L/Developer/Xcode/Archives" "rm -rf <archive>" "app store builds; may be needed for crash symbols"
  for c in pip pypoetry go-build node-gyp goimports Homebrew ms-playwright Yarn datalab; do
    known quick "$L/Caches/$c" "rm -rf (Homebrew: brew cleanup --prune=all)" "regenerable cache"
  done
  known quick "$HOME/.Trash" "user empties Trash in Finder" "never empty it for the user"
  known choice "$L/Containers/com.docker.docker/Data/vms/0/data/Docker.raw" "docker system prune -a --volumes; or uninstall Docker Desktop" "Docker Desktop VM disk (sparse; du shows real use)"
  known choice "$L/Application Support/MobileSync/Backup" "Finder > device > Manage Backups" "iPhone/iPad backups"
  known choice "$L/Application Support/Signal" "Signal > Settings > Chats > Manage storage" "message attachments"
  for fs in "$L/Application Support/Google/Chrome"/*/"File System"; do
    known choice "$fs" "chrome://settings/content/all, delete that site's data" "site storage; identify the site with: strings -n 3 \"$fs/Origins/\"* | grep -A1 ORIGIN:"
  done
  SHOTS=$(defaults read com.apple.screencapture location 2>/dev/null || echo "$HOME/Desktop")
  known choice "$SHOTS" "move files older than 6 months to Trash" "screenshots and screen recordings"
else
  known quick "$HOME/.cache/pip" "pip cache purge" ""
  known quick "$HOME/.local/share/Trash" "user empties Trash" "never empty it for the user"
fi

echo; echo "## Dev artifacts >= 0.5 GB under $ROOT (GB | path)"
find "$ROOT" -maxdepth 7 \( -path "$HOME/Library" -o -path "$HOME/.Trash" \) -prune -o -type d \
  \( -name node_modules -o -name .venv -o -name venv -o -name target -o -name build -o -name dist -o -name .next -o -name worktrees -o -name .worktrees -o -name tmp \) \
  -print -prune 2>/dev/null | while read -r d; do echo "$(gb "$d") $d"; done | sort -rn | awk '$1>=0.5'

echo; echo "## Files >= 2 GB under $HOME (outside ~/Library)"
find "$HOME" -xdev \( -path "$HOME/Library" -o -path "$HOME/.Trash" \) -prune -o -type f -size +2G -print 2>/dev/null | while read -r f; do echo "$(gb "$f") $f"; done | sort -rn
