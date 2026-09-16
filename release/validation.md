# Public validation summary

AuthDrift v0.1.0 is a synchronous developer testing harness. Publication is on
hold pending review of the sanitized release candidate.

The development candidate passed 18 unit tests and controlled benchmarks:
20/20 REVOCATION_ESCAPE for each deliberately vulnerable refund, delegation
and session fixture; 20/20 CLOSED for each corrected counterpart. These are
fixture outcomes, not vulnerabilities discovered in independent agents.

Reproduce from a trusted checkout with Python 3.10+:

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python benchmarks/run.py
```

The benchmark generates local environment information and result evidence.
Do not commit its raw output; review and sanitize it before sharing.

Raw development transcripts, machine details and external specimen records
are retained privately. Final distribution hashes and renewed CI results must
be reviewed for the sanitized candidate before publication.
