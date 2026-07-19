#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write_skill(repo_root: Path, name: str) -> Path:
    skill_root = repo_root / "skills" / name
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill for repository tooling.\n---\n\n# Test\n",
        encoding="utf-8",
    )
    return skill_root


class RepositoryScriptTests(unittest.TestCase):
    def test_validate_all_skills_scans_skills_directory_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_skill(repo, "demo-skill")
            incubator = repo / "incubator" / "draft-skill"
            incubator.mkdir(parents=True)
            (incubator / "SKILL.md").write_text(
                "---\nname: draft-skill\ndescription: Draft.\n---\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_all_skills.py"),
                    "--root",
                    str(repo),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["valid"])
            self.assertEqual([item["name"] for item in payload["skills"]], ["demo-skill"])

    def test_install_skill_project_scope_copies_requested_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            target_project = Path(tmp) / "target"
            write_skill(repo, "demo-skill")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "install_skill.py"),
                    "demo-skill",
                    "--client",
                    "codex",
                    "--scope",
                    "project",
                    "--project-root",
                    str(target_project),
                    "--repository",
                    str(repo),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            installed = target_project / ".codex" / "skills" / "demo-skill" / "SKILL.md"
            self.assertTrue(installed.is_file())
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "installed")


if __name__ == "__main__":
    unittest.main()
