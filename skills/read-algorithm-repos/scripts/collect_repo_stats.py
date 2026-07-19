#!/usr/bin/env python3
"""Measure repository language and role scale without external packages."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from repo_utils import (
    LANGUAGES,
    classify_role,
    discover_files,
    git_revision,
    load_custom_patterns,
    normalize_relative,
    write_json,
)


def non_empty_lines(path: Path) -> int:
    try:
        return sum(
            1
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
            if line.strip()
        )
    except OSError:
        return 0


def collect(repo: Path, config: Path | None = None) -> Dict[str, object]:
    repo = repo.resolve()
    patterns = load_custom_patterns(config)
    language_totals: Dict[str, Dict[str, object]] = defaultdict(
        lambda: {"files": 0, "lines": 0, "mainPaths": []}
    )
    role_totals: Dict[str, Dict[str, object]] = defaultdict(
        lambda: {"files": 0, "lines": 0, "representativePaths": []}
    )
    files = discover_files(repo, extensions=LANGUAGES, patterns=patterns)
    for path in files:
        relative = normalize_relative(path.relative_to(repo))
        language = LANGUAGES[path.suffix.lower()]
        role = classify_role(relative)
        lines = non_empty_lines(path)
        language_totals[language]["files"] += 1
        language_totals[language]["lines"] += lines
        role_totals[role]["files"] += 1
        role_totals[role]["lines"] += lines
        if len(language_totals[language]["mainPaths"]) < 5:
            language_totals[language]["mainPaths"].append(relative)
        if len(role_totals[role]["representativePaths"]) < 5:
            role_totals[role]["representativePaths"].append(relative)

    total_lines = sum(int(item["lines"]) for item in language_totals.values())
    languages: List[Dict[str, object]] = []
    for language, values in language_totals.items():
        languages.append(
            {
                "language": language,
                "files": values["files"],
                "lines": values["lines"],
                "share": round(int(values["lines"]) / total_lines, 6)
                if total_lines
                else 0.0,
                "mainPaths": values["mainPaths"],
            }
        )
    languages.sort(key=lambda item: (-int(item["lines"]), str(item["language"])))

    roles = [
        {"role": role, **values}
        for role, values in sorted(
            role_totals.items(), key=lambda item: (-int(item[1]["lines"]), item[0])
        )
    ]
    return {
        "metric": "non_empty_physical_lines",
        "method": "bundled Python standard-library counter",
        "repository": {
            "name": repo.name,
            "revision": git_revision(repo),
        },
        "totals": {"files": len(files), "lines": total_lines},
        "primaryLanguage": languages[0]["language"] if languages else None,
        "languages": languages,
        "roles": roles,
        "exclusions": {
            "source": "Repomix base config plus built-in noise filters",
            "customPatterns": patterns,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    write_json(collect(args.repo, args.config), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

