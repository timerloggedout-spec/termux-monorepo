# B6 — Advisory Dependency Vulnerability Review

**Status:** Implemented as a read-only, non-blocking vulnerability advisory.
**Ledger item:** X-02 / B6
**Workflow:** `.github/workflows/dependency-review-advisory.yml`

This workflow evaluates dependency vulnerability deltas only. Its license-analysis option is disabled. The job has `contents: read`, `warn-only: true`, and no PR-comment or repository-write path.

| Surface | Configuration |
|---|---|
| Action | GitHub `actions/dependency-review-action` v5.0.0, pinned to `a1d282b36b6f3519aa1f3fc636f609c47dddb294`. |
| Trigger | Pull-request changes to declared dependency manifests and lock files. |
| Permission | Workflow scope is empty; the job has `contents: read`; fork PRs are skipped. |
| Finding scope | Dependency vulnerabilities; `license-check: false`; high-severity threshold; `warn-only: true`. |
| Output | Native job output and step summary; PR comment summary disabled. |
| Rollback | Delete the workflow. It owns no state, cache, artifact, comment, label, issue, PR, dispatch, or secret. |

Licensing and legal-source observations live in the isolated [legal/licensing research silo](../../../../research/legal-licensing/README.md). That research produces source-attributed observations and uncertainty records; it supplies no legal opinion, automated verdict, production gate, or runtime authorization.

The production security surface retains vulnerability analysis, secret detection, code analysis, dependency integrity, and deterministic tests as engineering controls.

## Acceptance Evidence

The workflow contract test verifies immutable action pins, dependency-manifest-only triggers, same-repository PR filtering, read-only permissions, vulnerability-only configuration, `warn-only`, disabled comment summaries, and the absence of side-effecting output commands.

## References

- [Issue #192 action decision ledger](ACTION-DECISION-LEDGER.md)
- [Dependency Review Action repository](https://github.com/actions/dependency-review-action)
- [Dependency Review Action v5.0.0 revision](https://github.com/actions/dependency-review-action/commit/a1d282b36b6f3519aa1f3fc636f609c47dddb294)
- [Dependency Review Action v5 installation and configuration](https://github.com/actions/dependency-review-action/tree/v5.0.0)
