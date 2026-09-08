# Extended Action Research Notes

> **Scope:** Research evidence for Issue #192. This file records action metadata and repository-fit observations; it does not authorize action adoption.

## Source Batch 1 — Core Authentication, Checkout, Cache, and Commit/Push

| Starter entry | Canonical source / current status | Key evidence | Provisional fit |
|---|---|---|---|
| GitHub App token | Marketplace listing for `tibdex/github-app-token` | The listing explicitly marks the action deprecated and directs users to `actions/create-github-app-token`. Its stated purpose is a scoped GitHub App identity when the workflow token is insufficient. | **Replace candidate:** investigate the official successor only for a demonstrated cross-repository or event-propagation requirement. |
| Cache | `actions/cache` Marketplace listing | Official, verified action. Current listings describe cache v5/v6 runtime requirements, cache restore/save variants, branch-scoped cache behavior, and read-only save behavior for fork pull requests. | **Reuse existing:** the monorepo already uses this family. Do not add a second cache owner; evaluate cache-key/retention hygiene in AR-02/AR-06. |
| Checkout | `actions/checkout` Marketplace listing | Official action; current listing documents `persist-credentials`, shallow-fetch defaults, least-privilege `contents: read`, and the security risk of checking out fork code in trusted `pull_request_target` / `workflow_run` contexts. | **Reuse existing:** standardize pinned references and preserve `persist-credentials: false` unless a named write operation requires otherwise. |
| Git commit and push | Marketplace listing for `github-actions-x/commit` | The supplied listing is an old third-party action that demonstrates direct push and outdated mutable references. It is not GitHub-certified. | **Exclude from initial batches:** any generated change must use a separately designed, idempotent branch/PR path; no direct default-branch push. |

### References

1. <https://github.com/marketplace/actions/github-app-token>
2. <https://github.com/marketplace/actions/cache>
3. <https://github.com/marketplace/actions/checkout>
4. <https://github.com/marketplace/actions/git-commit-and-push>

## Source Batch 2 — Change Detection, Pull Requests, Artifact Cleanup, and Context Dumps

| Starter entry | Canonical source / current status | Key evidence | Provisional fit |
|---|---|---|---|
| Changed files | `tj-actions/changed-files` Marketplace listing | Supports REST-API or Git-diff paths, monorepo patterns, merge queues, JSON/matrix outputs, and outputs to files. It requires carefully matched checkout depth for push events and has a large configuration surface. | **Design comparison required:** evaluate against current scripted prior-PR inventory and `dorny/paths-filter`; adopt only one filter owner. |
| Create pull request | `peter-evans/create-pull-request` Marketplace listing | Creates or updates a fixed branch/PR from workspace changes and provides PR outputs. It requires explicit repository permission to create PRs; a default workflow token cannot trigger follow-on `push` or `pull_request` runs; workflow-file changes may require workflow scope. | **High-value, design-required candidate:** potential answer to automated issue-to-PR flow, but only with restricted pathspec, fixed branch, idempotency, provenance, minimal contents/PR permissions, and separate workflow-event design. |
| Delete artifact | `geekyeggo/delete-artifact` Marketplace listing | Third-party cleanup action supports named/wildcard deletion and fail-on-error control; Marketplace displays an immutable SHA example. | **Defer:** hosted artifact retention is preferred first. Add only after an artifact lifecycle audit demonstrates material quota/storage pressure. |
| Dump context | `crazy-max/ghaction-dump-context` Marketplace listing | Composite diagnostic action prints workflow and runner context to logs. | **Exclude from autonomous production flow:** diagnostics can be implemented with a minimal local/redacted `github-script` or manual debug workflow; broad context logging requires a data-exposure review. |

### References

5. <https://github.com/marketplace/actions/changed-files>
6. <https://github.com/marketplace/actions/create-pull-request>
7. <https://github.com/marketplace/actions/delete-artifact>
8. <https://github.com/marketplace/actions/dump-context>

