# delegation controlled fixture

scenario.py uses a cached authority decision; safe.py selects the same workflow
with a current-state recheck immediately before the in-memory effect.

Authority contract: revocation invalidates every outstanding uncommitted effect.
Authority remains invalid through completion. The list recording effects is the
authoritative, monotonic sink for this controlled simulation, not durable storage.
The checkpoint occurs after the workflow/coordinator observes authority.

Positive control must record an effect; pre-revoked negative control must not.
Mid-flight revocation should expose the cached-decision variant and block the
corrected variant. No LLM, real payment, network service, or framework is involved.
Check and mutation have no yield; real concurrent systems require atomicity.

Run from repository root:

    authdrift run examples/delegation/scenario.py --repeats 20
    authdrift run examples/delegation/safe.py --repeats 20

Expected exit codes are 1 and 0 respectively. Each experiment uses fresh state.
