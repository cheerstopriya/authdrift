# Methodology

For every repetition, allocate independent state and run positive, negative,
then mid-flight experiments. Failed controls exclude that repetition from the
escape-rate denominator. Retain each control and failure in JSON evidence.

The mid-flight checkpoint blocks workflow continuation while revocation is
requested and confirmed. Check sink absence after confirmation before returning
control to the workflow. If the sink already exists, ordering is ambiguous and
the experiment is invalid. Query the authoritative sink after the workflow has
joined all work. All callbacks must be synchronous and terminating.

Polling waits only for confirmation; it is not a sleep-based injection strategy.
Event sequence is explicit and elapsed times use a monotonic clock. Observation
time is not commit time. No PRCD is derived from a final boolean query. An actual
temporal sensitivity study would require injection sweeps and a probability curve.

## Required authority contract

The scenario author must establish that confirmed revocation invalidates every
outstanding uncommitted effect under test. This documented v0.1 precondition
cannot be inferred from a configuration update. JSON does not separate observation
and security interpretation. Do not apply its security labels to unspecified
revocation scope; those observations require separate descriptive reporting.

Place the checkpoint after authority observation. Under the synchronous,
monotonic-sink, no-independent-writer assumptions, absence after confirmation
followed by presence establishes causal ordering:
T_observe < T_revocation_confirmed < T_commit. Actual commit time is not captured;
clock readings can tie at clock resolution and event sequence records program
order. A false predicate, misplaced checkpoint, transient regrant, or hidden
writer cannot be reliably discovered by this harness.

Commit minus confirmed-revocation time is Post-Revocation Commit Delay (PRCD).
A final boolean observation cannot supply it. CLOSED describes no observed effect
in this trial, not a proven enforcement mechanism or universal closure.

Run vulnerable and safe fixtures under identical conditions. Synthetic fixtures
validate harness behavior, not real-world prevalence or general agent security.
Hypotheses about longer agent workflows, distributed boundaries, and mitigation
latency remain unproven. Benchmark JSON records measured outcomes only.
