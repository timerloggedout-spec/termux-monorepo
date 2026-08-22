# Repository Development Performance Suite

**Implements:** THUB-007
**Purpose:** Measure `termux-monorepo` development performance from validated GitHub and CI evidence.
**Execution plane:** GitHub Actions and repository metadata.
**Reference policy:** SWE-agent and mini-SWE-agent are optional pinned reference adapters. They are not the performance target and they cannot displace repository-local evidence.

> **Measurement rule:** Development performance means high-quality, efficiently delivered, coordinated work: validation health, substantive review resolution, duplicate avoidance, safe-feedback time, asynchronous orchestration completion, and bounded resource cost. A public benchmark or leaderboard is a prior only; it cannot substitute for repository outcomes.

## Suite Architecture

| Layer | Responsibility | THUB-007 implementation | Safety boundary |
|---|---|---|---|
| Subject | Repository change or pull request under evaluation. | Same-repository non-fork PRs and explicitly requested snapshots. | Fork PRs are excluded from the read-only adapter. |
| Evidence collector | Collect factual lifecycle, review, check, and trusted automation markers. | `repository-development-evaluation.yml`. | Read-only GitHub permissions; comment bodies are not retained. |
| Contract | Canonicalize, redact, validate, and digest evidence. | Python validators under `scripts/ci/`. | Fixed schema; credential-shaped values and invalid ordering fail closed. |
| Evidence store | Retain only short-lived redacted manifests and summaries. | GitHub Actions artifacts or reviewed result manifests. | No prompts, patches, trajectories, prediction payloads, or credentials. |
| Optional reference adapter | Provide a bounded external comparison only when explicitly enabled. | `swe-reference-evaluation.yml`, one `0:1` instance. | Manual input **and** trusted enablement are required; provider credentials exist only during the benchmark process, never checkout, clone, or package installation. |
| Decision layer | Interpret longitudinal patterns for future routing. | Advisory evidence for AR-18. | No automatic merge, issue mutation, device control, secret action, or provider-write authority. |

## Normalized Development Signals

| Signal family | Initial metric | Evidence source | Interpretation boundary |
|---|---|---|---|
| Delivery size | Commit, file, addition, and deletion counts | Pull request API | Descriptive context, not a quality score. |
| Validation health | Current-head checks grouped by success, failure, cancellation, and pending state | Checks API | Distinct providers publishing the same check name are not conflated. |
| Review resolution | Review count and resolved/unresolved review-thread counts | Pull request REST/GraphQL APIs | Review bodies remain unpersisted data. |
| Duplicate avoidance | Duplicate trusted automation-marker fingerprints | Trusted issue-comment metadata | Markers count only when the author is allowlisted; the metric is not a correctness verdict. |
| Safe feedback | First trusted automation response after PR opening | Trusted issue-comment metadata | Time is evidence for later aggregation, not a per-PR performance claim. |
| Coordination | Lifecycle state and timestamp ordering | Pull request API | Closed and merged states must be chronologically credible before a manifest is accepted. |
| Optional reference comparison | Adapter-specific one-instance result manifest | Pinned SWE reference runner | Context only; never a replacement for repository outcomes. |

## Evidence Contract

Every adapter emits a redacted JSON manifest with a fixed schema version, canonical SHA-256 digest, stable adapter identifier, source revision or evidence key, UTC timestamps, and bounded metrics. The repository adapter rejects unknown fields, credential-shaped values, impossible timestamp sequences, empty check evidence, and invalid direct outcome counts. A successful `0:1` SWE reference manifest requires exactly one prediction record; it does not assert benchmark resolution.

| Adapter | Credential policy | Trigger policy | Output policy |
|---|---|---|---|
| `repository-pr-lifecycle` | Read-only GitHub token only. | Same-repository PR lifecycle or manual dispatch. | Redacted lifecycle, checks, reviews, and trusted automation metrics. |
| `mini-swe-reference` | Provider secret only at the one bounded benchmark process. | Manual dispatch with `run_external_reference=true` and trusted repository enablement. | One redacted manifest; no prompt, patch, trajectory, log, or prediction payload. |
| Future reference adapter | Explicitly documented and tested before use. | Conservative by default. | Must pass the same digest, redaction, provenance, and metric-bound checks. |

## Guardrails and Relationship to AR-18

The suite must not treat absent data as success, infer benchmark resolution from agent completion, publish raw review content, run scheduled model workloads, alter GitHub secrets, or take autonomous merge/device actions. The first adapter is deterministic and inexpensive to run. Its longitudinal repository-local outcomes are the eligible evidence source for AR-18’s specialist-routing evaluation; external leaderboard and benchmark material remains a lower-weight prior.

The canonical context index is currently bounded and stale (`master-staging`, history page 1, with parser failures). THUB-007 records this limitation and adds the `development-performance` scope, but does not edit generated graph artifacts. A trusted publisher or manual bounded reconciler must refresh the index before it is used for current lineage assertions.

## References

[1]: https://github.com/timerloggedout-spec/SWE-agent_fork "SWE-agent fork"
[2]: https://github.com/timerloggedout-spec/mini-swe-agent_fork "mini-SWE-agent fork"
