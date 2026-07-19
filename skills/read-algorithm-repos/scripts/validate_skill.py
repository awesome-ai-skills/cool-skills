#!/usr/bin/env python3
"""Dependency-free validation for the portable Agent Skill package."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

from repo_utils import write_json


ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[Dict[str, str], Dict[str, str], List[str]]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        return {}, {}, ["SKILL.md must start with YAML frontmatter"]
    fields: Dict[str, str] = {}
    metadata: Dict[str, str] = {}
    current = ""
    errors: List[str] = []
    for number, raw in enumerate(match.group(1).splitlines(), start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")):
            nested = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*?)\s*$", raw)
            if current == "metadata" and nested:
                metadata[nested.group(1)] = unquote(nested.group(2))
            elif current not in {"metadata", "allowed-tools"}:
                errors.append(f"unsupported nested frontmatter at line {number}")
            continue
        item = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", raw)
        if not item:
            errors.append(f"cannot parse frontmatter line {number}")
            continue
        current = item.group(1)
        fields[current] = unquote(item.group(2))
    return fields, metadata, errors


def validate(skill_root: Path) -> Dict[str, object]:
    errors: List[str] = []
    warnings: List[str] = []
    skill_file = skill_root / "SKILL.md"
    if not skill_file.is_file():
        return {"valid": False, "errors": ["SKILL.md not found"], "warnings": []}
    text = skill_file.read_text(encoding="utf-8")
    fields, metadata, parse_errors = parse_frontmatter(text)
    errors.extend(parse_errors)
    unknown = sorted(set(fields) - ALLOWED_FIELDS)
    if unknown:
        errors.append("unknown frontmatter fields: " + ", ".join(unknown))
    for required in ("name", "description"):
        if not fields.get(required):
            errors.append(f"frontmatter field {required} is required")
    name = fields.get("name", "")
    if name and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("name must be lowercase alphanumeric words separated by single hyphens")
    if len(name) > 64:
        errors.append("name exceeds 64 characters")
    if name and skill_root.name != name:
        errors.append(f"directory name {skill_root.name!r} does not match skill name {name!r}")
    description = fields.get("description", "")
    if len(description) > 1024:
        errors.append("description exceeds 1024 characters")
    compatibility = fields.get("compatibility", "")
    if len(compatibility) > 500:
        errors.append("compatibility exceeds 500 characters")
    if "metadata" in fields and not metadata:
        errors.append("metadata must contain at least one string-to-string entry")
    if any(not value for value in metadata.values()):
        errors.append("metadata values must be non-empty strings")

    resources = sorted(
        set(
            re.findall(
                r"(?:references|scripts|assets|agents)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*",
                text,
            )
        )
    )
    for relative in resources:
        if not (skill_root / relative).exists():
            errors.append(f"referenced bundled resource does not exist: {relative}")
    for path in sorted(skill_root.rglob("*")):
        rel = path.relative_to(skill_root)
        parts = rel.parts
        if "__pycache__" in parts or ".DS_Store" in parts or path.suffix == ".pyc":
            continue
        if not path.is_file():
            continue
    for path in (skill_root / "assets").glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON asset {path.name}: {exc}")
    if "allowed-tools" in fields:
        warnings.append("allowed-tools is experimental and may be ignored by some clients")
    return {"valid": not errors, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", type=Path)
    args = parser.parse_args()
    result = validate(args.skill_root.resolve())
    write_json(result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
