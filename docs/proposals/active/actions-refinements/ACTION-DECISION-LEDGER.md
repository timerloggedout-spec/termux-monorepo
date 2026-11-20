# GitHub-Native Action Decision Ledger — Issue #192

**Status:** B1, B2, B3, and B6 controls are implemented on the consolidated Issue #192 PR; B4 and B5 remain intentionally gated by their separate authority/use-case decisions.
**Execution model:** GitHub Actions is the primary event, compute, and orchestration plane. The BLU B160V is not an operator prerequisite or primary runner; it is only an optional downstream service-capacity target when a future workflow has a separately defined, authenticated service contract.

> **Decision rule:** A Marketplace action is not adopted because it is popular or convenient. It must have one owner workflow, a concrete repository problem, minimal permissions, a full immutable commit SHA, testable trigger behavior, and a rollback path. A transitive image or tool reference that the immutable outer action does not expose for direct pinning is allowed only through an explicit exception: a reviewed expected digest, a read-only preflight that fails closed before the privileged job, deterministic tests, and a PR-reviewed update protocol.

## Executive Decision Table

| ID | User-supplied candidate | Decision | GitHub-native rationale | Earliest batch |
|---|---|---|---|---|
| A-01 | `github-app-token` | **Replace / defer** | The supplied `tibdex` action is deprecated. Investigate only the official `actions/create-github-app-token` successor when same-repo `GITHUB_TOKEN` cannot meet an approved cross-repository or workflow-trigger requirement. | B4 |
| A-02 | `actions/cache` | **Reuse** | Official cache is already present. Audit key ownership and restore/save usage; do not create a parallel cache pattern. | B2 review only |
| A-03 | `actions/checkout` | **Reuse** | Official checkout already exists. Preserve least privilege and `persist-credentials: false` on read-only jobs. | B1/B2 standardization |
| A-04 | `git-commit-and-push` | **Exclude** | The supplied third-party example uses direct push and mutable references. Generated changes must use a controlled branch/PR design, never direct default-branch push. | Never as supplied |
| A-05 | `changed-files` | **Do not adopt now** | Feature-rich but overlaps with the preferred path filter and current scripts. Select exactly one mechanism. | Rejected in favor of A-11 candidate |
| A-06 | `create-pull-request` | **Design-required candidate** | Can create/update one stable PR branch and produces explicit outputs, but needs a bounded file allowlist, idempotency, provenance, event-loop design, and workflow permissions. | B4 |
| A-07 | `delete-artifact` | **Defer** | Retention policy and immutable artifact design must come first; deletion is only justified by measured storage pressure. | Post-B2 |
| A-08 | `dump-context` | **Exclude from production** | Broad context logging creates unnecessary data-exposure risk. Use a minimal, manually invoked, redacted diagnostic when needed. | Debug only |
| A-09 | `github-status` | **Defer** | A GitHub service outage should not normally turn repository CI into a failed result. Use incident awareness only for an explicit release/deployment decision. | Future release workflow |
| A-10 | `issue-ai-agent` | **Replace with GitHub Agentic Workflows pilot** | The direct Marketplace endpoint was not extractable. GitHub’s documented agentic-workflow framework provides explicit safe outputs, compilation, cost caps, and least-privilege controls. | B3 |
| A-11 | `paths-changes-filter` | **Adopt candidate** | `dorny/paths-filter` provides job/step filtering, needs only PR read on PR events, and documents safe handling of attacker-influenced filename outputs. | B1 |
| A-12 | `replace-tokens` | **Exclude** | There is no approved substitution use case, and environment-driven file replacement can materialize sensitive configuration unexpectedly. | Never |
| A-13 | `retry-action` | **Exclude initially** | Retrying arbitrary shell commands/actions can duplicate side effects and its supplied examples use mutable references. Add retries only at an explicitly idempotent transient API boundary. | Future exception |
| A-14 | `repository-dispatch` | **Design-required candidate** | Useful for asynchronous cross-repository/service events, but requires allowlisted event types, schema-bounded payloads, and scoped authentication. | B5 |
| A-15 | `set-action-secret` | **Exclude** | Autonomous secret creation/rotation is outside scope and violates the repository’s human-only secret boundary. | Never |
| A-16 | `workflow-dispatch` | **Native-first / defer** | Reusable workflows, `needs`, and `workflow_run` cover the main same-repository patterns without a polling wrapper. | Future exception |
| A-17 | `skip-duplicate-actions` | **Defer / native-first** | Existing workflow `concurrency` must be normalized and measured first. This action needs `actions: write` to cancel runs and can affect required-check behavior. | Post-B1 audit |
| A-18 | `wait-on-check` | **Exclude by default** | Use `needs` for same workflow and reusable workflows/`workflow_run` for normal chaining; API polling is a last-resort multi-workflow coordination pattern. | Future exception |
| A-19 | `upload-a-build-artifact` | **Reuse and standardize** | Official immutable artifacts already exist in the repository. Standardize named, non-secret outputs, retention, hidden-file exclusion, and digest recording. | B2 |
| A-20 | `download-a-build-artifact` | **Adopt candidate** | Official download action enables explicit producer/consumer evidence handoff with same-run scoped access and digest validation. | B2 |
| A-21 | `super-linter` | **Deferred pilot** | Broad containerized linting may duplicate gate scripts and create a large failure surface. Prefer a narrow workflow-security lint pilot first. | B6 |
| A-22 | GitHub artifact guidance | **Adopt as standard** | Official docs require dependent jobs to use `needs` and treat v4 artifacts as immutable; this is the policy for B2. | B2 |
| A-23 | `useful-actions_fork` | **Discovery source only** | Useful curated examples, but its historical action versions are not an adoption authority. | Research complete |
| A-24 | `SWE-agent_fork` | **Pattern source only** | Its workflows are conventional docs, link-check, pytest, cache, artifact, and coverage CI; no issue-to-PR workflow is a direct drop-in. | Research complete |
| A-25 | `mini-swe-agent_fork` | **Pattern source only** | Its workflows are conventional CI, linting, link checks, release, cache, and test automation; no wholesale agent runtime import is justified. | Research complete |

