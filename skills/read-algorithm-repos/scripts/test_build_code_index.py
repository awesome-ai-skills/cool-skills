#!/usr/bin/env python3

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_code_index


class CodeIndexLearningMetadataTests(unittest.TestCase):
    def test_model_symbols_receive_portable_learning_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            model = repo / "package" / "models" / "deepfm.py"
            model.parent.mkdir(parents=True)
            model.write_text(
                "class DeepFM:\n    def forward(self, x):\n        return x\n",
                encoding="utf-8",
            )

            payload = build_code_index.build(repo)

        entry = next(item for item in payload["entries"] if item["symbol"] == "DeepFM")
        self.assertEqual(entry["language"], "Python")
        self.assertEqual(entry["pathRoot"], "package")
        self.assertEqual(entry["importance"], "core")
        self.assertEqual(entry["learningPhase"], "model-deep-dive")
        self.assertEqual(entry["modelFamily"], None)
        self.assertEqual(entry["tags"], [])

    def test_test_symbols_are_classified_for_validation_learning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            test_file = repo / "tests" / "test_model.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("def test_model():\n    pass\n", encoding="utf-8")

            payload = build_code_index.build(repo)

        entry = payload["entries"][0]
        self.assertEqual(entry["importance"], "reference")
        self.assertEqual(entry["learningPhase"], "training-validation")


if __name__ == "__main__":
    unittest.main()
