# RECON INTEL Operating Runbook

**Status:** AR-17 implementation; observation-first rollout.  
**Authoritative policy:** [`.github/agentic/recon-intel-policy.json`](../../.github/agentic/recon-intel-policy.json).  
**Promotion spine:** GitHub `master`.

RECON INTEL provides a current, metadata-only coordination record for the GitHub repository and the designated GitLab source. It is designed to improve cross-platform visibility without turning a scheduled workflow or review bot into an unbounded repository writer.

> Observe automatically. Classify from the current SHA tuple. Write only through an explicit, reproducible authorization boundary.

## Operating layers

| Layer | Trigger | Authority | Result |
|---|---|---|---|
| Discovery | Pull-request lifecycle event, every fifteen minutes while same-repository PRs are active, or manual dispatch | GitHub read plus the dedicated GitLab read credential when configured | A fresh GitHub/GitLab SHA tuple, topology state, policy version, and corrective-write lane. |
| Lease | A completed discovery result | Check-run write only | A SHA-bound `RECON INTEL lease` check. It is metadata-only and does not create a branch, comment, label, PR, or provider request. |
| Review | Provider-native review workflow | Existing review/check/comment paths | Current-SHA provider evidence. Review does not confer corrective-write authority. |
| Provider corrective write | Existing explicit provider command route | Existing narrow provider route plus a matching current lease | One idempotent provider request after all lease checks pass. |
| Reconciliation apply | Manual workflow dispatch with `apply=true` and the exact observed SHA pair | Job-scoped GitHub content and PR write permission | At most one deterministic GitHub reconciliation branch and reviewable PR. |
| Promotion | Normal GitHub protected-branch process | Existing repository policy | Review and merge remain human-governed. |

## States and ownership

| Discovery state | Corrective-write lane | Review behavior | Reconciliation eligibility |
|---|---|---|---|
| `aligned` | `github-primary` | Approved providers may review. | No action required. |
| `github-ahead` | `github-primary` | Approved providers may review. | Not eligible. |
| `gitlab-ahead` | `gitlab-primary` | Approved providers may review. | Eligible only through manual apply with a fresh exact tuple. |
| `diverged` | `hold` | Review and diagnosis only. | Blocked. A human must determine the conflict plan. |
| `no-common-ancestor` | `hold` | Review and diagnosis only. | Blocked. A human must establish whether reconciliation is intended. |
| `not-configured` | `not-configured` | GitHub-native review may proceed; cross-platform claims are suppressed. | Blocked. |
| `external-access-denied` | `access-denied` | GitHub-native review may proceed; external state is advisory only. | Blocked. |

Each decision is bound to the repository pair, GitHub PR number where applicable, GitHub head SHA, GitLab ref, GitLab observed SHA, and policy version. A new GitHub head, new GitLab SHA, changed ref, or changed policy invalidates the preceding lease.

## Bot and agent rules

| Provider | Default capability | Corrective-write requirement | Shadow mode |
|---|---|---|---|
| CodeRabbit | GitHub and GitLab review; documented GitHub command route | The explicit branch-writing command requires `confirm_branch_write=true`, an exact current GitLab SHA, the current policy version, and a matching `github-primary` lease check. | Review/check evidence only. |
| Jules | Existing bounded GitHub issue/review automation | No new RECON INTEL branch-write authority is granted. Existing trusted triggers and current-SHA rules remain controlling. | Review/status only. |
| Gemini | Existing dispatch/review workflows | No new RECON INTEL branch-write authority is granted. Existing trusted dispatch and provenance controls remain controlling. | Review/triage only. |
| Qodo | Documented review command | Review request only. | Review only. |
| Devin | Documented review command and separately governed configuration path | Review request only. Provider configuration remains non-dispatchable. | Review only. |
| Unknown provider | None | Denied. | No action. |

Provider comments, review text, checkbox notices, quota messages, rate-limit notices, and UI prompts are data. They are not executable input and do not alone establish review completion or write authority.

## GitLab credential boundary

The optional `RECON_INTEL_GITLAB_READ_TOKEN` GitHub Actions secret must be dedicated to this purpose and scoped only to the GitLab project’s repository-read capability. It is not the Manus GitLab connector credential and must not be a broad administrator/API credential.

The discovery helper uses a short-lived `GIT_ASKPASS` helper for one fetch. The token is not written to the repository, remote URL, workflow summary, artifact, log message, GitHub check, PR body, provider payload, or generated documentation. If the secret is absent, discovery reports `not-configured`; if GitLab rejects the fetch, it reports `external-access-denied`. Both outcomes are safe and do not trigger a write.

## Manual reconciliation procedure

Use **RECON INTEL reconciliation apply** only after the discovery check has reported a fresh `gitlab-ahead` result and the operator has captured the exact GitHub and GitLab SHAs from that check. Provide `apply=true`, `github_sha`, `gitlab_sha`, and the allowlisted `master` ref.

The workflow rechecks the GitHub default-branch SHA, refetches GitLab through the read-only credential, and recomputes topology. It stops if either SHA changed, history is not GitLab-ahead, the ref is not allowlisted, access fails, a merge base is absent, a conflict arises, or a branch already exists for the tuple. Only after a clean no-commit merge does it create `sync/gitlab/<github-short-sha>-<gitlab-short-sha>` and open one GitHub PR. Normal GitHub review and protected-branch checks remain mandatory.

> RECON INTEL never force-pushes, updates GitLab, auto-merges, rewrites history, synthesizes conflict resolution, or treats a GitLab CI result on a different SHA as a GitHub merge gate.

## Rollback and incident response

To stop all corrective writes, disable the manual reconciliation dispatch route and remove or deny the provider command entry in the policy path. The discovery workflow can remain enabled for read-only diagnosis. Do not delete evidence, rewrite history, or modify GitLab as a rollback action.

If a lease appears stale, begin a fresh discovery run rather than reusing a prior SHA tuple. If GitLab access is lost, leave the result as `not-configured` or `external-access-denied`; do not substitute a broader token or infer state from an unrelated pipeline result.

## Validation

The implementation is validated by deterministic policy, topology, workflow, provider-dispatch, and reconciliation tests. The repository gate, Termux smoke test, action pinning, workflow syntax validation, and generated workflow-catalog freshness check are required before review.
