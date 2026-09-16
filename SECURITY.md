# Security reporting

AuthDrift executes trusted scenario Python; it is not a sandbox or enforcement
system. An intentionally vulnerable fixture is not a harness vulnerability.

GitHub Private Vulnerability Reporting is enabled for
[cheerstopriya/authdrift](https://github.com/cheerstopriya/authdrift).
Use [Report a vulnerability](https://github.com/cheerstopriya/authdrift/security/advisories/new)
to privately submit a suspected harness vulnerability. Include the version,
impact, minimal reproduction, and sanitized evidence. Do not include credentials
or open a public issue containing an unpatched exploit. No response-time or
security-support guarantee is offered.

## Trusted code and report privacy

AuthDrift executes user-supplied Python scenarios. Running a scenario is
equivalent to executing trusted Python code. AuthDrift is not a sandbox.
Only execute scenarios you trust.

Exceptions and error messages may be included in generated result artifacts
and console output. Users should review and sanitize reports before sharing
or publishing them. AuthDrift does not automatically redact secrets or personal
data. Keep raw reports private by default.
