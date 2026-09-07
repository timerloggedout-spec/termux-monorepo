# Repository Development Performance Suite

**Implements:** THUB-007  
**Purpose:** Measure the development performance of `termux-monorepo` from validated GitHub and CI evidence.  
**Execution plane:** GitHub Actions and repository metadata.  
**Reference policy:** SWE-agent and mini-SWE-agent are pinned reference adapters in the suite; they are **not** the performance target.

> **Measurement rule:** The suite measures repository development outcomes—review latency, check outcomes, merge readiness, automation response, and rework—not an external benchmark score. A benchmark adapter may supply an additional comparable signal, but it cannot replace repository evidence.

## Suite Architecture

| Layer | Responsibility | Initial implementation |
|---|---|---|
| Subject | The repository change or pull request being evaluated. | Same-repository, non-fork pull requests and manual repository snapshots. |
| Evidence collector | Retrieves factual lifecycle, review, check, and automation markers. | `repository-development-evaluation.yml`, with read-only GitHub API permissions. |
| Adapter | Converts one evidence source into a normalized manifest. | `repository-pr-lifecycle` deterministic adapter; `mini-swe-reference` optional bounded reference adapter. |
| Contract | Validates schema, redaction, numerical relationships, and content integrity. | Python validators under `scripts/ci/`. |
| Evidence store | Holds only redacted manifests and short-lived immutable artifacts. | GitHub Actions artifacts; reviewed manifests may be committed under `results/`. |
| Decision layer | Interprets trends after enough real observations exist. | Advisory only; no automatic merge, issue mutation, device control, or credential action. |

## Normalized Development Signals

| Signal family | Initial metric | Evidence source | Interpretation boundary |
|---|---|---|---|
| Delivery size | Commit, file, addition, and deletion counts | Pull request API | A size descriptor, not a quality score. |
| Validation health | Completed checks grouped by success, failure, cancellation, and pending state | Checks API | Reflects the current head SHA only. |
| Review flow | Review and unresolved-thread counts | Pull request REST/GraphQL APIs | Does not expose review body text in the manifest. |
| Automation response | First marker timestamp and marker count for known automation comments | Pull request comments API | Counts only allowlisted, marker-bearing automation comments; no comment bodies are stored. |
| Lifecycle | Opened, last-updated, merged/closed timestamps and current state | Pull request API | Enables later duration computation; no performance claim from a single sample. |
| Reference comparison | Adapter-specific bounded result | Pinned SWE reference runner | Optional context only; never a substitute for repository development signals. |

## Adapter Contract

Every adapter must produce a redacted JSON manifest with a fixed schema version, a canonical SHA-256 digest, a stable adapter identifier, a source revision or evidence key, UTC timestamps, and bounded metrics. An adapter may add a documented metric only after a contract revision and tests are reviewed.

| Adapter class | Credential policy | Trigger policy | Output policy |
|---|---|---|---|
| `repository-pr-lifecycle` | No provider credential. GitHub token is read-only and scoped by workflow permissions. | Pull-request event or manual dispatch. | Redacted lifecycle/check/review/automation metrics. |
| `mini-swe-reference` | Human-managed provider secret only. | Manual dispatch only. | One-instance, redacted run manifest; no prompt, patch, trajectory, log, or prediction payload. |
| Future reference adapter | Explicitly documented before use. | Conservative by default. | Must pass the same digest/redaction/metric-bound checks. |

## Guardrails

The suite must not treat absent data as success, infer benchmark resolution from agent completion, publish raw prompts or patches, run scheduled model workloads, alter GitHub secrets, or take autonomous merge/device actions. The first repository adapter is deliberately read-only and deterministic; it can run frequently without provider inference cost.

## Extension Sequence

The next adapter after `repository-pr-lifecycle` should be a **scorer** that converts a compatible, separately approved prediction artifact into an explicit score. It must preserve reference pinning, result-digest validation, input provenance, bounded workload, and the existing redaction rules. Only after longitudinal observations exist should an advisory trend report be added.

## References

[1]: https://github.com/timerloggedout-spec/SWE-agent_fork "SWE-agent fork"
[2]: https://github.com/timerloggedout-spec/mini-swe-agent_fork "mini-SWE-agent fork"
