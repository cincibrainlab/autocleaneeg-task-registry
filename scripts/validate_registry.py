#!/usr/bin/env python3
"""Validate registry.json against tasks directory contents."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
registry_path = ROOT / "registry.json"

errors: list[str] = []

try:
    data = json.loads(registry_path.read_text(encoding="utf-8"))
except FileNotFoundError:
    sys.stderr.write("registry.json is missing\n")
    sys.exit(1)
except json.JSONDecodeError as exc:
    sys.stderr.write(f"registry.json is not valid JSON: {exc}\n")
    sys.exit(1)

if data.get("version") != 1:
    errors.append("registry version must be set to 1")

tasks = data.get("tasks")
if not isinstance(tasks, list):
    errors.append("registry 'tasks' field must be a list")
    tasks = []

names_seen: set[str] = set()
paths_seen: set[str] = set()
for entry in tasks:
    if not isinstance(entry, dict):
        errors.append(f"registry entry is not an object: {entry!r}")
        continue

    name = entry.get("name")
    path = entry.get("path")

    if not isinstance(name, str) or not name:
        errors.append(f"registry entry missing valid name: {entry!r}")
        continue
    if name in names_seen:
        errors.append(f"duplicate task name in registry: {name}")
    names_seen.add(name)

    if not isinstance(path, str) or not path:
        errors.append(f"registry entry missing valid path: {entry!r}")
        continue
    if path in paths_seen:
        errors.append(f"duplicate task path in registry: {path}")
    paths_seen.add(path)

    candidate = ROOT / path
    if candidate.is_file():
        continue
    errors.append(f"registry path does not exist: {path}")

actual_files = {
    str(p.relative_to(ROOT)).replace("\\", "/")
    for p in (ROOT / "tasks").rglob("*.py")
    if p.name != "__init__.py"
}

missing_entries = actual_files - paths_seen
if missing_entries:
    errors.append(
        "task files missing from registry: " + ", ".join(sorted(missing_entries))
    )

unknown_entries = paths_seen - actual_files
if unknown_entries:
    errors.append(
        "registry entries pointing to missing files: "
        + ", ".join(sorted(unknown_entries))
    )

if errors:
    sys.stderr.write("\n".join(errors) + "\n")
    sys.exit(1)

print("registry.json matches tasks directory")
