# B1 — Workflow Surface Policy

**Status:** Implemented on `fix/ar01-automation-baseline`; pending GitHub pull-request publication and review.
**Ledger items:** AR-02, AR-05, AR-06
**Owner workflow:** `.github/workflows/workflow-surface-policy.yml`

The B1 control introduces one narrow, immutable `dorny/paths-filter` use for pull-request workflow-surface routing. It does not expose changed filenames to shell commands, comments, artifacts, or downstream workflow inputs. Its only cross-job values are four booleans: `automation`, `source`, `tests`, and `docs`.

> A path name can be attacker-influenced on a pull request. This workflow therefore treats action-produced file lists as unsafe data and consumes only fixed boolean filter outputs.

## Runtime Contract

| Property | Control |
|---|---|
| Trigger | Pull requests that touch a workflow, local action, policy helper/test, or Issue #192 program document. |
| Permissions | Workflow default is `permissions: {}`. The route job has `contents: read` and `pull-requests: read`; the verification job has `contents: read`. |
| Third-party supply chain | `dorny/paths-filter` is pinned to immutable commit `ceb8a2b8f2d89434be7ff52d3de7ec3738c5cc9d` (v4.0.3, MIT). |
| Duplicate-run behavior | A PR-number concurrency group cancels obsolete policy runs. |
| Verification | The final job runs with `if: always()` and always reports the fixed boolean routing summary. |
| Checkout | Immutable `actions/checkout` v5 SHA with `persist-credentials: false` and `fetch-depth: 1`. |

## Deterministic Fixture Coverage

`scripts/ci/workflow_surface_policy.py` supplies a standard-library model for the same category boundaries. Its tests prove documentation-only, automation, source/test, and mixed-change classifications, plus the rejection of absolute paths, traversal paths, and dot-prefixed escape attempts. The helper never returns a filename for interpolation and never invokes a shell.

## Promotion Boundary

B1 establishes routing evidence only. It does not automatically invoke a writer, artifact hand-off, retry wrapper, generic status integration, issue agent, or external service. Any future job that consumes the booleans must retain least-privilege permissions and use a fixed operation rather than interpolating a path into shell or API authority.

## References

[1]: [Issue #192 action decision ledger](ACTION-DECISION-LEDGER.md)
[2]: [dorny/paths-filter v4.0.3 release](https://github.com/dorny/paths-filter/releases/tag/v4.0.3)
[3]: [GitHub Actions security hardening guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
