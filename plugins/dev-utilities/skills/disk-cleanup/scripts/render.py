"""Render a cleanup plan JSON into the interactive review page.

Usage: python3 render.py plan.json out.html
"""

import json
import pathlib
import sys

plan_path, out_path = sys.argv[1], sys.argv[2]
plan = json.loads(pathlib.Path(plan_path).read_text(encoding="utf-8"))
for key in ("title", "breakdown", "tiers"):
    if key not in plan:
        sys.exit(f"plan is missing '{key}'")
ids = [item["id"] for tier in plan["tiers"] for item in tier["items"]]
if len(ids) != len(set(ids)):
    sys.exit("item ids must be unique across tiers")

template = pathlib.Path(__file__).parent.parent / "assets" / "review.html"
page = template.read_text(encoding="utf-8").replace("__PLAN_JSON__", json.dumps(plan).replace("</", "<\\/"))
pathlib.Path(out_path).write_text(page, encoding="utf-8")
print(f"wrote {out_path} ({len(ids)} items)")
