# Contributing

Use Python 3.10+ and `python -m pip install -e .` from a checkout.
Run `python -m unittest discover -s tests -v` and `python benchmarks/run.py`.
Tests use the standard library; no extra test dependencies are required.

Keep changes small; include regression tests for correctness changes. Scenarios
must specify the authority contract, independent confirmation, sink, checkpoint
ordering, isolation, and positive/negative/mid-flight controls. Distinguish
harness-supplied authority from upstream authorization semantics.

Independent specimens must pin source and preserve its license and behavior.
Record actual prerequisites and outcomes. Never commit credentials or real user
data. Review deliberately retained release evidence before adding it.

Real integration reports are welcome even when the experiment is blocked. Use the
integration issue template and include the framework/runtime, authority contract,
checkpoint, revocation confirmation, authoritative sink, result, and the smallest
adapter required. Do not alter upstream authorization semantics to force an escape.

Read the [trusted-code and report-privacy boundaries](SECURITY.md#trusted-code-and-report-privacy).
Keep raw validation and external-specimen evidence private.
