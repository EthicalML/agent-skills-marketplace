#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
import json
import pathlib
import sys

import yaml

root = pathlib.Path(".")
marketplace_path = root / ".claude-plugin" / "marketplace.json"
failures = []

def fail(path, message):
    failures.append(f"FAIL {path}: {message}")

try:
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    sys.exit(f"FAIL {marketplace_path}: {error}")

for key in ("name", "owner", "plugins"):
    if not marketplace.get(key):
        fail(marketplace_path, f"missing or empty '{key}'")

listed = {}
for entry in marketplace.get("plugins", []):
    name = entry.get("name")
    source = entry.get("source")
    if not name or not isinstance(source, str):
        fail(marketplace_path, "each plugin needs a name and string source")
        continue
    if name in listed:
        fail(marketplace_path, f"duplicate plugin name '{name}'")
    listed[name] = pathlib.Path(source)
    if not listed[name].is_dir():
        fail(marketplace_path, f"plugin source does not exist: {source}")
    elif not (listed[name] / ".claude-plugin" / "plugin.json").is_file():
        fail(marketplace_path, f"plugin manifest missing under {source}")

actual = {path.name: path for path in (root / "plugins").iterdir() if path.is_dir()}
for name in sorted(set(actual) - set(listed)):
    fail(marketplace_path, f"plugins/{name} is not listed")
for name in sorted(set(listed) - set(actual)):
    fail(marketplace_path, f"listed plugin '{name}' has no matching directory")

skill_names = {}
for directory_name, plugin_dir in sorted(actual.items()):
    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(manifest_path, str(error))
        continue
    if not manifest.get("name") or not manifest.get("description"):
        fail(manifest_path, "missing or empty name or description")
    if manifest.get("name") != directory_name:
        fail(manifest_path, f"name '{manifest.get('name')}' does not equal directory '{directory_name}'")
    else:
        print(f"PASS {manifest_path}: plugin manifest valid")
    for skill_file in sorted((plugin_dir / "skills").glob("*/SKILL.md")):
        try:
            data = yaml.safe_load(skill_file.read_text(encoding="utf-8").split("---", 2)[1])
            skill_name = data.get("name")
        except Exception as error:
            fail(skill_file, f"cannot read skill name: {error}")
            continue
        if skill_name in skill_names:
            fail(skill_file, f"duplicate skill name '{skill_name}', also in {skill_names[skill_name]}")
        skill_names[skill_name] = skill_file

if failures:
    print("\n".join(failures))
    sys.exit(1)
print(f"PASS {marketplace_path}: marketplace and plugin coverage valid")
for skill_name, skill_file in sorted(skill_names.items()):
    print(f"PASS {skill_file}: unique skill name '{skill_name}'")
PY
