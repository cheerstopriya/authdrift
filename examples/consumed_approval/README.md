# Consumed approval: a modeled domain transition

An approval has one remaining use. The workflow observes it; a legitimate
reservation consumes it; the later effect must not reuse the cached permission.
This example follows the question raised by Rob in
[discussion #5](https://github.com/cheerstopriya/authdrift/discussions/5#discussioncomment-18541806)
and [draft PR #6](https://github.com/cheerstopriya/authdrift/pull/6).
It is a separate follow-up implementation, not execution or approval of that PR.

## Contract and scope

- One approval permits one qualifying use. A completed reservation consumes it
  and invalidates outstanding effects; observation does not reserve a future use.
- The callback performs a modeled reservation and consumption synchronously.
  This demonstrates the transition, not fidelity to an external business workflow.
- `revoked()` reads remaining uses; `committed()` reads EFFECT-002 independently.
  Domain events are explanatory evidence and never authorization inputs.
- All state is **in memory**. There is no durable store, concurrent atomicity,
  external integration or production security claim.

## Controls

| Experiment | Reservation | Expected later effect |
| --- | --- | --- |
| Positive | Absent | Commits and consumes the one use |
| Pre-revoked | Before authority observation | Blocked in both variants |
| Mid-flight | After observation, at the checkpoint | Vulnerable commits; corrected blocks |

The vulnerable mid-flight path deliberately reuses stale permission. A corrected
concurrent implementation would also need atomic consume-and-mutate semantics;
the sequential recheck here is only sufficient for this fixture.

## Reproduce

From the checkout, run `python benchmarks/showcase.py --output results/consumed-demo`.
Alongside the harness reports it exports observed domain state and event history,
joined to each experiment's run ID and control mode in `*-domain-events.json`.
The join uses this runner's sequential fresh-factory calls and fails if the count
does not match. No new core report schema or automatic causal inference is claimed.

For CLI-only output run these separately (the vulnerable command exits 1):

```sh
python -m authdrift run examples/consumed_approval/scenario.py --repeats 20
python -m authdrift run examples/consumed_approval/safe.py --repeats 20
```

CLI execution alone does not export the fixture-side domain ledger; use the showcase.
