#!/usr/bin/env python3
"""Validate the shared manifest and offline Markdown/HTML report contracts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Tuple

from repo_utils import write_json


REQUIRED_MANIFEST_FIELDS = {
    "schemaVersion": str,
    "repository": dict,
    "capabilities": dict,
    "domain": dict,
    "statistics": dict,
    "pipeline": list,
    "flows": list,
    "models": list,
    "codeIndex": list,
    "onboarding": dict,
    "assessment": dict,
}

REQUIRED_CODE_MAP_CONTROLS = {
    "codeSearch",
    "categoryFilter",
    "codeStageFilter",
    "codeKindFilter",
    "codeFamilyFilter",
    "codeImportanceFilter",
    "codeLearningFilter",
    "codePathFilter",
    "coreOnly",
    "codeSort",
    "activeFilters",
    "clearCode",
}

REQUIRED_HTML_SECTIONS = {"model-atlas", "code-map", "learning-route", "change-guide"}


class ReportHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: List[str] = []
        self.hash_links: List[str] = []
        self.remote_runtime: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        href = values.get("href", "")
        if tag == "a" and href.startswith("#") and len(href) > 1:
            self.hash_links.append(href[1:])
        runtime_url = ""
        if tag == "script" and values.get("src"):
            runtime_url = values["src"]
        elif tag == "img" and values.get("src"):
            runtime_url = values["src"]
        elif tag == "link" and "stylesheet" in values.get("rel", "").lower():
            runtime_url = href
        if runtime_url.startswith(("http://", "https://", "//")):
            self.remote_runtime.append(runtime_url)


def validate_manifest(payload: object) -> List[str]:
    if not isinstance(payload, dict):
        return ["manifest root must be an object"]
    errors: List[str] = []
    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        if field not in payload:
            errors.append(f"manifest is missing required field: {field}")
        elif not isinstance(payload[field], expected):
            errors.append(f"manifest field {field} must be {expected.__name__}")
    if payload.get("schemaVersion") != "2.1":
        errors.append("manifest schemaVersion must be 2.1")
    repository = payload.get("repository", {})
    if isinstance(repository, dict) and not repository.get("name"):
        errors.append("manifest repository.name is required")
    domain = payload.get("domain", {})
    if isinstance(domain, dict) and not domain.get("type"):
        errors.append("manifest domain.type is required")
    code_index = payload.get("codeIndex", [])
    if isinstance(code_index, list) and len(code_index) > 10:
        semantic_fields = {
            "category",
            "stage",
            "kind",
            "language",
            "pathRoot",
            "importance",
            "learningPhase",
            "modelFamily",
        }
        for field in sorted(semantic_fields):
            if any(field not in item for item in code_index if isinstance(item, dict)):
                errors.append(f"codeIndex entries must include newcomer filter field: {field}")
    models = payload.get("models", [])
    if isinstance(models, list):
        for index, model in enumerate(models):
            if not isinstance(model, dict):
                errors.append(f"models[{index}] must be an object")
                continue
            for field in ("name", "family", "problem", "architecture", "sources"):
                if not model.get(field):
                    errors.append(f"models[{index}] is missing required learning field: {field}")
    onboarding = payload.get("onboarding", {})
    if isinstance(onboarding, dict):
        for field in ("mentalModel", "keyConcepts", "readingTracks", "modificationGuide"):
            if not onboarding.get(field):
                errors.append(f"onboarding.{field} is required")
    return errors


def validate_markdown(path: Path, payload: Dict[str, object]) -> List[str]:
    text = path.read_text(encoding="utf-8")
    errors: List[str] = []
    if text.count("```") % 2:
        errors.append("Markdown has an unbalanced fenced code block")
    if payload.get("flows") and not re.search(r"```mermaid\s+", text, flags=re.IGNORECASE):
        errors.append("Markdown must contain a Mermaid diagram when manifest flows are present")
    required_sections = {
        "核心模型 / Core Models": r"核心模型|core\s+models?",
        "新人阅读路线 / Newcomer Reading Route": r"新人阅读路线|newcomer\s+reading",
        "修改入口 / Modification Guide": r"修改入口|modification\s+guide|where\s+to\s+modify",
    }
    for label, pattern in required_sections.items():
        if not re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"Markdown is missing required newcomer section: {label}")
    return errors


def validate_html(path: Path) -> List[str]:
    parser = ReportHTMLParser()
    parser.feed(path.read_text(encoding="utf-8"))
    errors: List[str] = []
    duplicates = sorted(item for item, count in Counter(parser.ids).items() if count > 1)
    for item in duplicates:
        errors.append(f"duplicate HTML id: {item}")
    available = set(parser.ids)
    for target in sorted(set(parser.hash_links) - available):
        errors.append(f"HTML hash link has no target: #{target}")
    for url in parser.remote_runtime:
        errors.append(f"HTML has an external runtime dependency: {url}")
    for control_id in sorted(REQUIRED_CODE_MAP_CONTROLS - available):
        errors.append(f"HTML is missing required Code Map control: #{control_id}")
    for section_id in sorted(REQUIRED_HTML_SECTIONS - available):
        errors.append(f"HTML is missing required newcomer section: #{section_id}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--html", type=Path)
    args = parser.parse_args()
    errors: List[str] = []
    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        payload = {}
        errors.append(f"cannot read manifest JSON: {exc}")
    errors.extend(validate_manifest(payload))
    if args.markdown:
        errors.extend(validate_markdown(args.markdown, payload))
    if args.html:
        errors.extend(validate_html(args.html))
    result = {"valid": not errors, "errors": errors}
    write_json(result)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
