# B6 — Advisory Dependency Review

**Status:** Implemented on `fix/ar01-automation-baseline`; pending pull-request execution and review.
**Ledger item:** X-02 / B6
**Workflow:** `.github/workflows/dependency-review-advisory.yml`

This B6 control evaluates only dependency-manifest changes in the public repository. It is an advisory review: the action is configured with `warn-only: true`, the job has only `contents: read`, no comment path is enabled, and the workflow has no code-write, pull-request-write, issue-write, security-event-write, or identity-token permission.

| Candidate-review criterion | Result |
|---|---|
| Action | GitHub’s official `actions/dependency-review-action` v5.0.0, pinned to commit `a1d282b36b6f3519aa1f3fc636f609c47dddb294`. |
| License and maintenance | MIT-licensed, non-archived, and active as of the August 2026 review. |
| Repository eligibility | The target repository is public, which the action supports without a GitHub Advanced Security license. |
| Action runtime | The pinned version uses Node 24 and requires Actions Runner v2.327.1 or later; the hosted PR check is the compatibility evidence. |
| Trigger | Pull-request changes to declared dependency manifests and lock files only; no manual, issue, comment, push, workflow-run, or repository-dispatch trigger. |
| Permission boundary | Scope permissions are empty; the sole job has `contents: read`. Fork pull requests are skipped. |
| Findings policy | High-severity threshold, license and vulnerability checks enabled, `warn-only: true`, and `comment-summary-in-pr: never`. The only intended outputs are the action’s native check output and a step summary. |
| Rollback | Delete the workflow. It owns no state, cache, artifact, comment, label, issue, pull request, dispatch, or secret. |

> The action’s own manifest states that its summary-comment option requires `pull-requests: write`. This pilot selects `never` and does not grant that permission.

## Deferred B6 Candidates

The next two security candidates remain intentionally deferred. `ossf/scorecard-action` needs a separate decision on publishing SARIF and the associated `security-events: write` scope; its scorecard signal should not be introduced as a hidden write-capable side effect. `github/codeql-action` needs a separate language/build matrix and SARIF ownership decision across this repository’s Python, JavaScript/TypeScript, Rust, and auxiliary project trees. Neither control is required to make this narrow dependency-delta review useful.

## Acceptance Evidence

The workflow’s static contract test verifies immutable action pins, dependency-manifest-only triggers, same-repository PR filtering, read-only permissions, `warn-only` configuration, disabled comment summary, and absence of side-effecting output commands. The workflow itself is lint-clean under the checksum-verified actionlint v1.7.12 release binary. The first GitHub-hosted run will record runtime and baseline findings before any promotion decision.

## References

[1]: [Issue #192 action decision ledger](ACTION-DECISION-LEDGER.md)
[2]: [Dependency Review Action repository](https://github.com/actions/dependency-review-action)
[3]: [Dependency Review Action v5.0.0 revision](https://github.com/actions/dependency-review-action/commit/a1d282b36b6f3519aa1f3fc636f609c47dddb294)
[4]: [Dependency Review Action v5 installation and configuration](https://github.com/actions/dependency-review-action/tree/v5.0.0)
