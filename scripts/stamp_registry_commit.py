#!/usr/bin/env python3
"""Update registry.json commit field to match the current revision."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sha = os.environ.get("GITHUB_SHA")
if not sha:
    sys.stderr.write("GITHUB_SHA is not set; nothing to do\n")
    sys.exit(0)

root = Path(__file__).resolve().parents[1]
registry_path = root / "registry.json"

data = json.loads(registry_path.read_text(encoding="utf-8"))
if data.get("commit") == sha:
    print("registry commit already up to date")
    sys.exit(0)

data["commit"] = sha
registry_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(f"registry commit updated to {sha}")