## Source Batch 3 — Status Awareness, Issue Agents, Path Filtering, and Token Replacement

| Starter entry | Canonical source / current status | Key evidence | Provisional fit |
|---|---|---|---|
| GitHub Status | `crazy-max/ghaction-github-status` Marketplace listing | An informational third-party action that can set failure thresholds for GitHub service incidents, including Actions, API, issues, and pull requests. | **Defer:** do not convert transient GitHub incidents into repository failures without a demonstrated outage-sensitive release workflow. |
| Issue AI agent | Supplied Marketplace URL | The Marketplace text endpoint returned no extractable listing. The existing repository workflows and the two agent forks will be the primary evidence sources instead of assuming an unverified template is safe. | **Research further; no adoption decision.** |
| Paths changes filter | `dorny/paths-filter` Marketplace listing | Job/step-level conditional filtering with PR REST API support, `pull-requests: read` requirement, filter outputs, and explicit warning that changed filename outputs are attacker-influenced and must not be directly interpolated into shell scripts. | **Preferred filter candidate:** compare directly against `tj-actions/changed-files`; adopt one pinned action with paths stored in a versioned filter file if the current dispatcher lacks this capability. |
| Replace tokens | `cschleiden/replace-tokens` Marketplace listing | Old third-party token-substitution action interpolates environment values into matched files. | **Exclude:** no established repository need and high risk of unintended secret/config materialization. |

### References

9. <https://github.com/marketplace/actions/github-status>
10. <https://github.com/marketplace/issue-ai-agent>
11. <https://github.com/marketplace/actions/paths-changes-filter>
12. <https://github.com/marketplace/actions/replace-tokens>

## Source Batch 4 — Retry, Dispatch, and Secret-Management Authority

| Starter entry | Canonical source / current status | Key evidence | Provisional fit |
|---|---|---|---|
| Retry action | `Wandalen/wretry.action` Marketplace listing | Can retry arbitrary actions or shell commands, but the supplied examples use mutable `@master`; its documentation warns that handling pre/main/post action stages can disrupt a workflow. | **Exclude from initial batches:** use explicit retry semantics only at known transient API boundaries; never wrap arbitrary privileged or non-idempotent steps. |
| Repository dispatch | `peter-evans/repository-dispatch` Marketplace listing | Same-repository dispatch can use the workflow token; cross-repository dispatch requires separately scoped credentials. Receiving workflows must reside on the default branch, and payload size/top-level field limits apply. | **Design-required:** potentially useful for GitHub-native asynchronous capacity/service signaling, but only with schema-validated, minimal payloads and an allowlisted event type. |
| Set Action Secret | `hmanzur/actions-set-secret` Marketplace listing | Writes repository or organization secrets using a repository-access token. | **Exclude:** violates the no autonomous secret-creation/rotation boundary. |
| Workflow dispatch | `benc-uk/workflow-dispatch` Marketplace listing | Triggers a named workflow; its own documentation points to reusable workflows as the native chaining model. Cross-repository triggering needs an external token, and waiting adds polling behavior. | **Prefer native reusable workflows:** use only for genuinely asynchronous/manual workflow interfaces after event semantics are proven. |

### References

13. <https://github.com/marketplace/actions/retry-action>
14. <https://github.com/marketplace/actions/repository-dispatch>
15. <https://github.com/marketplace/actions/set-action-secret>
16. <https://github.com/marketplace/actions/workflow-dispatch>

## Source Batch 5 — Duplicate-Run Control, Check Waiting, and Artifact Transfer

