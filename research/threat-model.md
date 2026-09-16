# Threat model

The fault is stale authority between observation and consequential effect.
The experiment operator controls revocation and a cooperative workflow checkpoint.
The authoritative sink and revocation predicates are trusted. No model output
is accepted as evidence of a commit.

This v0.1 harness assumes fresh isolated state, persistent revocation, monotonic
sink existence, synchronous completion, and no concurrent independent writers.
Predicates must read authoritative state and return actual booleans. Callback
exceptions fail the experiment; scenario authors should represent expected
permission denial as normal completion without an effect.

Excluded: malicious instrumentation, transient regrant, hidden or erased effects,
unjoined background jobs, eventual-consistency observations, and hard termination
of hung Python callbacks. A successful local test does not prove distributed
revocation closure. Commit-time checks need atomicity in real systems.
