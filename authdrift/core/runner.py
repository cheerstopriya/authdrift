import json
from pathlib import Path
from uuid import uuid4

from .events import Events
from .injector import InvalidExperiment, invoke, predicate, revoke_and_confirm
from .result import Outcome
from .scenario import Scenario
from ..hooks.lifecycle import _hook


def _experiment(source, mode):
    events = Events()
    evidence = {"run_id": str(uuid4()), "experiment": mode, "events": events.items}
    token = None
    reached = False
    injection_error = None
    try:
        scenario = source if isinstance(source, Scenario) else invoke(source)
        if not isinstance(scenario, Scenario):
            raise InvalidExperiment("factory must return Scenario")
        evidence["scenario"] = scenario.name
        if scenario.reset is not None:
            invoke(scenario.reset)
        if isinstance(source, Scenario) and scenario.reset is None:
            raise InvalidExperiment("a Scenario instance requires reset; alternatively pass a fresh factory")
        if predicate(scenario.committed) or predicate(scenario.revoked):
            raise InvalidExperiment("experiment must start with valid authority and an empty sink")
        events.add("experiment_ready")

        def hook(name):
            nonlocal reached, injection_error
            events.add("checkpoint", name=name)
            if name != scenario.trigger or reached:
                return
            reached = True
            if mode != "mid_flight":
                return
            try:
                if predicate(scenario.committed):
                    raise InvalidExperiment("effect already committed before injection")
                revoke_and_confirm(scenario, events)
                # A commit during revocation cannot be ordered after confirmation.
                if predicate(scenario.committed):
                    raise InvalidExperiment("effect present at confirmation; commit ordering is ambiguous")
                events.add("sink_absent_after_confirmation")
            except Exception as exc:
                injection_error = exc
                raise

        if mode == "negative":
            revoke_and_confirm(scenario, events)
            if predicate(scenario.committed):
                raise InvalidExperiment("revocation itself changed the sink")
        token = _hook.set(hook)
        invoke(scenario.run)
        events.add("workflow_completed")
        if injection_error is not None:
            raise injection_error
        if mode == "mid_flight" and not reached:
            raise InvalidExperiment("trigger checkpoint not reached")
        if mode != "positive" and not predicate(scenario.revoked):
            raise InvalidExperiment("authority was restored during the experiment")
        committed = predicate(scenario.committed)
        events.add("effect_observed" if committed else "effect_absent")
        evidence["committed"] = committed
        if mode == "positive":
            result = "PASS" if committed else Outcome.INVALID_EXPERIMENT.value
        elif mode == "negative":
            result = Outcome.BASELINE_FAILURE.value if committed else "PASS"
        else:
            result = (Outcome.REVOCATION_ESCAPE if committed else Outcome.CLOSED).value
        evidence["result"] = result
    except Exception as exc:
        evidence["result"] = Outcome.INVALID_EXPERIMENT.value
        evidence["reason"] = f"{type(exc).__name__}: {exc}"
        events.add("experiment_invalid", reason=evidence["reason"])
    finally:
        if token is not None:
            _hook.reset(token)
    return evidence


def run(scenario, *, repeats=1, json_path=None, quiet=False):
    """Run isolated positive, negative, and mid-flight experiments per repetition.

    Pass a fresh Scenario factory or a Scenario with a reset callback. Callbacks
    must terminate, and run() must wait for all effects to become observable.
    """
    if type(repeats) is not int or repeats < 1:
        raise ValueError("repeats must be a positive integer")
    if not isinstance(scenario, Scenario) and not callable(scenario):
        raise TypeError("expected Scenario or factory")
    if _hook.get() is not None:
        raise ValueError("nested experiments are unsupported")
    trials = []
    for index in range(repeats):
        experiments = []
        for mode in ("positive", "negative", "mid_flight"):
            result = _experiment(scenario, mode)
            experiments.append(result)
            if result["result"] != "PASS":
                break
        trials.append({"repetition": index + 1, "result": experiments[-1]["result"],
                       "experiments": experiments})
    escapes = sum(t["result"] == Outcome.REVOCATION_ESCAPE for t in trials)
    valid = sum(t["result"] in (Outcome.CLOSED, Outcome.REVOCATION_ESCAPE) for t in trials)
    priority = (Outcome.INVALID_EXPERIMENT, Outcome.BASELINE_FAILURE,
                Outcome.REVOCATION_ESCAPE, Outcome.CLOSED)
    overall = next(o.value for o in priority if any(t["result"] == o for t in trials))
    report = {"schema_version": "1.0", "result": overall, "repeats": repeats,
              "valid_trials": valid, "escapes": escapes,
              "escape_rate": escapes / valid if valid else None, "trials": trials}
    if json_path is not None:
        Path(json_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not quiet:
        for trial in trials:
            print(f"Trial {trial['repetition']}: {trial['result']}")
            for experiment in trial["experiments"]:
                print(f"  {experiment['experiment']}: {experiment['result']}")
                if "reason" in experiment:
                    print(f"    {experiment['reason']}")
        rate = f"{report['escape_rate']:.1%}" if valid else "unavailable"
        print(f"Escapes: {escapes}/{valid} valid trials ({rate}); total trials: {repeats}")
    return report
