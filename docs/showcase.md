# Walk through AuthDrift in three minutes

## The developer problem

A workflow remembers an earlier approval. If that approval is withdrawn before
the action, does the workflow still issue the refund? AuthDrift makes this
ordering reproducible, allowing developers to compare a vulnerable path with a
corrected one before relying on their authorization logic.

## Demo

1. Follow the README installation instructions. The package is `authdrift-harness`.
2. Run `python -m authdrift run examples/refund/scenario.py --repeats 20 --json vulnerable.json`.
   Exit 1 means the expected escape was detected.
3. Separately run `python -m authdrift run examples/refund/safe.py --repeats 20 --json safe.json`.
   Exit 0 means these controlled trials closed the tested boundary.
4. Open the JSON: compare the positive and negative controls, then find confirmed
   invalidation, absence of the effect at confirmation, and the final effect read.
5. Run `python benchmarks/showcase.py --output results/my-run` for all eight fixtures.
   This writes raw reports, a readable summary, environment details and source hashes.
   Use a new output directory for each run; existing evidence is not overwritten.

The [consumed-approval example](../examples/consumed_approval/README.md) also
exports its observed domain ledger, so the earlier consumption can be inspected.

## What to explain while demonstrating

- The initial permission check and the later effect are distinct steps.
- Revocation confirmation reads authority state independently of the mutation callback.
- A broken control invalidates an experiment; it cannot count as a passing security test.
- Corrected synchronous examples recheck permission. Concurrent services also need
  an atomic relationship between authorization and mutation; these examples do not prove it.

## Evidence and limits

All included fixtures use synthetic in-memory records. No payment is sent and no
model credential is needed. Twenty repetitions are not twenty vulnerabilities.
Read [claim evidence](resume-claims.md), [methodology](../research/methodology.md)
and [integration guidance](integrating-your-agent.md) for interpretation and scope.
Reports from real integrations can contain sensitive error text; the public demo
bundle should contain only these repository-owned synthetic fixtures.
