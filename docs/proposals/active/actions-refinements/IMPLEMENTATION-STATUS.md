# Implementation Status — Issue #192 Action Refinements

**Program status:** AR-01 through AR-07 are implemented or explicitly bounded on `fix/ar01-automation-baseline`, with B1 deterministic routing, B2 same-run evidence artifacts, B3 read-only agentic reporting, and B6 advisory actionlint added to PR #261. B4 remains blocked pending separate writer-authority acceptance; B5 remains deferred because no concrete external capacity/service use case exists.

> **Sequencing rule:** The repository must land AR-01’s baseline repair before any runtime workflow change from this program. No workflow in this document gains write, secret-management, or issue-derived execution authority merely because an item is specified.

## Program Matrix

| Item | Current result | Runtime change now? | Promotion condition |
|---|---|---:|---|
| AR-01 — baseline repair | Implemented and locally validated on `fix/ar01-automation-baseline`. | Yes, in PR #261. | Required checks and merge into `master-staging`. |
| AR-02 — ownership inventory | Completed in this record. | No additional runtime owner. | Review the owner and pinning findings before any wider normalization change. |
| AR-03 — artifact hand-off | B2 provides an allowlisted same-run producer/consumer test-evidence artifact with a SHA-256 manifest. | Yes, in PR #261. | Required checks and review of the seven-day retention boundary. |
| AR-04 — issue-to-PR path | Threat model and minimum design are complete. | No. | Separate acceptance of event provenance, branch ownership, write permissions, and test fixtures. |
| AR-05 — changed-file filter | B1 adopts one immutable `dorny/paths-filter` owner that emits booleans only. | Yes, in PR #261. | Required checks and review of fixture coverage. |
| AR-06 — native execution controls | B1/B2 preserve native concurrency, markers, checks, summaries, and dispatch owners. | Yes, bounded additions only. | Demonstrated owner and test case for any future primitive. |
| AR-07 — non-adoption controls | Explicitly recorded below. | No. | Separate threat model and approved minimal-permission design per privileged capability. |

## AR-02 — First-Party Ownership Inventory

| Capability | Current owner / use | Current integrity and retention behavior | Decision |
|---|---|---|---|
| Checkout | Multiple CI, gate, integrity, and agent workflows. | Both immutable checkout pins and legacy mutable `@v4` references exist. Most narrow workflows use `fetch-depth: 1` and disable submodules. | **No duplicate checkout abstraction.** Record the mutable tags as a later pin-normalization finding, not as an AR-01 side effect. |
| Cache | `model-router` owns daily soft-budget counters; `agent-context-store` owns bounded non-secret agent context; `deepseek-ci` owns its exact-ref session cache. | Model-router uses immutable restore/save pins; context-store currently uses a mutable cache major tag; DeepSeek uses an immutable cache pin. | **No new cache layer.** Future pin normalization must preserve key scope and context-store redaction rules. |
| Artifact upload | `deepseek-ci.yml` produces `deepseek_output.json`. | Artifact name is `deepseek-output`; upload is pinned; missing output is ignored; no download consumer is currently present. | **No generic artifact producer.** A consumer appears only under AR-03’s explicit hand-off contract. |
| Artifact download | No direct workflow use was found. | No current retained artifact crosses a declared `needs` boundary. | **Defer.** Do not add a download action merely because upload exists. |
| GitHub API scripting | Dispatcher, peer-review, review, quota, and proposal workflows own event handling and idempotent comment markers. | Most active uses pin `actions/github-script` to an immutable v7 SHA; a few legacy mutable tags remain in unrelated workflows. | **Reuse existing native API patterns.** Do not add status, wait, dispatch, or duplicate-run wrappers without a demonstrated gap. |
| Agent context store | Local composite action owns non-secret context cache and optional marker bookmarks. | Explicitly strips token, cookie, secret, password, and PoW-shaped fields; 32 KB cap; runner-temp auth state stays ephemeral. | **Reuse, do not fork.** Comment bookmarks remain optional and require the caller’s existing permission. |
| Model router | Local composite action owns per-day, branch-best-effort free-tier model routing counters. | Immutable cache restore/save pins; run-specific save key; no broad cross-branch restore. | **Reuse, do not duplicate.** It is not an artifact or general-purpose state system. |

## AR-03 — Bounded Artifact Hand-Off Contract

B2 implements the required producer/consumer relationship for a real, deterministic policy-test evidence report. The contract and tests are documented in [B2 workflow-surface evidence](B2-WORKFLOW-SURFACE-EVIDENCE.md).

| Contract element | Required control |
|---|---|
| Producer | One named report or evidence file from an allowlisted workspace path; producer job declares an immutable artifact name containing the run identity. |
| Consumer | Explicit `needs: producer`; named first-party download limited to the producer artifact. |
| Content | Deterministic, non-secret report or test evidence only. Browser profiles, session data, tokens, context caches, raw prompts, and device data are prohibited. |
| Integrity | Producer records a SHA-256 digest in the job summary or manifest; consumer verifies the digest before use. |
| Retention | A documented finite retention period and `include-hidden-files: false`; failure behavior must be explicit. |
| Validation | Tests cover missing report, unexpected path, digest mismatch, duplicate artifact name, and excluded sensitive path. |

The existing `deepseek_output.json` producer is not automatically enrolled because it has no declared dependent consumer or matching integrity contract.

