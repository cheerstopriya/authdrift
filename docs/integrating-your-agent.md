# Test a real agent workflow with AuthDrift

AuthDrift needs five pieces of information from your application. It does not
need to replace your agent, policy engine, or tool implementation.

| AuthDrift input | Connect it to |
| --- | --- |
| `run()` | The real workflow entry point that reaches the consequential tool path |
| `checkpoint()` | The deterministic point after authority is observed and before the effect |
| `revoke()` | The operation that makes authority invalid in the real source of truth |
| `revoked()` | An independent read proving that authority is now invalid |
| `committed()` | A read from the authoritative sink proving whether the effect happened |

## Decide whether v0.1 fits

Good fits for the current release:

- synchronous Python workflows;
- a tool call executed in the same process as the checkpoint;
- local databases, files, or test services with a reliable sink-state query;
- workflows that wait for all consequential work before returning.

Integrations that need additional coordination:

- async callbacks;
- jobs that leave the process through a broker or queue;
- worker processes that do not inherit the checkpoint hook;
- multiple writers to the same sink;
- distributed authorization and mutation services that require atomic semantics.

Do not hide these gaps with sleeps or canned tool responses. If the real workflow
cannot be synchronized without changing its behavior, document that as a blocked
integration.

## 1. State the authority contract

Write one sentence that makes the expected security behavior testable:

> Revoking the user's approval invalidates every outstanding, uncommitted refund.

Name the actor, resource, action, revocation operation, and the point after which
the effect must not commit. AuthDrift cannot infer this contract for you.

## 2. Choose the observation boundary

Place the checkpoint after the workflow has obtained the authority it might later
reuse and before the consequential effect:

```python
def run_real_workflow():
    observed_permission = permission_service.can_refund(user_id, ticket_id)
    authdrift.checkpoint("authority_observed")
    agent_or_workflow_continues(observed_permission)
```

Do not place the checkpoint after the mutation. Do not remove or weaken existing
authorization checks to manufacture an escape.

## 3. Connect the authority source and sink

```python
def revoke_real_authority():
    permission_service.revoke_refund(user_id, ticket_id)

def authority_is_really_revoked():
    return not permission_service.can_refund(user_id, ticket_id)

def durable_effect_exists():
    return refunds_database.has_refund(ticket_id)
```

`revoked()` must independently read current state. Do not return a cached value or
trust the return value of `revoke()`. `committed()` must read the durable effect,
not the model's narration or a planned tool call.

## 4. Create isolated state for every experiment

Pass a factory that creates fresh users, resources, authority, and sink state:

```python
import authdrift

def build_scenario():
    fixture = create_isolated_test_fixture()

    def run_workflow():
        fixture.run_agent_until_completion()

    return authdrift.Scenario(
        name="real-refund-revocation",
        run=run_workflow,
        revoke=fixture.revoke_authority,
        revoked=fixture.authority_is_revoked,
        committed=fixture.refund_exists,
        trigger="authority_observed",
    )

if __name__ == "__main__":
    authdrift.run(build_scenario)
```

The positive baseline must commit. The pre-revoked negative baseline must reject
the effect. AuthDrift runs the mid-flight experiment only after both controls make
the temporal result meaningful.

## 5. Run and inspect evidence

```sh
authdrift run path/to/scenario.py --repeats 20 --json authdrift-result.json
```

Interpret the result under your declared authority contract:

- `REVOCATION_ESCAPE`: the effect was absent after confirmed revocation and present after continuation;
- `CLOSED`: the confirmed revocation remained in force and no effect was observed;
- `BASELINE_FAILURE`: the pre-revoked workflow committed, so the temporal experiment is not meaningful;
- `INVALID_EXPERIMENT`: a control, predicate, checkpoint, or ordering requirement failed.

Reports may contain exception text or application data. Review and sanitize them
before sharing. Scenario files execute as trusted Python and are not sandboxed.

## Share an integration

Real integrations are more useful than another toy fixture. Open an
[integration report](https://github.com/cheerstopriya/authdrift/issues/new?template=integration-report.yml)
with the framework, authority contract, checkpoint, sink, outcome, and required
adapter. A blocked result is useful when it documents the exact incompatibility.
