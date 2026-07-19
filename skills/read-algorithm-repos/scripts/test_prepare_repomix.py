#!/usr/bin/env python3

import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prepare_repomix


class RepomixBootstrapTests(unittest.TestCase):
    def test_generated_newcomer_reports_do_not_make_snapshot_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            source = repo / "src" / "model.py"
            source.parent.mkdir(parents=True)
            source.write_text("class Model:\n    pass\n", encoding="utf-8")
            artifact = repo / "repomix-output.xml"
            artifact.write_text("<repository/>", encoding="utf-8")
            time.sleep(0.01)
            report = repo / "docs" / "demo_newcomer_architecture.md"
            report.parent.mkdir(parents=True)
            report.write_text("# Generated report\n", encoding="utf-8")
            manifest = report.parent / "algorithm-repo-analysis.json"
            manifest.write_text("{}\n", encoding="utf-8")
            config = Path(__file__).resolve().parents[1] / "assets" / "repomix-base.config.json"

            payload = prepare_repomix.inspect(repo, artifact, config)

        self.assertEqual(payload["status"], "fresh")

    def test_uses_existing_repomix_before_npx(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / "node_modules" / ".bin" / "repomix"
            local.parent.mkdir(parents=True)
            local.write_text("", encoding="utf-8")

            invocation = prepare_repomix.resolve_invocation(
                repo, Path("config.json"), Path("repomix-output.xml")
            )

        self.assertEqual(invocation["source"], "project-local")
        self.assertEqual(invocation["command"][0], str(local))

    @patch.object(prepare_repomix.shutil, "which")
    def test_uses_npx_download_when_repomix_is_missing(self, which):
        which.side_effect = lambda name: "/usr/bin/npx" if name == "npx" else None
        with tempfile.TemporaryDirectory() as tmp:
            invocation = prepare_repomix.resolve_invocation(
                Path(tmp),
                Path("config.json"),
                Path("repomix-output.xml"),
                package="repomix@latest",
            )

        self.assertEqual(invocation["source"], "npx-download")
        self.assertEqual(
            invocation["command"][:3],
            ["/usr/bin/npx", "--yes", "repomix@latest"],
        )

    @patch.object(prepare_repomix.shutil, "which")
    def test_no_download_disables_npx_bootstrap(self, which):
        which.side_effect = lambda name: "/usr/bin/npx" if name == "npx" else None
        with tempfile.TemporaryDirectory() as tmp:
            invocation = prepare_repomix.resolve_invocation(
                Path(tmp),
                Path("config.json"),
                Path("repomix-output.xml"),
                allow_download=False,
            )

        self.assertIsNone(invocation["command"])
        self.assertEqual(invocation["source"], "unavailable")
        self.assertIn("disabled", invocation["reason"].lower())

    @patch.object(prepare_repomix, "os")
    def test_windows_discovers_npx_cmd(self, mocked_os):
        mocked_os.name = "nt"
        with patch.object(prepare_repomix.shutil, "which") as which:
            which.side_effect = lambda name: "C:\\Program Files\\nodejs\\npx.cmd" if name == "npx.cmd" else None
            result = prepare_repomix.find_npx()

        self.assertEqual(result, Path("C:\\Program Files\\nodejs\\npx.cmd"))


if __name__ == "__main__":
    unittest.main()
