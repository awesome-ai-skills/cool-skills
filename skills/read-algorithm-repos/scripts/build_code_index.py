#!/usr/bin/env python3
"""Build a portable source-symbol index with line-aware navigation targets."""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path
from typing import Dict, Iterable, List
from urllib.parse import quote

from repo_utils import (
    LANGUAGES,
    classify_role,
    discover_files,
    load_custom_patterns,
    normalize_relative,
    write_json,
)


def absolute_path_to_file_uri(value: str) -> str:
    raw = value.strip()
    if raw.startswith("\\\\") or raw.startswith("//"):
        normalized = re.sub(r"[\\/]+", "/", raw).lstrip("/")
        host, _, remainder = normalized.partition("/")
        return f"file://{quote(host)}/{quote(remainder, safe='/@:')}"
    if re.match(r"^[A-Za-z]:[\\/]", raw):
        normalized = re.sub(r"[\\/]+", "/", raw)
        return "file:///" + quote(normalized, safe="/:@")
    return Path(raw).resolve().as_uri()


def editor_uri(file_uri: str, line: int, column: int = 1) -> str:
    suffix = file_uri[len("file://") :]
    if not suffix.startswith("/"):
        suffix = "/" + suffix
    return f"vscode://file{suffix}:{line}:{column}"


class PythonSymbols(ast.NodeVisitor):
    def __init__(self) -> None:
        self.entries: List[Dict[str, object]] = []
        self.parents: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        symbol = ".".join([*self.parents, node.name])
        self.entries.append({"symbol": symbol, "kind": "class", "line": node.lineno})
        self.parents.append(node.name)
        self.generic_visit(node)
        self.parents.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        symbol = ".".join([*self.parents, node.name])
        kind = "method" if self.parents else "function"
        self.entries.append({"symbol": symbol, "kind": kind, "line": node.lineno})
        if not self.parents:
            self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


DECLARATION_PATTERNS = [
    ("class", re.compile(r"^\s*(?:export\s+)?(?:public\s+)?class\s+([A-Za-z_$][\w$]*)")),
    ("function", re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)")),
    ("function", re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)")),
    ("class", re.compile(r"^\s*(?:pub\s+)?(?:struct|enum|trait)\s+([A-Za-z_]\w*)")),
    ("function", re.compile(r"^\s*(?:pub\s+)?fn\s+([A-Za-z_]\w*)")),
]


def symbols_for(path: Path) -> Iterable[Dict[str, object]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".py":
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError:
            return []
        visitor = PythonSymbols()
        visitor.visit(tree)
        return visitor.entries
    entries: List[Dict[str, object]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in DECLARATION_PATTERNS:
            match = pattern.match(line)
            if match:
                entries.append({"symbol": match.group(1), "kind": kind, "line": number})
                break
    return entries


def learning_metadata(category: str, kind: str) -> Dict[str, object]:
    if category == "core_models":
        importance = "core" if kind == "class" else "important"
        phase = "model-deep-dive"
    elif category in {"data_input", "layers_operators"}:
        importance = "important" if kind == "class" else "supporting"
        phase = "foundation"
    elif category == "examples":
        importance = "important"
        phase = "orientation"
    elif category in {"tests", "training_evaluation_inference"}:
        importance = "reference" if category == "tests" else "important"
        phase = "training-validation"
    else:
        importance = "supporting"
        phase = "foundation"
    return {
        "importance": importance,
        "learningPhase": phase,
        "modelFamily": None,
        "summary": None,
        "tags": [],
    }


def build(repo: Path, config: Path | None = None) -> Dict[str, object]:
    repo = repo.resolve()
    patterns = load_custom_patterns(config)
    entries: List[Dict[str, object]] = []
    for path in discover_files(repo, extensions=LANGUAGES, patterns=patterns):
        relative = normalize_relative(path.relative_to(repo))
        absolute = str(path.resolve())
        file_uri = absolute_path_to_file_uri(absolute)
        category = classify_role(relative)
        path_root = relative.split("/", 1)[0]
        language = LANGUAGES.get(path.suffix.lower(), path.suffix.lstrip(".") or "Unknown")
        for symbol in symbols_for(path):
            line = int(symbol["line"])
            entry = {
                    "relativePath": relative,
                    "absolutePath": absolute,
                    "fileUri": file_uri,
                    "editorUri": editor_uri(file_uri, line),
                    "symbol": symbol["symbol"],
                    "kind": symbol["kind"],
                    "line": line,
                    "language": language,
                    "pathRoot": path_root,
                    "category": category,
                    "stage": None,
                }
            entry.update(learning_metadata(category, str(symbol["kind"])))
            entries.append(entry)
    entries.sort(key=lambda item: (str(item["relativePath"]), int(item["line"]), str(item["symbol"])))
    return {
        "repository": {"name": repo.name, "root": str(repo)},
        "pathPolicy": "relative-primary; absolute and URI fields are machine-local enhancements",
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    write_json(build(args.repo, args.config), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
