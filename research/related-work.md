# Related work

Bibliographic metadata and abstracts checked against the linked primary pages on
16 September 2026. The arXiv entries are preprints, not claims of peer review.
AuthDrift's intended contribution is developer-facing injection, testing, and
reproduction tooling; it does not claim discovery of stale authority or TOCTOU.

- Igor Santos-Grueiro. **Temporary Authority, Permanent Effects: Commit-Time
  Authorization for LLM Agents.** arXiv:2607.10487v1, 11 July 2026.
  [Source](https://arxiv.org/abs/2607.10487v1). Studies commit-time authority and
  controlled invalidation; proposes CommitGuard enforcement. AuthDrift is a test
  harness, not that monitor, and its fixtures do not reproduce the paper's suite.
- Yuxiang Peng and Xiaodi Wu. **Stateful Governance for Concurrent Agentic
  Systems.** arXiv:2608.02764v2, 10 August 2026 (v1: 3 August).
  [Source](https://arxiv.org/abs/2608.02764v2). Defines policy-state serializability
  and presents MasuGate. AuthDrift does not implement its runtime coordination.
- Lifei Liu, Haoran Yu, and Xiaochong Jiang. **VERA: Authority-Preserving Edge
  Revocation for Federated AI-Agent Workflows.** arXiv:2608.30091v1,
  30 August 2026. [Source](https://arxiv.org/abs/2608.30091v1).
  Addresses federated edge revocation. The local delegation fixture does not
  implement or validate a federated revocation protocol.
- Chris Zheng and Geng Yang. **CONTINUITY: Security-Context Contracts for
  Composable LLM Agent Controls.** arXiv:2609.05269v1, 4 September 2026.
  [Source](https://arxiv.org/abs/2609.05269v1). Addresses preservation of security
  context across composed controls. AuthDrift tests a narrower authority-change
  fault family, not general control composition.
- Deonté Watts. **Revocation Closure for Agentic Authorization Systems.**
  draft-watts-oauth-agent-revocation-closure-00, 13 September 2026.
  [Primary record](https://datatracker.ietf.org/doc/draft-watts-oauth-agent-revocation-closure/00/).
  Individual Internet-Draft, work in progress, not an RFC or adopted standard.
  Covers authority-derived paths to effects; AuthDrift's CLOSED label is a scoped
  experimental outcome, not protocol compliance or a closure receipt.
- Tobin South, Samuele Marro, Thomas Hardjono, Robert Mahari, Cedric Deslandes
  Whitney, Alan Chan, and Alex Pentland. **Position: AI Agents Need Authenticated
  Delegation.** ICML 2025, PMLR 267:82211–82231.
  [Proceedings](https://proceedings.mlr.press/v267/south25a.html).
  Motivates authenticated and accountable delegation. AuthDrift introduces no
  delegation protocol.
