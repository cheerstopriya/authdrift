"""Synthetic single-use approval fixture, inspired by Rob's discussion #5.

This is a modeled domain transition, not an external application integration.
The sidecar evidence collector is separate from the harness report and policy.
"""
from authdrift import Scenario, checkpoint


def build_scenario(safe=False, evidence=None):
    state = {"remaining_uses": 1, "effects": [], "reservations": [], "events": []}
    if evidence is not None:
        evidence.append(state)

    def record(kind, **fields):
        state["events"].append({"seq": len(state["events"]) + 1,
                                "type": kind, **fields})

    record("approval_issued", approval_id="APR-001", remaining_uses=1)

    def available():
        return state["remaining_uses"] == 1

    def reserve():
        # A modeled legitimate competing use; no later EFFECT-002 is created here.
        if available():
            state["remaining_uses"] = 0
            state["reservations"].append("RES-001")
            record("approval_consumed", approval_id="APR-001", cause_id="RES-001")

    def revoked():
        return state["remaining_uses"] == 0

    def committed():
        return "EFFECT-002" in state["effects"]

    def workflow():
        observed = available()
        record("authority_observed", available=observed)
        checkpoint("authority_observed")
        permitted = available() if safe else observed
        record("later_effect_attempted", effect_id="EFFECT-002", permitted=permitted)
        if permitted:
            if available():
                state["remaining_uses"] = 0
                record("approval_consumed", approval_id="APR-001", cause_id="EFFECT-002")
            state["effects"].append("EFFECT-002")
            record("later_effect_committed", effect_id="EFFECT-002")
        else:
            record("later_effect_blocked", effect_id="EFFECT-002")

    return Scenario("consumed-approval-corrected" if safe else "consumed-approval-vulnerable",
                    workflow, reserve, revoked, committed)