## AR-04 — Controlled Issue-to-PR Design

CodeRabbit’s workflow-file limitation does not justify a broad write token or a direct issue-body-to-shell bridge. The smallest acceptable future path is a **single-purpose generated-artifact PR** with a fixed branch owner and a human merge gate.

| Design surface | Required boundary |
|---|---|
| Trigger | Same-repository, allowlisted event only. A label or approved comment command must be resolved server-side; fork and untrusted issue events are rejected. |
| Input | Event payload is treated as untrusted data. It may select a fixed generator mode but never becomes a shell command, workflow expression, path, or free-form commit message. |
| Output | One fixed generated artifact under an approved allowlist. Workflow files, action metadata, proposal registry state, secrets, and arbitrary source paths are excluded. |
| Branch | One bot-owned branch name. Existing PR is updated idempotently; duplicate event delivery must not create a second PR. |
| Permission | `contents: write` and `pull-requests: write` only in the isolated writer job, not at workflow scope. A GitHub App is considered only if repository `GITHUB_TOKEN` event semantics are proven insufficient. |
| Review | The generated PR is never auto-merged. Required checks and human review remain the merge gate. |
| Test matrix | No change; repeat event; existing generated PR; fork event; untrusted issue content; invalid path; workflow-file attempt; permission denial; and stale branch. |

This design is **not implementation authorization**. It requires a separate accepted item and a dedicated threat-model review.

## AR-05 — Changed-File and Path Filtering Decision

B1 adds one narrow `dorny/paths-filter` owner in `workflow-surface-policy.yml`, pinned to an immutable v4.0.3 commit. It emits boolean route signals only and never interpolates changed filenames into shell. The deterministic classifier and fixture suite cover documentation-only, automation, source/test, mixed, traversal, and path-normalization cases. The control is documented in [B1 workflow-surface policy](B1-WORKFLOW-SURFACE-POLICY.md).

## AR-06 — Native Execution-Control Decision

| Candidate concern | Existing mechanism | Decision |
|---|---|---|
| Duplicate-run suppression | Workflow concurrency groups, `cancel-in-progress`, per-SHA markers, and explicit throttles. | Retain native controls; do not add a skip-duplicate wrapper. |
| Retry | Targeted `curl --retry` in the local HTTP invocation action, with explicit timeout bounds. | Retain targeted retry; do not wrap every step in a generic retry action. |
| Check waiting | Peer-review orchestrator polls the specific expected review/check evidence with a bounded timeout. | Retain purpose-built wait logic; no generic wait-on-check action. |
| Status reporting | Checks, step summaries, and idempotent marker comments. | No separate github-status wrapper. |
| Dispatch | Existing `workflow_dispatch` use and GitHub Script event handling. No `repository_dispatch` consumer exists. | No dispatch wrapper or repository dispatch endpoint until AR-05/AR-04 evidence requires it. |
| Cache maintenance | Local owners have scoped keys and read/write behavior. | No delete-artifact or cache-maintenance action without retention-pressure evidence. |

## AR-07 — Explicit Non-Adoption and Security Controls

| Candidate | Decision | Required before reconsideration |
|---|---|---|
| `set-action-secret` | **Not adopted.** | Operator-only credential-management procedure, non-git secret source, audit trail, and explicit repository-setting review. |
| `replace-tokens` | **Not adopted.** | A fixed, non-secret templating contract with path allowlist and tests proving no credential or workflow mutation. |
| `git-commit-and-push` | **Not adopted.** | A separate generated-artifact branch ownership design; current AR-04 conditions still apply. |
| `create-pull-request` | **Deferred.** | AR-04 acceptance, narrow writer job, fixed branch/path controls, idempotency, and human merge review. |
| `github-app-token` | **Deferred.** | A demonstrated same-repository `GITHUB_TOKEN` insufficiency and an approved App permission minimization review. |
| `issue-ai-agent` | **Not adopted.** | Prompt-injection threat model, tool allowlist, credit cap, redacted output contract, and read-only pilot review. |
| Direct issue/comment-to-shell | **Prohibited.** | No current exception path. Event text remains data and cannot become a command. |

## B3 — Read-Only Agentic Operations Pilot

B3 is a scheduled/manual, metadata-only operations report with read-only agent permissions, a 40-AI-Credit per-run ceiling, an 80-credit daily ceiling, four turns, an explicit prompt-injection corpus, and a single isolated `create_issue` safe-output type. The generated lock workflow is reviewed alongside the Markdown source. See [B3 agentic operations pilot](B3-AGENTIC-OPERATIONS-PILOT.md).

## B6 — Advisory Workflow Lint

B6 adds two advisory, non-blocking controls: actionlint for changed automation surfaces and dependency review for declared dependency deltas. Both have `contents: read` only, immutable action/source pins, no auto-fix, and no pull-request comments. Their baseline and promotion decisions are recorded in [B6 actionlint advisory](B6-ACTIONLINT-ADVISORY.md) and [B6 dependency-review advisory](B6-DEPENDENCY-REVIEW-ADVISORY.md).

## References

[1]: [GitHub Actions artifact guidance](https://docs.github.com/en/actions/tutorials/store-and-share-data#passing-data-between-jobs-in-a-workflow)
[2]: [Issue #192 decision ledger](ACTION-DECISION-LEDGER.md)
[3]: [Issue #192 source evidence](source.md)
