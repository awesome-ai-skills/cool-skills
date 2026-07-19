#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_reports


class HtmlRendererTests(unittest.TestCase):
    def test_renders_self_contained_v21_cockpit(self):
        payload = {
            "schemaVersion": "2.1",
            "repository": {"name": "Demo", "snapshot": {"status": "fresh", "freshnessBasis": "test"}},
            "capabilities": {"filesystem": True, "shell": True, "browserAutomation": False},
            "domain": {"type": "generic-ml", "summary": "Demo", "evidence": ["test"]},
            "statistics": {"metric": "lines", "totals": {"files": 1, "lines": 2}, "roles": []},
            "pipeline": [], "flows": [], "models": [], "codeIndex": [],
            "onboarding": {"mentalModel": "Demo", "keyConcepts": [], "readingTracks": [], "modificationGuide": []},
            "assessment": {"strengths": [], "limitations": [], "productionGaps": []},
        }
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.json"
            output = Path(tmp) / "report.html"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("render_html_report.py")), "--manifest", str(manifest), "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            errors = validate_reports.validate_html(output)
            rendered = output.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(errors, [])
        self.assertIn('type="application/json"', rendered)
        self.assertNotIn("https://", rendered)


if __name__ == "__main__":
    unittest.main()
