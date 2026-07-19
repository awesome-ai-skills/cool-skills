#!/usr/bin/env python3
"""Install a skill from this repository into a supported client directory."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


USER_BASES = {
    "agents": Path(".agents/skills"),
    "claude-code": Path(".claude/skills"),
    "codex": Path(".codex/skills"),
    "opencode": Path(".config/opencode/skills"),
}

PROJECT_BASES = {
    "agents": Path(".agents/skills"),
    "claude-code": Path(".claude/skills"),
    "codex": Path(".codex/skills"),
    "opencode": Path(".opencode/skills"),
}


def destination(client: str, scope: str, project_root: Path | None, skill_name: str) -> Path:
    if scope == "user":
        return Path.home() / USER_BASES[client] / skill_name
    if project_root is None:
        raise ValueError("--project-root is required for project scope")
    return project_root.resolve() / PROJECT_BASES[client] / skill_name


def copy_skill(source: Path, target: Path, force: bool) -> str:
    if source == target.resolve():
        return "already-installed"
    if target.exists():
        if not force:
            raise FileExistsError(f"destination already exists: {target}; use --force to replace it")
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc"),
    )
    return "installed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_name")
    parser.add_argument("--client", choices=sorted(USER_BASES), required=True)
    parser.add_argument("--scope", choices=["user", "project"], default="user")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    repo_root = args.repository.resolve()
    source = repo_root / "skills" / args.skill_name
    if not (source / "SKILL.md").is_file():
        parser.error(f"skill not found: {source}")
    try:
        target = destination(args.client, args.scope, args.project_root, args.skill_name)
    except ValueError as exc:
        parser.error(str(exc))

    payload = {
        "client": args.client,
        "destination": str(target),
        "dryRun": args.dry_run,
        "scope": args.scope,
        "skill": args.skill_name,
        "source": str(source),
    }
    if args.dry_run:
        payload["status"] = "would-replace" if target.exists() else "would-install"
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    try:
        payload["status"] = copy_skill(source, target, args.force)
    except FileExistsError as exc:
        parser.error(str(exc))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
