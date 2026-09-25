"""Download a checksum-pinned upstream add-on. Does not start MCP or change Blender preferences."""

import argparse
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path

REVISION = "35de9ba202a5dc212b139820eef9f9d999a2edb2"
SHA256 = "daaea155399fab3a7af937834d4e826b3b60038f641566717ab2af1c27775df1"
BASE = f"https://raw.githubusercontent.com/ahujasid/mcp-for-blender/{REVISION}"


def install(destination):
    directory = Path(destination).expanduser().resolve()
    source = urllib.request.urlopen(BASE + "/addon.py", timeout=30).read()
    if hashlib.sha256(source).hexdigest() != SHA256:
        raise RuntimeError("Add-on checksum mismatch; refusing to install")
    license_text = urllib.request.urlopen(BASE + "/LICENSE", timeout=30).read()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "blender_mcp.py"
    if target.exists() and target.read_bytes() != source:
        backup = target.with_suffix(".py.bak")
        if backup.exists():
            raise RuntimeError(f"Existing backup would be overwritten: {backup}")
        shutil.copy2(target, backup)
    target.write_bytes(source)
    (directory / "blender_mcp.LICENSE.txt").write_bytes(license_text)
    return {
        "addon": str(target),
        "revision": REVISION,
        "sha256": SHA256,
        "next": "Enable blender_mcp in Blender Preferences and start its sidebar listener. No MCP server is needed.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--addons-dir",
        required=True,
        help="Blender user scripts/addons directory, or a staging directory for manual install",
    )
    args = parser.parse_args()
    print(json.dumps(install(args.addons_dir), indent=2))
