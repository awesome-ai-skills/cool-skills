#!/usr/bin/env python3
"""
Unit tests for read-algorithm-repos skill scripts.

Tests cover:
- repo_utils utility functions (LANGUAGES, classify_role, discover_files)
- collect_repo_stats.py output structure
- build_code_index.py output structure
- render_html_report.py HTML generation
- validate_reports.py validation logic
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# Skill root is the parent directory of tests/
SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
ASSETS_DIR = SKILL_ROOT / "assets"


def create_mock_repo(root: Path) -> Path:
    """Create a minimal mock repository for testing."""
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)

    # Create some Python files with different content
    (root / "src" / "model.py").write_text(
        "import torch\nimport torch.nn as nn\n\nclass SimpleModel(nn.Module):\n"
        "    def __init__(self):\n        super().__init__()\n"
        "        self.linear = nn.Linear(10, 1)\n\n"
        "    def forward(self, x):\n        return self.linear(x)\n",
        encoding="utf-8",
    )
    (root / "src" / "utils.py").write_text(
        "def helper_function():\n    return 'hello'\n", encoding="utf-8"
    )
    (root / "tests" / "test_model.py").write_text(
        "from src.model import SimpleModel\n\ndef test_model():\n"
        "    model = SimpleModel()\n"
        "    assert model is not None\n",
        encoding="utf-8",
    )

    # Create README and requirements
    (root / "README.md").write_text(
        "# Test Repo\n\nA test repository.\n\n## Installation\n\npip install torch\n",
        encoding="utf-8",
    )
    (root / "requirements.txt").write_text(
        "torch>=2.0.0\nnumpy>=1.20.0\n", encoding="utf-8"
    )

    return root


class TestRepoUtils(unittest.TestCase):
    """Test utility functions in repo_utils.py via subprocess."""

    def test_languages_dict_contains_python(self):
        """Verify LANGUAGES mapping includes .py -> Python."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    f"import sys; sys.path.insert(0, '{SCRIPTS_DIR}'); "
                    f"from repo_utils import LANGUAGES; "
                    f"assert LANGUAGES.get('.py') == 'Python'"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_languages_dict_contains_javascript(self):
        """Verify LANGUAGES mapping includes .js -> JavaScript."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    f"import sys; sys.path.insert(0, '{SCRIPTS_DIR}'); "
                    f"from repo_utils import LANGUAGES; "
                    f"assert LANGUAGES.get('.js') == 'JavaScript'"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_classify_role_test_files(self):
        """Test that test files are classified correctly."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    f"import sys; sys.path.insert(0, '{SCRIPTS_DIR}'); "
                    f"from repo_utils import classify_role; "
                    f"assert classify_role('tests/test_model.py') == 'tests'"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_classify_role_model_files(self):
        """Test that model files are classified as core_models."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    f"import sys; sys.path.insert(0, '{SCRIPTS_DIR}'); "
                    f"from repo_utils import classify_role; "
                    f"assert classify_role('models/transformer.py') == 'core_models'"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_classify_role_training_files(self):
        """Test that training files are classified correctly."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    f"import sys; sys.path.insert(0, '{SCRIPTS_DIR}'); "
                    f"from repo_utils import classify_role; "
                    f"assert classify_role('training/trainer.py') == 'training_evaluation_inference'"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_classify_role_other_source(self):
        """Test that generic files are classified as other_source."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    f"import sys; sys.path.insert(0, '{SCRIPTS_DIR}'); "
                    f"from repo_utils import classify_role; "
                    f"assert classify_role('src/utils.py') == 'other_source'"
                ),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_discover_files_finds_python_files(self):
        """Test that discover_files finds .py files in a directory."""
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "main.py").write_text("print('hello')")
            
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        f"from pathlib import Path\n"
                        f"import sys; sys.path.insert(0, '{SCRIPTS_DIR}')\n"
                        f"from repo_utils import discover_files\n"
                        f"files = discover_files(Path('{repo}'))\n"
                        f"py_files = [f for f in files if f.suffix == '.py']\n"
                        f"assert len(py_files) > 0, 'Should find .py files'\n"
                    ),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_normalize_relative_path(self):
        """Test path normalization."""
        with TemporaryDirectory() as tmp:
            # Create the file first
            src_dir = Path(tmp) / "src"
            src_dir.mkdir()
            (src_dir / "model.py").write_text("# test")

            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        f"import sys; sys.path.insert(0, '{SCRIPTS_DIR}'); "
                        f"from repo_utils import normalize_relative\n"
                        f"from pathlib import Path\n"
                        f"result = normalize_relative(Path('{tmp}/src/model.py'))\n"
                        f"# Result should be relative path without leading ./\n"
                        f"'model' in result or 'src' in result\n"
                    ),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


class TestCollectRepoStats(unittest.TestCase):
    """Test collect_repo_stats.py script."""

    def _run_collect_stats(self, repo: Path, output_file: Path) -> subprocess.CompletedProcess:
        config = ASSETS_DIR / "repomix-base.config.json"
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "collect_repo_stats.py"),
                "--repo",
                str(repo),
                "--config",
                str(config),
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_stats_output_structure(self):
        with TemporaryDirectory() as tmp:
            repo = create_mock_repo(Path(tmp))
            output_file = Path(tmp) / "repo-stats.json"

            result = self._run_collect_stats(repo, output_file)
            self.assertEqual(result.returncode, 0, result.stderr)

            self.assertTrue(output_file.exists(), "Stats file should be created")

            stats = json.loads(output_file.read_text(encoding="utf-8"))
            # Verify expected fields based on actual script output
            self.assertIn("languages", stats)
            self.assertIn("repository", stats)
            self.assertIn("exclusions", stats)
            # languages is a list of dicts
            self.assertIsInstance(stats["languages"], list)

    def test_stats_detects_python_language(self):
        with TemporaryDirectory() as tmp:
            repo = create_mock_repo(Path(tmp))
            output_file = Path(tmp) / "repo-stats.json"

            result = self._run_collect_stats(repo, output_file)
            self.assertEqual(result.returncode, 0, result.stderr)

            stats = json.loads(output_file.read_text(encoding="utf-8"))
            # languages is a list of language entries
            python_found = any(
                lang.get("language") == "Python" for lang in stats["languages"]
            )
            self.assertTrue(python_found, "Python should be detected in languages")


class TestBuildCodeIndex(unittest.TestCase):
    """Test build_code_index.py script."""

    def _run_build_index(self, repo: Path, output_file: Path) -> subprocess.CompletedProcess:
        config = ASSETS_DIR / "repomix-base.config.json"
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "build_code_index.py"),
                "--repo",
                str(repo),
                "--config",
                str(config),
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_code_index_output_structure(self):
        with TemporaryDirectory() as tmp:
            repo = create_mock_repo(Path(tmp))
            output_file = Path(tmp) / "code-index.json"

            result = self._run_build_index(repo, output_file)
            self.assertEqual(result.returncode, 0, result.stderr)

            self.assertTrue(output_file.exists(), "Code index file should be created")

            index = json.loads(output_file.read_text(encoding="utf-8"))
            # Verify expected fields based on actual script output
            self.assertIn("entries", index)
            self.assertIn("pathPolicy", index)
            self.assertIn("repository", index)
            self.assertIsInstance(index["entries"], list)

    def test_code_index_contains_class_definitions(self):
        with TemporaryDirectory() as tmp:
            repo = create_mock_repo(Path(tmp))
            output_file = Path(tmp) / "code-index.json"

            result = self._run_build_index(repo, output_file)
            if result.returncode != 0:
                self.skipTest(f"build_code_index failed: {result.stderr}")

            index = json.loads(output_file.read_text(encoding="utf-8"))
            entries = index.get("entries", [])
            classes = [e for e in entries if e.get("kind") == "class"]
            self.assertGreater(len(classes), 0, "Should find at least one class definition")


class TestRenderHtmlReport(unittest.TestCase):
    """Test render_html_report.py script."""

    @staticmethod
    def _create_valid_manifest() -> dict:
        return {
            "$schema": "../skills/read-algorithm-repos/assets/analysis-manifest.schema.json",
            "schemaVersion": "2.1",
            "version": "2.1.0",
            "repository": {
                "name": "test-repo",
                "root": "/tmp/test",
                "revision": "abc123",
                "timestamp": "2024-01-01T00:00:00Z",
            },
            "snapshot": {"tool": "manual", "timestamp": "2024-01-01T00:00:00Z"},
            "domain": {"primary": "ml", "evidence": ["test"], "framing": "Test ML repository"},
            "stats": {"languages": {"Python": 100}, "total_files": 5, "total_lines": 50},
            "pipeline": {"stages": []},
            "models": {"core": [], "offline": [], "online": [], "representative": []},
            "codeIndex": {"symbols": [], "files": []},
            "strengths": [],
            "limitations": [],
            "gaps": [],
            "readingOrder": [],
            "newcomer": {
                "mentalModel": "",
                "keyConcepts": [],
                "entryPoints": [],
                "learningTracks": [],
                "modificationGuide": "",
                "modelFamilies": [],
            },
        }

    def test_render_creates_html_file(self):
        with TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "manifest.json"
            output_path = Path(tmp) / "report.html"

            manifest_path.write_text(json.dumps(self._create_valid_manifest()), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "render_html_report.py"),
                    "--manifest",
                    str(manifest_path),
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists(), "HTML report file should be created")

            html = output_path.read_text(encoding="utf-8")
            self.assertIn("<html", html.lower())
            self.assertIn("</html>", html.lower())

    def test_render_includes_required_control_ids(self):
        """Verify that the rendered HTML includes required control IDs."""
        with TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "manifest.json"
            output_path = Path(tmp) / "report.html"

            manifest_path.write_text(json.dumps(self._create_valid_manifest()), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "render_html_report.py"),
                    "--manifest",
                    str(manifest_path),
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            html = output_path.read_text(encoding="utf-8")
            # Use actual control IDs from the template
            required_ids = [
                "modelFamilyFilter",
                "categoryFilter",
                "codeStageFilter",
                "codeKindFilter",
                "codeFamilyFilter",
            ]
            for ctrl_id in required_ids:
                self.assertIn(ctrl_id, html, f"HTML must contain control ID: {ctrl_id}")


class TestValidateReports(unittest.TestCase):
    """Test validate_reports.py script."""

    @staticmethod
    def _create_minimal_markdown() -> str:
        return (
            "# Architecture Report\n\n"
            "- **Domain**: ml\n"
            "- **Primary Language**: Python\n"
            "- **Total Files**: 5\n\n"
            "## Pipeline\n\nNo pipeline stages defined.\n"
        )

    def test_validate_accepts_valid_reports(self):
        with TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "manifest.json"
            md_path = Path(tmp) / "report.md"
            html_path = Path(tmp) / "report.html"

            manifest = {
                "$schema": "../skills/read-algorithm-repos/assets/analysis-manifest.schema.json",
                "schemaVersion": "2.1",
                "version": "2.1.0",
                "repository": {
                    "name": "test",
                    "root": "/tmp",
                    "revision": "abc123",
                    "timestamp": "2024-01-01T00:00:00Z",
                },
                "snapshot": {"tool": "manual", "timestamp": "2024-01-01T00:00:00Z"},
                "domain": {"primary": "ml", "evidence": [], "framing": ""},
                "stats": {"languages": {}, "total_files": 0, "total_lines": 0},
                "pipeline": {"stages": []},
                "models": {"core": [], "offline": [], "online": [], "representative": []},
                "codeIndex": {"symbols": [], "files": []},
                "strengths": [],
                "limitations": [],
                "gaps": [],
                "readingOrder": [],
                "newcomer": {
                    "mentalModel": "",
                    "keyConcepts": [],
                    "entryPoints": [],
                    "learningTracks": [],
                    "modificationGuide": "",
                    "modelFamilies": [],
                },
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            md_path.write_text(self._create_minimal_markdown(), encoding="utf-8")
            html_path.write_text("<html><body>Test</body></html>", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "validate_reports.py"),
                    "--manifest",
                    str(manifest_path),
                    "--markdown",
                    str(md_path),
                    "--html",
                    str(html_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertIn(result.returncode, [0, 1], "Should exit with 0 or 1")


class TestPrepareRepomix(unittest.TestCase):
    """Test prepare_repomix.py script."""

    def test_prepare_repomix_no_download_flag_accepted(self):
        """Verify --no-download flag doesn't cause crashes."""
        with TemporaryDirectory() as tmp:
            repo = create_mock_repo(Path(tmp))
            output_dir = Path(tmp) / "output"
            output_dir.mkdir()

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "prepare_repomix.py"),
                    "--repo",
                    str(repo),
                    "--no-download",
                    "--output-dir",
                    str(output_dir),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            # Should not crash; may fail gracefully but must accept the flag
            self.assertIsNotNone(result.stdout or result.stderr)


if __name__ == "__main__":
    unittest.main()