| Starter entry | Canonical source / current status | Key evidence | Provisional fit |
|---|---|---|---|
| Skip duplicate actions | `fkirc/skip-duplicate-actions` Marketplace listing | Offers duplicate detection, path-based skipping, and optional cancellation of outdated runs. It needs `actions: write` for cancellation and documents required-check pitfalls when jobs are skipped. | **Defer / native-first:** existing `concurrency` should be audited first. Adopt only if content-aware duplicate suppression delivers a measurable benefit without breaking required checks. |
| Wait on check | `lewagon/wait-on-check-action` Marketplace listing | Uses polling against the Checks API. Its own decision guidance favors `needs` for same-workflow sequencing and `workflow_run` for simple default-branch chaining; polling risks API limits. | **Exclude by default:** use native `needs`, reusable workflows, or `workflow_run`; revisit only for an explicit multi-workflow atomic-wait requirement. |
| Upload artifact | `actions/upload-artifact` Marketplace listing | Official verified action. Current versions provide immutable artifact behavior, SHA-256 output digest, explicit retention, hidden-file exclusion by default, and no multi-job mutation of the same artifact name. | **Reuse existing / expand conditionally:** establish a tight non-secret artifact contract, unique names, short retention, and explicit `if-no-files-found`; do not upload device/session state. |
| Download artifact | `actions/download-artifact` Marketplace listing | Official verified action. Supports named or ID-based immutable downloads, digest-mismatch handling, scoped same-run defaults, and token-gated cross-run/repo access. | **Small candidate addition:** use only with an accepted producer/consumer contract and ID/name allowlist. |

### References

17. <https://github.com/marketplace/actions/skip-duplicate-actions>
18. <https://github.com/marketplace/actions/wait-on-check>
19. <https://github.com/marketplace/actions/upload-a-build-artifact>
20. <https://github.com/marketplace/actions/download-a-build-artifact>

## Source Batch 6 — Linting and Official Artifact Contract

| Starter entry | Canonical source / current status | Key evidence | Provisional fit |
|---|---|---|---|
| Super-Linter | `super-linter/super-linter` Marketplace listing | Verified, broad containerized multi-language linter. It can require full history and additional status/comment permissions; it supports many overlapping tools and optional fix modes. | **Deferred pilot candidate:** scope must be limited to workflow/YAML/security linting first and compared with existing repository gates; no auto-fix or PR-comment permissions in the initial pilot. |
| Artifact workflow guide | Official GitHub Actions documentation | Defines upload/download artifacts for dependent jobs via `needs`, custom retention, v4 immutable artifact naming, and digest validation on download. | **Adopt as the artifact design standard:** use named, non-secret artifacts, explicit producers/consumers, short retention, and default digest validation. |

### References

21. <https://github.com/marketplace/actions/super-linter>
22. <https://docs.github.com/en/actions/tutorials/store-and-share-data#passing-data-between-jobs-in-a-workflow>

## Additional Discovery — GitHub Agentic Workflows

GitHub now documents **GitHub Agentic Workflows** as a public-preview, GitHub-native automation framework. Workflows are authored as Markdown with YAML frontmatter, compiled into `.lock.yml` GitHub Actions workflows, and can use Copilot, Claude, Codex, Gemini, or Pi engines. The framework distinguishes deterministic Actions work from agentic reasoning work and supports declared safe outputs, including issue, comment, and pull-request creation.

| Opportunity | Evidence | Provisional fit |
|---|---|---|
| Agentic issue triage | Markdown-authored workflow with read-scoped permissions, explicit `safe-outputs`, compiled lock file, and action triggers. | **High-priority research candidate:** a better-aligned alternative to an opaque marketplace issue-agent action, but it is public preview and requires a dedicated capability, cost, and safe-output review. |
| Agentic CI diagnosis | Framework examples include CI-failure investigation, report generation, and quality/testing automation; workflow-level AI credit budgets and audit logs are documented. | **Candidate after deterministic baseline repair:** use only to analyze/triage failures initially; do not permit code writes in the first pilot. |
| Safe issue/PR writes | The framework defaults to read access and routes configured writes through validated safe outputs with scoped permissions. | **Preferred design direction for eventual issue-to-PR automation:** validate version pinning, permission model, preview stability, engine authentication, and GitHub Actions cost before adoption. |

### References

23. <https://docs.github.com/en/copilot/how-tos/github-agentic-workflows/creating-github-agentic-workflows>
24. <https://github.github.com/gh-aw/>
