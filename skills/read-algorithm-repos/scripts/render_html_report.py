#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a self-contained newcomer architecture cockpit from a V2.1 manifest."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

# Default template location relative to this script's directory
_DEFAULT_TEMPLATE = Path(__file__).parent.parent / "assets" / "report-template.html"


def load_template(template_path: str | None) -> str:
    """Load HTML template from file.

    Args:
        template_path: Optional path to template file. If not provided,
                       uses the default report-template.html in assets/.

    Returns:
        Template string content.
    """
    if template_path:
        p = Path(template_path)
    else:
        p = _DEFAULT_TEMPLATE

    if not p.exists():
        raise FileNotFoundError(f"Template file not found: {p}")
    return p.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Path to V2.1 manifest JSON")
    parser.add_argument("--output", required=True, type=Path, help="Output HTML file path")
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Optional path to custom HTML template (default: assets/report-template.html)",
    )
    args = parser.parse_args()

    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != "2.1":
        raise SystemExit("render_html_report.py requires manifest schemaVersion 2.1")

    # Load and render template
    template_str = load_template(args.template)
    repo = str(payload.get("repository", {}).get("name") or "Algorithm Repository")
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")

    rendered = (
        template_str.replace("__TITLE__", html.escape(f"{repo} 新人架构导读"))
        .replace("__REPO__", html.escape(repo))
        .replace("__REPORT_DATA__", encoded)
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