## Additional Opportunities Found

| ID | Source | Opportunity | Decision | Why it is more relevant than a generic Marketplace import |
|---|---|---|---|---|
| X-01 | `rhysd/actionlint` | Static GitHub Actions workflow validation | **Implemented B6 advisory** | A focused, deterministic advisory check complements `repo_gate`; its baseline and promotion conditions are documented. |
| X-02 | `actions/dependency-review-action` | Pull-request dependency and license policy review | **Implemented B6 advisory** | Official action with a narrow supply-chain purpose, read-only scope, and `warn-only` output. |
| X-03 | `ossf/scorecard-action` | Repository security posture review | **Implemented B6 advisory with controlled updateability** | Immutable outer action pin, preflight registry tag-to-digest assertion, and isolated Scorecard result-publication permissions. |
| X-04 | `github/codeql-action` | CodeQL security analysis | **Implemented B6 advisory** | Official security analysis for Python, JavaScript/TypeScript, and Actions sources with isolated SARIF publication. |
| X-05 | GitHub Agentic Workflows (`gh-aw`) | Declarative AI issue triage, CI investigation, reporting, or controlled PR outputs | **Implemented B3 pilot** | GitHub-native Markdown source, compiled lock workflow, safe output, cost caps, and deterministic contract tests. |
| X-06 | `actions/starter-workflows` | Official workflow templates and security examples | **Reference source** | Use as canonical template source, not as a bulk import catalog. |
| X-07 | `sdras/awesome-actions` and action-security catalog | Curated discovery | **Reference source** | Useful for discovery and comparison only; every candidate still requires the ledger gates above. |

## Autonomous Implementation Sequence

| Batch | Scope | Exact deliverable | Permissions / safety boundary | Acceptance tests |
|---|---|---|---|---|
| **B0** | AR-01 baseline repair | Separate PR resolving syntax-affecting conflict markers in `repo_gate.py`, `gemini-dispatch.yml`, and `gemini-review.yml`. | No new action; preserve reusable-workflow interfaces; do not opportunistically repair unrelated files. | `repo_gate`, Termux smoke, YAML/actionlint validation, and a GitHub PR check run. |
| **B1** | Deterministic workflow routing | One pinned `dorny/paths-filter` action plus a versioned filter map; optionally `actionlint` if it does not duplicate the gate. | `contents: read`, `pull-requests: read`; no filename output may be interpolated directly into shell. | Fixture PRs for docs-only, workflow-only, source/test, and malicious filename cases; required checks always report. |
| **B2** | Evidence artifact contract | Named upload/download artifact producer-consumer pair for a real CI report or test evidence output; retention policy and digest capture. | Same-run scoped access; no hidden files, tokens, browser data, session stores, or device data; explicit path allowlist. | Success/failure artifact paths, unique names, digest validation, retention assertion, and no artifact on excluded paths. |
| **B3** | Read-only agentic operations pilot | A GitHub Agentic Workflow that triages Issue/CI information or emits a daily repository report as a safe issue/comment. | Read-only repository tools initially; safe output limited to one issue/comment type; per-run AI credit cap; no code writes. | Compiled lock-file review, trigger fixtures, prompt-injection test corpus, cost ceiling, and output schema checks. |
| **B4** | Controlled issue-to-PR automation | One fixed-name bot branch with `create-pull-request` or a reviewed `gh-aw` safe-output path, limited to an approved generated artifact. | Explicit `contents: write`, `pull-requests: write`; restricted `add-paths`; branch ownership; duplicate/run-loop prevention; human review before merge. | No-change, update-existing-PR, duplicate-event, untrusted-issue-content, and workflow-file-change tests. |
| **B5** | Repository/service dispatch | Typed `repository_dispatch` envelope for a concrete external capacity/service use case. | Same-repo first; strict event allowlist; JSON schema and payload size limits; no secret payloads; cross-repo token only if separately approved. | Schema rejection, replay/duplicate handling, allowed/denied event tests, and audit trail. |
| **B6** | Security and quality advisory pilots | Implemented actionlint, dependency review, Scorecard, and CodeQL advisory controls; Super-Linter remains deferred. | Advisory/non-required first; no auto-fix or PR comments. CodeQL and Scorecard isolate `security-events: write`; Scorecard alone isolates `id-token: write` and guards its transitive container tag with a reviewed registry digest. | Baselines or first hosted run, false-positive review, runtime/cost measure, controlled-update test, and a decision to promote, update, or remove. |

