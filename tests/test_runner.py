import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from authdrift import Scenario, checkpoint, run

ROOT = Path(__file__).resolve().parents[1]


def factory(safe=False, broken=False, no_checkpoint=False, no_effect=False,
            never_confirm=False, precommit=False, restore=False, swallow=False):
    def build():
        state = {"valid": True, "effect": False}
        def workflow():
            observed = state["valid"]
            if precommit and observed:
                state["effect"] = True
            if not no_checkpoint:
                try:
                    checkpoint("authority_observed")
                except Exception:
                    if not swallow:
                        raise
            if restore:
                state["valid"] = True
            if not no_effect and (broken or (state["valid"] if safe else observed)):
                state["effect"] = True
        return Scenario("test", workflow, lambda: state.update(valid=False),
                        lambda: False if never_confirm else not state["valid"],
                        lambda: state["effect"], confirmation_timeout=0.005)
    return build


class RunnerTests(unittest.TestCase):
    def outcome(self, source, **kwargs):
        return run(source, quiet=True, **kwargs)

    def test_vulnerable(self):
        report = self.outcome(factory(), repeats=20)
        self.assertEqual(report["result"], "REVOCATION_ESCAPE")
        self.assertEqual(report["escape_rate"], 1)
        self.assertEqual(report["valid_trials"], 20)
        ids = [e["run_id"] for t in report["trials"] for e in t["experiments"]]
        self.assertEqual(len(set(ids)), 60)

    def test_safe(self):
        self.assertEqual(self.outcome(factory(safe=True))["result"], "CLOSED")

    def test_broken_baseline(self):
        report = self.outcome(factory(broken=True))
        self.assertEqual(report["result"], "BASELINE_FAILURE")
        self.assertIsNone(report["escape_rate"])
        self.assertEqual(len(report["trials"][0]["experiments"]), 2)

    def test_invalid_cases(self):
        for option in ("no_checkpoint", "no_effect", "never_confirm", "precommit", "restore"):
            with self.subTest(option=option):
                self.assertEqual(self.outcome(factory(**{option: True}))["result"], "INVALID_EXPERIMENT")

    def test_event_order(self):
        experiment = self.outcome(factory())["trials"][0]["experiments"][-1]
        events = experiment["events"]
        names = [e["event"] for e in events]
        self.assertLess(names.index("revocation_confirmed"), names.index("sink_absent_after_confirmation"))
        self.assertLess(names.index("sink_absent_after_confirmation"), names.index("effect_observed"))
        self.assertEqual([e["sequence"] for e in events], list(range(len(events))))
        self.assertEqual([e["t_ms"] for e in events], sorted(e["t_ms"] for e in events))

    def test_outside_checkpoint(self):
        checkpoint("anything")

    def test_instance_requires_reset(self):
        self.assertEqual(self.outcome(factory()())["result"], "INVALID_EXPERIMENT")

    def test_reset_instance(self):
        state = {}
        def workflow():
            valid = state["valid"]
            checkpoint("authority_observed")
            state["effect"] = valid
        scenario = Scenario("reset", workflow, lambda: state.update(valid=False),
                            lambda: not state["valid"], lambda: state["effect"],
                            reset=lambda: state.update(valid=True, effect=False))
        self.assertEqual(self.outcome(scenario, repeats=3)["escapes"], 3)

    def test_bad_predicate(self):
        def build():
            scenario = factory()()
            scenario.committed = lambda: None
            return scenario
        self.assertEqual(self.outcome(build)["result"], "INVALID_EXPERIMENT")

    def test_factory_error(self):
        def build():
            raise RuntimeError("setup error")
        self.assertEqual(self.outcome(build)["result"], "INVALID_EXPERIMENT")

    def test_async_rejected(self):
        async def workflow():
            pass
        def build():
            scenario = factory()()
            scenario.run = workflow
            return scenario
        self.assertEqual(self.outcome(build)["result"], "INVALID_EXPERIMENT")

    def test_bad_repeat(self):
        for value in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                self.outcome(factory(), repeats=value)

    def test_confirmation_side_effect(self):
        def build():
            state = {"valid": True, "effect": False}
            def workflow():
                valid = state["valid"]
                checkpoint("authority_observed")
                if valid:
                    state["effect"] = True
            return Scenario("bad-revoke", workflow,
                            lambda: state.update(valid=False, effect=True),
                            lambda: not state["valid"], lambda: state["effect"])
        self.assertEqual(self.outcome(build)["result"], "INVALID_EXPERIMENT")

    def test_swallowed_injection_error(self):
        self.assertEqual(self.outcome(factory(precommit=True, swallow=True))["result"], "INVALID_EXPERIMENT")

    def test_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            report = self.outcome(factory(), json_path=path)
            self.assertEqual(json.loads(path.read_text()), report)

    def test_all_examples(self):
        for domain in ("refund", "delegation", "session"):
            for filename, expected in (("scenario.py", "REVOCATION_ESCAPE"), ("safe.py", "CLOSED")):
                with self.subTest(domain=domain, filename=filename):
                    build = runpy.run_path(str(ROOT / "examples" / domain / filename))["build_scenario"]
                    self.assertEqual(self.outcome(build, repeats=5)["result"], expected)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            for filename, code in (("scenario.py", 1), ("safe.py", 0)):
                path = Path(directory) / "result.json"
                process = subprocess.run([sys.executable, "-m", "authdrift", "run",
                    str(ROOT / "examples/refund" / filename), "--json", str(path)],
                    cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(process.returncode, code, process.stderr)
                self.assertEqual(json.loads(path.read_text())["schema_version"], "1.0")

    def test_hook_cleanup(self):
        self.outcome(factory(precommit=True))
        checkpoint("authority_observed")
        self.assertEqual(self.outcome(factory(safe=True))["result"], "CLOSED")


if __name__ == "__main__":
    unittest.main()
