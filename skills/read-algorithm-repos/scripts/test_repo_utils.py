#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from repo_utils import classify_role


class RoleClassificationTests(unittest.TestCase):
    def test_module_filenames_are_classified_without_matching_directories(self):
        self.assertEqual(classify_role("package/inputs.py"), "data_input")
        self.assertEqual(classify_role("package/features.py"), "data_input")
        self.assertEqual(classify_role("package/callbacks.py"), "training_evaluation_inference")
        self.assertEqual(classify_role("package/trainer.py"), "training_evaluation_inference")


if __name__ == "__main__":
    unittest.main()
