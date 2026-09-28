from pathlib import Path
import runpy
import unittest

from authdrift import run

ROOT = Path(__file__).resolve().parents[1]
build = runpy.run_path(str(ROOT / "examples/consumed_approval/scenario.py"))["build_scenario"]


class ConsumedApprovalTests(unittest.TestCase):
    def test_controls_ordering_and_independent_state(self):
        for safe in (False, True):
            with self.subTest(safe=safe):
                evidence = []
                report = run(lambda: build(safe=safe, evidence=evidence), repeats=2, quiet=True)
                self.assertEqual(report["result"], "CLOSED" if safe else "REVOCATION_ESCAPE")
                self.assertEqual(report["valid_trials"], 2)
                self.assertEqual(len(evidence), 6)
                self.assertEqual(len({id(state) for state in evidence}), 6)
                for offset in (0, 3):
                    positive, negative, mid = evidence[offset:offset + 3]
                    self.assertEqual(positive["effects"], ["EFFECT-002"])
                    self.assertEqual(positive["remaining_uses"], 0)
                    self.assertEqual(positive["reservations"], [])
                    self.assertEqual(negative["effects"], [])
                    self.assertEqual(negative["reservations"], ["RES-001"])
                    self.assertEqual(mid["effects"], [] if safe else ["EFFECT-002"])
                    self.assertEqual(mid["reservations"], ["RES-001"])
                    self.assertEqual(mid["remaining_uses"], 0)
                    kinds = [event["type"] for event in mid["events"]]
                    self.assertLess(kinds.index("authority_observed"), kinds.index("approval_consumed"))
                    self.assertLess(kinds.index("approval_consumed"), kinds.index("later_effect_attempted"))
                    consumed = next(e for e in mid["events"] if e["type"] == "approval_consumed")
                    self.assertEqual(consumed["cause_id"], "RES-001")

    def test_ledger_is_not_an_authorization_input(self):
        evidence = []
        scenario = build(safe=True, evidence=evidence)
        evidence[0]["events"].append({"type": "approval_consumed"})
        self.assertFalse(scenario.revoked())
        scenario.revoke()
        evidence[0]["events"].clear()
        self.assertTrue(scenario.revoked())
        self.assertFalse(scenario.committed())
