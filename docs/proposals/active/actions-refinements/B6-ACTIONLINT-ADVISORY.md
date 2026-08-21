# B6 — Advisory GitHub Actions Lint Pilot

**Status:** Implemented, current baseline rechecked on 2026-08-21; retained as an advisory control.
**Ledger item:** X-01 / B6
**Workflow:** `.github/workflows/actionlint-advisory.yml`

The B6 pilot performs a narrow GitHub Actions syntax, expression, and ShellCheck review for changed workflow surfaces. It remains advisory: it has no auto-fix step, no pull-request comment path, no dispatch path, and no write permission. Branch protection must not promote it to required status until every residual finding below has a documented resolution or an accepted compatibility decision.

## Candidate Review

| Criterion | Review result |
|---|---|
| Tool | `rhysd/actionlint` v1.7.12 at immutable commit `914e7df21a07ef503a81201c76d2b11c789d3fca`. |
| License | MIT. |
| Maintenance signal | The repository was not archived and had GitHub activity in July–August 2026 when reviewed. |
| Invocation | The workflow fetches and verifies the exact source revision, then builds `./cmd/actionlint`. It uses neither a mutable action tag nor `curl | bash`. |
| First-party dependencies | `actions/checkout` v5 and `actions/setup-go` v5 use immutable 40-character commit SHAs. Checkout disables persisted credentials. |
| Permissions | Workflow scope is `permissions: {}`; the sole job receives `contents: read`. |
| Trigger | Pull requests affecting `.github/workflows/**`, `.github/actions/**`, or an actionlint configuration file, plus controlled manual dispatch. |
| Rollback | Delete `actionlint-advisory.yml`. It owns no state, artifacts, secrets, labels, comments, or external dispatches. |

## Current Baseline and Disposition

The first hosted baseline recorded 26 findings across eight files. That historical count predates subsequent AR-14, AR-15, and workflow reliability remediation, so it is not a current promotion metric. After the safe baseline fixes merged in PR #298, the remaining advisory signal was six findings: two generated-lock `queue: max` compatibility diagnostics and four findings in held PR #276 workflow code. The B3 remediation adds the officially documented `copilot-requests: write` permission, which actionlint v1.7.12—the latest release at review time—does not yet recognize; upstream issue #686 remains open. The repository therefore uses one path- and message-specific compatibility filter for that exact generated B3 lock diagnostic. Its lint subprocess returns nonzero only when unsuppressed findings exist; this is a normal advisory outcome, not an infrastructure failure. The workflow records `clean`, `findings`, or `not-run` explicitly so the job summary retains that distinction.

| Affected file | Current findings | Disposition |
|---|---:|---|
| `agent-review-auto-jules.yml` | 4 × SC2086 | Fix in this batch by quoting GitHub output writes; no trigger, permission, provider gate, or relay behavior changes. |
| `context-relationship-backfill.yml` | 1 × SC2016 | Fix in this batch by preserving the Markdown backticks through an escaped double-quoted summary string. |
| `proposal-lifecycle.yml` | 1 × SC2129 | Fix in this batch by grouping existing summary writes behind one redirection; proposal lifecycle behavior is unchanged. |
| `publish-wiki.yml` | 1 YAML parse error | Fix in this batch by quoting the dry-run command as a YAML scalar; writer authority and wiki publishing behavior are unchanged. |
| `agentic-repository-operations-report.lock.yml` | 1 scoped compatibility filter | The official `copilot-requests: write` permission is unsupported by actionlint v1.7.12; upstream [#686](https://github.com/rhysd/actionlint/issues/686) is open. `.github/actionlint.yaml` ignores only that full diagnostic on this generated lock path; all other B3 diagnostics remain visible. Remove the filter when actionlint supports the scope. |
| `agentic-repository-operations-report.lock.yml` | 2 × `queue: max` | Retain as a generated-workflow/tool-compatibility finding. `queue` is emitted by `gh aw` but unknown to actionlint v1.7.12. Do not hand-edit generated lock output; validate a newer compiler/toolchain or generator guidance first. |
| `ops-gitlink-lego-fork.yml` | 4 × SC2028 | Retain while PR #276 is held. The workflow contains unaccepted `contents: write` direct-branch-push behavior; no lint-only change may normalize or legitimize that authority surface. |

The historical findings in `agent-jules-on-issues.yml`, `gemini-dispatch.yml`, `gemini-invoke.yml`, and `gemini-triage.yml` are absent from the latest hosted scan and are therefore no longer treated as current B6 baseline debt. They remain covered by their respective workflow contracts and Issue #192 remediation history.

## Promotion Decision

Do **not** promote this check to required status yet. First, merge and re-run the B3 compatibility filter; then reassess the six unsuppressed residual findings. Promotion requires actionlint support for `copilot-requests` so the scoped filter can be removed, a toolchain-compatible disposition for the two generated-lock `queue` entries, and a separately accepted resolution for the four PR #276 writer-workflow findings—or a documented decision that advisory operation remains the appropriate steady state. Remove the workflow if its pinned compiler/tool version cannot be maintained or if the residual false-positive rate becomes unacceptable.

## References

[1]: [Issue #192 action decision ledger](ACTION-DECISION-LEDGER.md)
[2]: [actionlint repository](https://github.com/rhysd/actionlint)
[3]: [actionlint v1.7.12 revision](https://github.com/rhysd/actionlint/commit/914e7df21a07ef503a81201c76d2b11c789d3fca)
[4]: [actionlint v1.7.12 usage guide](https://github.com/rhysd/actionlint/blob/v1.7.12/docs/usage.md)
[5]: [latest hosted advisory run](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/32526383015)
[6]: [actionlint issue #686: Copilot permission support](https://github.com/rhysd/actionlint/issues/686)
[7]: [GitHub Docs: Creating GitHub Agentic Workflows](https://docs.github.com/en/copilot/how-tos/github-agentic-workflows/creating-github-agentic-workflows)
