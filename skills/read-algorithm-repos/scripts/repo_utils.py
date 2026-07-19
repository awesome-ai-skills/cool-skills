#!/usr/bin/env python3
"""Shared, dependency-free repository helpers for the skill scripts."""

from __future__ import annotations

import fnmatch
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence


LANGUAGES: Dict[str, str] = {
    ".py": "Python",
    ".pyx": "Cython",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".scala": "Scala",
    ".go": "Go",
    ".rs": "Rust",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cc": "C++",
    ".cpp": "C++",
    ".cxx": "C++",
    ".hpp": "C/C++ Header",
    ".cu": "CUDA",
    ".cuh": "CUDA",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".r": "R",
    ".R": "R",
    ".jl": "Julia",
    ".lua": "Lua",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
}

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "coverage",
    "htmlcov",
    "logs",
    "outputs",
    "weights",
    "checkpoints",
}

DEFAULT_EXCLUDED_SUFFIXES = {
    ".log",
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".dll",
    ".zip",
    ".tar",
    ".gz",
    ".parquet",
    ".feather",
    ".npy",
    ".npz",
    ".pt",
    ".pth",
    ".ckpt",
    ".h5",
    ".onnx",
}


def normalize_relative(path: Path) -> str:
    return path.as_posix().lstrip("./")


def load_custom_patterns(config_path: Optional[Path]) -> List[str]:
    if not config_path or not config_path.is_file():
        return []
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    patterns = payload.get("ignore", {}).get("customPatterns", [])
    return [str(item).strip() for item in patterns if str(item).strip()]


def matches_any_pattern(relative_path: str, patterns: Sequence[str]) -> bool:
    path = relative_path.replace("\\", "/").lstrip("./")
    candidates = {path, f"/{path}"}
    for pattern in patterns:
        normalized = pattern.replace("\\", "/").strip()
        if normalized.startswith("**/"):
            suffix = normalized[3:].rstrip("/")
            if fnmatch.fnmatch(path, suffix) or fnmatch.fnmatch(path, f"*/{suffix}"):
                return True
        if normalized.startswith("**/"):
            normalized = normalized[3:]
        normalized = normalized.rstrip("/")
        for candidate in candidates:
            if fnmatch.fnmatch(candidate, normalized) or fnmatch.fnmatch(
                candidate, f"{normalized}/**"
            ):
                return True
        if normalized.startswith("repomix-output.") and Path(path).name.startswith(
            "repomix-output."
        ):
            return True
    return False


def is_excluded(relative_path: str, patterns: Sequence[str] = ()) -> bool:
    path = Path(relative_path)
    if any(part in DEFAULT_EXCLUDED_DIRS for part in path.parts[:-1]):
        return True
    if path.suffix.lower() in DEFAULT_EXCLUDED_SUFFIXES:
        return True
    if path.name == ".DS_Store" or path.name.startswith("repomix-output."):
        return True
    return matches_any_pattern(relative_path, patterns)


def git_file_list(repo: Path) -> Optional[List[str]]:
    try:
        probe = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
            check=False,
            capture_output=True,
            text=True,
        )
        if probe.returncode != 0:
            return None
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})
    except (OSError, subprocess.SubprocessError):
        return None


def discover_files(
    repo: Path,
    *,
    extensions: Optional[Iterable[str]] = None,
    patterns: Sequence[str] = (),
) -> List[Path]:
    allowed = {suffix.lower() for suffix in extensions} if extensions else None
    listed = git_file_list(repo)
    files: List[Path] = []
    if listed is not None:
        candidates = (repo / item for item in listed)
    else:
        candidates = (
            Path(root) / name
            for root, dirs, names in os.walk(repo)
            for _ in [dirs.__setitem__(slice(None), sorted(d for d in dirs if d not in DEFAULT_EXCLUDED_DIRS))]
            for name in sorted(names)
        )
    for path in candidates:
        if not path.is_file():
            continue
        relative = normalize_relative(path.relative_to(repo))
        if is_excluded(relative, patterns):
            continue
        if allowed is not None and path.suffix.lower() not in allowed:
            continue
        files.append(path)
    return sorted(files, key=lambda item: normalize_relative(item.relative_to(repo)))


def git_revision(repo: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None if result.returncode == 0 else None
    except OSError:
        return None


def classify_role(relative_path: str) -> str:
    path = relative_path.lower().replace("\\", "/")
    parts = set(path.split("/"))
    stem = Path(path).stem
    if "test" in parts or "tests" in parts or Path(path).name.startswith("test_"):
        return "tests"
    if "example" in parts or "examples" in parts or "demo" in parts or "demos" in parts:
        return "examples"
    if parts & {"layer", "layers", "operator", "operators", "ops", "modules"}:
        return "layers_operators"
    if parts & {"model", "models", "network", "networks", "architectures"}:
        return "core_models"
    if parts & {"data", "dataset", "datasets", "feature", "features", "input", "inputs"} or stem in {
        "data", "dataset", "datasets", "feature", "features", "input", "inputs"
    }:
        return "data_input"
    if parts & {
        "train",
        "training",
        "trainer",
        "evaluation",
        "evaluate",
        "inference",
        "serving",
        "export",
    } or stem in {
        "train", "training", "trainer", "callbacks", "callback", "evaluation",
        "evaluate", "evaluator", "inference", "predict", "serving", "export",
    }:
        return "training_evaluation_inference"
    return "other_source"


def write_json(payload: object, output: Optional[Path] = None) -> None:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
