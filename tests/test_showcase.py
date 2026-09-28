"""Evidence checks must reject broken controls even if summary counts look good."""
import copy
from pathlib import Path
import runpy
import unittest

from authdrift import run

ROOT = Path(__file__).resolve().parents[1]
validate = runpy.run_path(str(ROOT / "benchmarks" / "showcase.py"))["validate_report"]


class ShowcaseEvidenceTests(unittest.TestCase):
    def setUp(self):
        factory = runpy.run_path(str(ROOT / "examples" / "refund" / "scenario.py"))["build_scenario"]
        self.report = run(factory, repeats=2, quiet=True)

    def test_accepts_actual_fixture_with_all_controls(self):
        self.assertTrue(validate(self.report, "REVOCATION_ESCAPE", 2))

    def test_rejects_missing_or_failed_control(self):
        for field, value in (("result", "BASELINE_FAILURE"), ("committed", True)):
            damaged = copy.deepcopy(self.report)
            damaged["trials"][0]["experiments"][1][field] = value
            self.assertFalse(validate(damaged, "REVOCATION_ESCAPE", 2))
        damaged = copy.deepcopy(self.report)
        damaged["trials"][0]["experiments"].pop(0)
        self.assertFalse(validate(damaged, "REVOCATION_ESCAPE", 2))

    def test_rejects_partial_trials_or_wrong_expected_outcome(self):
        self.assertFalse(validate(self.report, "CLOSED", 2))
        self.report["valid_trials"] = 1
        self.assertFalse(validate(self.report, "REVOCATION_ESCAPE", 2))
