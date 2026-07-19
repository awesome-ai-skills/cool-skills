#!/usr/bin/env python3
"""Inspect Repomix freshness and regenerate with local tooling or npx."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

from repo_utils import discover_files, git_revision, load_custom_patterns, write_json


RELEVANT_EXTENSIONS = {
    ".py", ".pyx", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".scala",
    ".go", ".rs", ".c", ".h", ".cc", ".cpp", ".hpp", ".cu", ".cuh",
    ".r", ".R", ".jl", ".lua", ".sh", ".ps1", ".sql", ".md", ".rst",
    ".toml", ".yaml", ".yml", ".json", ".json5", ".ini", ".cfg", ".xml",
}


def find_repomix(repo: Path) -> Optional[Path]:
    names = ["repomix.cmd", "repomix"] if os.name == "nt" else ["repomix"]
    for name in names:
        local = repo / "node_modules" / ".bin" / name
        if local.is_file():
            return local
    found = shutil.which("repomix")
    return Path(found) if found else None


def find_npx() -> Optional[Path]:
    names = ["npx.cmd", "npx"] if os.name == "nt" else ["npx"]
    for name in names:
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def resolve_invocation(
    repo: Path,
    config: Path,
    artifact: Path,
    *,
    allow_download: bool = True,
    package: str = "repomix@latest",
) -> Dict[str, object]:
    executable = find_repomix(repo)
    if executable:
        local_bin = repo / "node_modules" / ".bin"
        source = "project-local" if executable.parent == local_bin else "global"
        return {
            "source": source,
            "command": [
                str(executable),
                "--config",
                str(config.resolve()),
                "--output",
                str(artifact.resolve()),
            ],
        }
    if not allow_download:
        return {
            "source": "unavailable",
            "command": None,
            "reason": "Automatic npx download is disabled by --no-download.",
        }
    npx = find_npx()
    if not npx:
        return {
            "source": "unavailable",
            "command": None,
            "reason": "Neither Repomix nor npx is available.",
        }
    return {
        "source": "npx-download",
        "package": package,
        "command": [
            str(npx),
            "--yes",
            package,
            "--config",
            str(config.resolve()),
            "--output",
            str(artifact.resolve()),
        ],
    }


def inspect(
    repo: Path,
    artifact: Path,
    config: Path,
    *,
    allow_download: bool = True,
) -> Dict[str, object]:
    repo = repo.resolve()
    artifact = artifact.resolve()
    patterns = load_custom_patterns(config)
    relevant = discover_files(repo, extensions=RELEVANT_EXTENSIONS, patterns=patterns)
    latest = max((path.stat().st_mtime for path in relevant), default=0.0)
    if not artifact.is_file():
        status = "missing"
        basis = "artifact does not exist"
    elif artifact.stat().st_mtime >= latest:
        status = "fresh"
        basis = "artifact mtime is not older than architecture-relevant files"
    else:
        status = "stale"
        basis = "an architecture-relevant file is newer than the artifact"
    executable = find_repomix(repo)
    npx = find_npx()
    return {
        "status": status,
        "freshnessBasis": basis,
        "artifact": str(artifact),
        "config": str(config.resolve()),
        "repomixExecutable": str(executable) if executable else None,
        "npxExecutable": str(npx) if npx else None,
        "downloadPolicy": "automatic" if allow_download else "disabled",
        "revision": git_revision(repo),
        "relevantFilesChecked": len(relevant),
        "canRegenerateWithoutInstall": executable is not None,
        "canRegenerate": executable is not None or (allow_download and npx is not None),
    }


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument(
        "--config",
        type=Path,
        default=skill_root / "assets" / "repomix-base.config.json",
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Do not use npx to download Repomix when no local executable exists.",
    )
    parser.add_argument(
        "--package",
        default="repomix@latest",
        help="Package spec passed to npx (default: repomix@latest).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Generation timeout in seconds (default: 300).",
    )
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    artifact = (args.artifact or repo / "repomix-output.xml").resolve()
    allow_download = not args.no_download
    payload = inspect(repo, artifact, args.config, allow_download=allow_download)
    if args.execute and payload["status"] != "fresh":
        invocation = resolve_invocation(
            repo,
            args.config,
            artifact,
            allow_download=allow_download,
            package=args.package,
        )
        payload["executionSource"] = invocation["source"]
        payload["package"] = invocation.get("package")
        command = invocation["command"]
        if not command:
            payload["error"] = invocation.get("reason", "Repomix generation is unavailable.")
            write_json(payload, args.json_out)
            return 2
        try:
            result = subprocess.run(
                command,
                cwd=repo,
                check=False,
                capture_output=True,
                text=True,
                timeout=max(1, args.timeout),
            )
        except subprocess.TimeoutExpired:
            payload["error"] = f"Repomix generation timed out after {max(1, args.timeout)} seconds."
            write_json(payload, args.json_out)
            return 124
        except OSError as exc:
            payload["error"] = f"Could not start Repomix generation: {exc}"
            write_json(payload, args.json_out)
            return 2
        if result.returncode != 0:
            payload["error"] = result.stderr.strip() or result.stdout.strip() or "Repomix failed"
            write_json(payload, args.json_out)
            return result.returncode or 1
        payload = inspect(repo, artifact, args.config, allow_download=allow_download)
        payload["status"] = "regenerated"
        payload["executionSource"] = invocation["source"]
        payload["package"] = invocation.get("package")
        payload["freshnessBasis"] = f"generated through {invocation['source']}"
    write_json(payload, args.json_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
