#!/usr/bin/env python3
"""Validate every published skill under the repository skills/ directory."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for raw in match.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#") or raw.startswith((" ", "\t")):
            continue
        item = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", raw)
        if item:
            value = item.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            fields[item.group(1)] = value
    return fields


def fallback_validate(skill_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    skill_file = skill_root / "SKILL.md"
    if not skill_file.is_file():
        return {
            "name": skill_root.name,
            "path": str(skill_root),
            "valid": False,
            "errors": ["SKILL.md not found"],
            "warnings": [],
            "validator": "fallback",
        }
    fields = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name:
        errors.append("frontmatter field name is required")
    if not description:
        errors.append("frontmatter field description is required")
    if name and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("name must be lowercase alphanumeric words separated by single hyphens")
    if name and name != skill_root.name:
        errors.append(f"directory name {skill_root.name!r} does not match skill name {name!r}")
    return {
        "name": name or skill_root.name,
        "path": str(skill_root),
        "valid": not errors,
        "errors": errors,
        "warnings": [],
        "validator": "fallback",
    }


def run_bundled_validator(skill_root: Path) -> dict[str, Any] | None:
    validator = skill_root / "scripts" / "validate_skill.py"
    if not validator.is_file():
        return None
    result = subprocess.run(
        [sys.executable, str(validator), str(skill_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {
            "valid": False,
            "errors": [result.stderr.strip() or "validator did not emit JSON"],
            "warnings": [],
        }
    fields = parse_frontmatter((skill_root / "SKILL.md").read_text(encoding="utf-8"))
    payload.setdefault("errors", [])
    payload.setdefault("warnings", [])
    payload["name"] = fields.get("name", skill_root.name)
    payload["path"] = str(skill_root)
    payload["validator"] = str(validator.relative_to(skill_root))
    if result.returncode != 0 and payload.get("valid"):
        payload["valid"] = False
        payload["errors"].append(result.stderr.strip() or f"validator exited with {result.returncode}")
    return payload


def validate_repository(repo_root: Path) -> dict[str, Any]:
    skills_dir = repo_root / "skills"
    errors: list[str] = []
    if not skills_dir.is_dir():
        return {"root": str(repo_root), "valid": False, "skills": [], "errors": ["skills/ not found"]}
    skills: list[dict[str, Any]] = []
    for skill_root in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        if skill_root.name.startswith("."):
            continue
        result = run_bundled_validator(skill_root) or fallback_validate(skill_root)
        result["path"] = str(skill_root.relative_to(repo_root))
        skills.append(result)
    if not skills:
        errors.append("no skills found under skills/")
    errors.extend(
        f"{item['path']}: {error}"
        for item in skills
        if not item.get("valid")
        for error in item.get("errors", [])
    )
    return {"root": str(repo_root), "valid": not errors, "skills": skills, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = validate_repository(args.root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
