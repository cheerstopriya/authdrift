# AuthDrift

**Can your AI agent still act after you revoke its authority?**

AuthDrift is a developer testing harness for injecting confirmed authority changes
into running agent trajectories and observing whether consequential effects still
commit. It reproduces the gap between an earlier approval and a later action.
It does not enforce policy or protect a running agent.

## A 30-second example

An approval is checked, then withdrawn while the workflow is paused. Does the
refund still happen?

```python
# Naive: reuse the earlier decision.
approved = approval.valid()
authdrift.checkpoint("authority_observed")
prepare_refund()
if approved:
    issue_refund()
```

```python
# Corrected for this synchronous fixture: consult current authority.
approved = approval.valid()
authdrift.checkpoint("authority_observed")
prepare_refund()
if approval.valid():
    issue_refund()
```

These illustrative snippets assume revocation invalidates outstanding effects.
The runnable fixtures below explicitly define that contract. In concurrent
systems the final check and mutation must be atomic with respect to revocation;
a separate recheck alone does not guarantee that.

## Installation

Python **3.10+**, **no runtime dependencies**. From a source checkout:

```sh
git clone https://github.com/cheerstopriya/authdrift.git
cd authdrift
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
authdrift --help
```

Version 0.1.0 is a release candidate, not a published PyPI release.
Source builds require setuptools >= 77, normally supplied by pip's isolated
build environment. Examples are included in the repository/source distribution.
The connected editable-install workflow passed on Windows and Ubuntu with Python
3.10, 3.12, and 3.13; see [GitHub validation](release/validation.md).

## Quick start

```sh
authdrift run examples/refund/scenario.py --repeats 20 --json vulnerable.json
authdrift run examples/refund/safe.py --repeats 20 --json safe.json
```

The controlled vulnerable fixture reports `REVOCATION_ESCAPE` (exit **1**);
the corrected fixture reports `CLOSED` (exit **0**).

In AuthDrift's deliberately vulnerable controlled fixtures, all 20/20 runs
produced `REVOCATION_ESCAPE`; the corresponding corrected fixtures produced
20/20 `CLOSED`. These counts are fixture runs, not vulnerabilities discovered in
independent agents. The scenario's declared authority contract gives the security
classification its meaning; AuthDrift cannot infer that contract.

Measured final summary lines for the refund commands:

```text
vulnerable: Escapes: 20/20 valid trials (100.0%); total trials: 20
corrected:  Escapes: 0/20 valid trials (0.0%); total trials: 20
```

Run all three families and the tests:

```sh
python benchmarks/run.py
python -m unittest discover -s tests -v
```

See [release validation](release/validation.md) for measured results and
exact commands. The fixtures use in-memory effect records, not real payments,
LLM calls, or durable external services.

## How AuthDrift works

```text
Workflow observes authority
          |
Checkpoint pauses continuation
          |
Request authority change -> independently confirm state
          |
Verify effect is still absent
          |
Resume the same workflow -> inspect authoritative sink state
```

Each repetition uses fresh state for positive, pre-revoked negative, and
mid-flight controls. Failed controls prevent that mid-flight trial from running.
Confirmation reads the supplied authority predicate, not the revocation callback's
return value or model narration.

## Outcomes

**Scenario contract required:** confirmed revocation must invalidate outstanding,
uncommitted effects. A policy/configuration change alone does not establish this.
The v0.1 API assumes this contract; it cannot discover or verify it automatically.
Do not use its security classifications for unspecified upstream semantics.

| Outcome | Meaning under the scenario contract | CLI exit |
| --- | --- | --- |
| `REVOCATION_ESCAPE` | Effect absent after confirmation, present after continuation | 1 |
| `CLOSED` | Authority remains revoked; no effect observed after completion, scoped to this trial | 0 |
| `BASELINE_FAILURE` | Pre-revoked control commits; temporal interpretation stops | 2 |
| `INVALID_EXPERIMENT` | Failed positive control, bad predicates, missing checkpoint, callback error, or ambiguous ordering | 3 |

