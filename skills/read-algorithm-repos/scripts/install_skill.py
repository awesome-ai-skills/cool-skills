#!/usr/bin/env python3
"""Install this portable skill into a supported CLI discovery directory."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


USER_BASES = {
    "codex": Path(".codex/skills"),
    "claude-code": Path(".claude/skills"),
    "opencode": Path(".config/opencode/skills"),
    "agents": Path(".agents/skills"),
}

PROJECT_BASES = {
    "codex": Path(".codex/skills"),
    "claude-code": Path(".claude/skills"),
    "opencode": Path(".opencode/skills"),
    "agents": Path(".agents/skills"),
}


def destination(client: str, scope: str, project_root: Path | None) -> Path:
    if scope == "user":
        return Path.home() / USER_BASES[client] / "read-algorithm-repos"
    if project_root is None:
        raise ValueError("--project-root is required for project scope")
    return project_root.resolve() / PROJECT_BASES[client] / "read-algorithm-repos"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=sorted(USER_BASES), required=True)
    parser.add_argument("--scope", choices=["user", "project"], default="user")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    try:
        target = destination(args.client, args.scope, args.project_root)
    except ValueError as exc:
        parser.error(str(exc))
    payload = {
        "client": args.client,
        "scope": args.scope,
        "source": str(source),
        "destination": str(target),
        "dryRun": args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if source == target.resolve():
        payload["status"] = "already-installed"
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if target.exists():
        if not args.force:
            parser.error(f"destination already exists: {target}; use --force to replace it")
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc"),
    )
    payload["status"] = "installed"
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
