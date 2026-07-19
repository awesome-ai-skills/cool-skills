#!/usr/bin/env python3

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_reports


class ReportContractTests(unittest.TestCase):
    def test_manifest_requires_v21_newcomer_contract(self):
        payload = {
            "schemaVersion": "2.0",
            "repository": {"name": "demo"},
            "capabilities": {},
            "domain": {"type": "generic-ml"},
            "statistics": {},
            "pipeline": [],
            "flows": [],
            "codeIndex": [],
            "assessment": {},
        }

        errors = validate_reports.validate_manifest(payload)

        self.assertTrue(any("schemaVersion" in error for error in errors))
        self.assertTrue(any("models" in error for error in errors))
        self.assertTrue(any("onboarding" in error for error in errors))

    def test_markdown_requires_newcomer_learning_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            path.write_text("# Report\n```mermaid\nflowchart LR\nA-->B\n```\n", encoding="utf-8")

            errors = validate_reports.validate_markdown(path, {"flows": [{}]})

        self.assertTrue(any("新人阅读路线" in error for error in errors))
        self.assertTrue(any("修改入口" in error for error in errors))
        self.assertTrue(any("核心模型" in error for error in errors))

    def test_html_requires_rich_code_map_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.html"
            path.write_text("<!doctype html><html><body><input id='categoryFilter'></body></html>", encoding="utf-8")

            errors = validate_reports.validate_html(path)

        for control_id in validate_reports.REQUIRED_CODE_MAP_CONTROLS - {"categoryFilter"}:
            self.assertTrue(any(control_id in error for error in errors), control_id)


if __name__ == "__main__":
    unittest.main()