## Integration Checklist

| Batch | Checklist status | Current evidence / retained boundary |
|---|---|---|
| B0 / AR-01 | **Complete** | Baseline workflow repair is included in PR #261. |
| B1 / AR-05 | **Complete** | Boolean-only path routing, immutable pin, fixtures, and policy workflow are present. |
| B2 / AR-03 | **Complete** | Same-run evidence artifact producer/consumer with digest validation and retention boundary is present. |
| B3 / X-05 | **Complete pilot** | Compiled read-only agentic report, caps, safe-output schema, injection corpus, and fixtures are present. |
| B4 / AR-04 | **Blocked by design** | Requires separately accepted writer authority, provenance, stable-branch, and hostile-input tests. |
| B5 / A-14 | **Deferred by design** | Requires a concrete approved external capacity/service case and typed dispatch envelope. |
| B6 / X-01–X-04 | **Complete advisory set** | Actionlint, dependency review, Scorecard, and CodeQL are implemented; all remain non-required. Scorecard uses the controlled-update protocol in [B6 Scorecard advisory](B6-SCORECARD-ADVISORY.md). |

## Agent Fork Compatibility Findings

The two research forks should inform patterns, not become runtime dependencies. Both have MIT licenses and recently updated forks, but their GitHub Actions surfaces are conventional CI rather than autonomous issue-to-PR systems.

| Fork | Reusable evidence | Non-transferable scope |
|---|---|---|
| `SWE-agent_fork` | Python test, docs build, markdown link validation, cache, artifact upload, and coverage workflows demonstrate ordinary hosted-runner CI composition. | Its issue-solving runtime, model configuration, and external agent behavior must not be imported into the monorepo’s workflow plane without a separate threat, cost, and data-flow design. |
| `mini-swe-agent_fork` | Narrow Python CI, linting, link checking, cache, testing, and release workflow examples support small workflow ownership and deterministic validation. | Its application agent runtime and release assumptions are not a generic GitHub-native orchestration layer. |

## GitHub-Native Capacity Boundary

GitHub-hosted runners, repository events, reusable workflows, artifacts, concurrency, and safe output controls own normal orchestration. The BLU B160V must only appear in a future design as a named service endpoint or optional downstream capacity consumer with an authenticated, idempotent contract. It is not a browser operator, a mandatory self-hosted runner, or a manual approval step.

## References

1. [GitHub App token Marketplace listing](https://github.com/marketplace/actions/github-app-token)
2. [actions/cache Marketplace listing](https://github.com/marketplace/actions/cache)
3. [actions/checkout Marketplace listing](https://github.com/marketplace/actions/checkout)
4. [Create Pull Request Marketplace listing](https://github.com/marketplace/actions/create-pull-request)
5. [dorny/paths-filter Marketplace listing](https://github.com/marketplace/actions/paths-changes-filter)
6. [GitHub artifact workflow guide](https://docs.github.com/en/actions/tutorials/store-and-share-data#passing-data-between-jobs-in-a-workflow)
7. [Super-Linter Marketplace listing](https://github.com/marketplace/actions/super-linter)
8. [GitHub Agentic Workflows guide](https://docs.github.com/en/copilot/how-tos/github-agentic-workflows/creating-github-agentic-workflows)
9. [GitHub Agentic Workflows documentation](https://github.github.com/gh-aw/)
10. [Official starter workflows](https://github.com/actions/starter-workflows)
11. [SWE-agent fork](https://github.com/timerloggedout-spec/SWE-agent_fork)
12. [mini-swe-agent fork](https://github.com/timerloggedout-spec/mini-swe-agent_fork)
13. [actionlint](https://github.com/rhysd/actionlint)
14. [Dependency Review Action](https://github.com/actions/dependency-review-action)
15. [OpenSSF Scorecard Action](https://github.com/ossf/scorecard-action)
16. [CodeQL Action](https://github.com/github/codeql-action)
