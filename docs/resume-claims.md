# Implementation and claim evidence

AuthDrift tests synchronous authority changes; it does not enforce authorization.
The following describes implemented behavior, not a broader product roadmap.

| Claim | Implementation | Verification | Scope |
| --- | --- | --- | --- |
| Pause a workflow after authority observation, invalidate permission, resume and inspect the effect | `authdrift/hooks/lifecycle.py`, `authdrift/core/runner.py` | `tests/test_runner.py`; refund demo | Cooperative checkpoint in synchronous Python |
| Independently confirm authority and effect state | Scenario predicates and runner controls | Positive, pre-revoked and mid-flight records in each JSON report | Supplied predicates must be truthful and the contract explicit |
| Reproduce 20/20 escapes and 20/20 closures | Refund, delegation and session vulnerable/corrected fixtures | `python benchmarks/showcase.py --output results/my-run` | Repeated synthetic fixture trials, not distinct external vulnerabilities |
| Structured reports and no runtime dependencies | `authdrift/cli/main.py`, `pyproject.toml` | Existing CLI tests; package metadata; published v0.1.0 | Python 3.10+; package name `authdrift-harness` |

## Suggested factual project bullets

- Built a Python authorization-testing harness that pauses a workflow after its permission check, revokes authority and verifies whether the resumed action still changes the effect state.
- Added positive, pre-revoked and mid-flight controls with independent authority and effect checks; reproduced stale-authorization escapes and corrected behavior across refund, delegation and session fixtures.
- Published a dependency-free Python package with CLI execution and JSON evidence, enabling repeatable investigation of synchronous authorization regressions.

Use the numerical fixture counts only with a retained, successful reproduction.
Do not claim customer adoption, production validation, framework compatibility,
async execution or discovered external vulnerabilities from these examples.