JSON schema 1.0 contains controls, per-experiment IDs, ordered monotonic events,
reasons, counts, and escape rate over valid mid-flight trials only (null if none).
Mixed reports prioritize invalid experiments, baseline failures, escapes, then
closed outcomes. CLI errors also exit 3. JSON does not yet separate observation
from security interpretation; see [methodology](research/methodology.md).

## Included scenarios

| Family | Authority | Controlled effect | Implementations |
| --- | --- | --- | --- |
| Refund | Approval | Refund record | [vulnerable](examples/refund/scenario.py), [corrected](examples/refund/safe.py) |
| Delegation | Worker eligibility | Worker result | [vulnerable](examples/delegation/scenario.py), [corrected](examples/delegation/safe.py) |
| Session | Session authorization | Protected-action record | [vulnerable](examples/session/scenario.py), [corrected](examples/session/safe.py) |

Each directory documents its authority contract. Delegation is a synchronous
worker fixture, not a distributed-agent integration.

## Writing your own scenario

```python
import authdrift

def build_scenario():
    # Contract: revoked approval invalidates every outstanding refund.
    state = {"approved": True, "refunds": []}

    def workflow():
        approved = state["approved"]
        authdrift.checkpoint("authority_observed")
        if approved:
            state["refunds"].append("refund")

    return authdrift.Scenario(
        name="refund-revocation",
        run=workflow,
        revoke=lambda: state.update(approved=False),
        revoked=lambda: not state["approved"],
        committed=lambda: bool(state["refunds"]),
        trigger="authority_observed",
    )

if __name__ == "__main__":
    authdrift.run(build_scenario)
```

CLI files export `build_scenario()` or `scenario`. Prefer a factory creating
fresh authority and sink state for each experiment. A `Scenario` instance requires
`reset=` restoring authorization and clearing the sink. Callbacks are synchronous;
predicates return actual booleans. Optional `confirmation_timeout` and
`poll_interval` default to 1 second and 0.001 seconds.

## Methodology and validity

Place the checkpoint after authority observation and before any effect. With
truthful monotonic sink state, no independent writers, and synchronous continuation,
absence after confirmation followed by presence establishes causal ordering:
observation < confirmed revocation < commit. Exact commit time is not measured.
`effect_observed` is an observation timestamp; **Post-Revocation Commit Delay
(PRCD)** is not calculated from it.

The workflow must join all consequential work before returning. Revocation must
persist without regrant; effects must not be erased. Predicates independently
read actual authority and sink state without side effects. Factory isolation is
a caller obligation, not a sandbox. Read [methodology](research/methodology.md)
and [threat model](research/threat-model.md) before interpreting results.

## What AuthDrift does not do

No enforcement, automatic interception, framework adapters, universal compatibility,
async execution, or production validation. Threads/processes do not automatically
inherit the checkpoint hook. Confirmation polling has a timeout, but the harness
cannot safely preempt blocked callbacks. Scenario files execute Python: load only
trusted code. CLOSED is not proof of general revocation closure.

## External validation status

| Specimen | Execution status | Security outcome |
| --- | --- | --- |
| LangGraph airline | `BLOCKED_NOT_EXECUTED` | None |
| Goose | `BLOCKED_NOT_EXECUTED`; `SEMANTICS_UNSPECIFIED` | None |

These are validation-attempt provenance, not successful external validation or
AuthDrift failures. No LangGraph or Goose vulnerability is claimed. Details and
the failed Ollama memory preflight: [external validation](research/external-validation.md).

## Related research

The intended contribution is developer-facing testing, injection, and reproduction
tooling. AuthDrift does not claim to invent stale authority, TOCTOU, commit-time
authorization, or revocation closure. See [related work](research/related-work.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Independent specimens are welcome with
honest execution provenance and explicit authority contracts. For suspected
harness vulnerabilities, see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE). Retained upstream specimen material keeps its own license.

## Trusted code and report privacy

AuthDrift executes user-supplied Python scenarios. Running a scenario is
equivalent to executing trusted Python code. AuthDrift is not a sandbox.
Only execute scenarios you trust.

Exceptions and error messages may be included in generated result artifacts
and console output. Users should review and sanitize reports before sharing
or publishing them. AuthDrift does not automatically redact secrets or personal
data. Keep raw reports private by default.
