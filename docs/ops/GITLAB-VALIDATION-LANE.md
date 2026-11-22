# GitLab validation without a second production writer

GitHub `timerloggedout-spec/termux-monorepo` on `master` remains canonical.
The existing GitLab reconciliation source is
`https://gitlab.com/a-group2180532/termux-monorepo`.
The requested account is `timerloggedout@gmail.com`; membership and access
must be verified in GitLab before changing that project. An email address
alone does not prove its permissions or ownership.

## What this change does

The root `.gitlab-ci.yml` adds an **opt-in validation lane**, not deployment.
It runs the same stdlib-only `repo_gate.py` and `termux_smoke.py` commands
used by the GitHub promotion spine, plus reconciliation regression tests.
It fetches the public canonical GitHub branch as a comparison baseline and
records both immutable source SHAs in a seven-day artifact. Gate scripts run
from the candidate checkout: a green GitLab pipeline is advisory, not proof
that externally supplied code is trusted or approved for promotion.

`TERMUX_GITLAB_CI_ENABLED` must equal `true` before any pipeline is admitted.
Once enabled, branch pushes, merge requests, and manual web runs are allowed;
open merge requests suppress duplicate branch-push pipelines. Schedules, tags,
API triggers, and downstream pipeline triggers are excluded. Runner usage may
consume GitLab compute allocation; no LLM provider calls are added.

## Activation and provisioning

1. Verify the named account can access the existing GitLab project. Do not
   create a similarly named project or replace its repository implicitly.
2. Review this change through the normal GitHub PR and dual-gate process.
3. Deliver the reviewed commit to GitLab through a separately authorized
   synchronization path. The current reconciliation workflow reads GitLab and
   opens GitHub PRs; it does **not** push GitHub changes to GitLab.
4. Validate `.gitlab-ci.yml` with the project's GitLab CI Lint API or editor.
   Local YAML parsing is not a substitute for GitLab's semantic validation.
5. Use an isolated, unprivileged container runner with Python and Git. Do not
   give this job host Docker sockets, production credentials, cloud roles,
   privileged mode, or sensitive mounts. Disable protected-variable access for
   merge request pipelines; review inherited group/project variables before
   enabling the lane. Do not run untrusted candidates on a production runner.
6. Set the non-secret project variable `TERMUX_GITLAB_CI_ENABLED=true` only
   after review. Run once, then record project ID, pipeline/job URLs, runner
   identity, candidate SHA, canonical baseline SHA, and gate conclusions.
7. Disable the variable to stop new pipelines; cancel already running jobs
   separately. This is the rollback; no application deployment is changed.

This change does not provision hosts, alter project settings, add secrets,
install runners, create schedules, or claim a GitLab pipeline has run.

## LLM CI/CD and production

Keep the existing GitHub LLM/agent workflows as the execution owners. Do not
copy provider keys into this validation job or execute merge-request text as
instructions. Future GitLab LLM review must use a separate explicitly enabled,
bounded lane with reviewed model/provider, spending limit, secret access,
prompt-injection defenses, and attributable SHA-bound results. Generated code
returns through the canonical GitHub PR path, not a second autonomous writer.

Production provisioning or deployment needs a separate recorded lane in
`docs/DEPLOYMENT-LANES.md`: provider, project, root, source SHA, authority,
approval/credentials boundary, verification, and rollback. This validation
pipeline intentionally contains no placeholder deploy job or automatic apply.

## Reconciliation repair

[Run 39725770282](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39725770282)
fetched GitLab successfully but failed because the runner lacked a Git
committer identity, before an actual merge could be assessed. That is not
evidence of a merge conflict or expired GitLab credentials. The companion
repair sets a repository-local automation identity and fixes safe Markdown
summary output. It preserves the existing read-only GitLab boundary and
normal GitHub review/promotion path.

See [the governed reconciliation contract](GITHUB-GITLAB-GOVERNED-RECONCILIATION.md),
[GitLab workflow rules](https://docs.gitlab.com/ci/yaml/workflow/), and
[GitLab CI Lint](https://docs.gitlab.com/api/lint/).

## Compute and storage quota ledger

The existing validation job is a bounded **secondary compute lane**, separate
from the GitLab mirror/webhook redundancy path and separate from GitHub's
canonical promotion authority.

| Resource | GitLab.com Free published entitlement | Ledger record | Current account state |
|---|---:|---|---|
| Instance-runner compute | 400 compute minutes per top-level namespace per month | `gitlab.ci.compute_minutes` in `ops/quota/registry.json` | Namespace tier, cost factor, used and remaining minutes **UNKNOWN** |
| Repository + Git LFS | 10 GiB per project | `gitlab.project.repository_lfs_storage` in `ops/quota/registry.json`; storage plane also appears in `ops/free-storage/free-storage-registry.json` | Project tier and current repository/LFS usage **UNKNOWN** |

The compute quota is aggregated at the top-level namespace. Job compute is
calculated from running duration multiplied by the runner/project cost factor;
parallel jobs can consume more compute than the pipeline's wall-clock time.
The documented monthly allocation resets on the first day of each calendar
month. Project runners are outside the instance-runner compute quota; the
current project runner class remains unverified.

The [GitLab Namespaces API](https://docs.gitlab.com/api/namespaces/) documents `GET /api/v4/namespaces/:id` with
`ci_minutes_usage` fields for eligible top-level groups when the caller has
the Owner role. The namespace ID, Owner access, and a live usage observation
remain unverified. Account usage remains unobserved; development performed zero account requests.

The registry records an **80% planning factor** (320 minutes/month against the
published 400-minute Free entitlement). This is an advisory planning ceiling; runtime reservation and monthly
enforcement remain unimplemented. The existing ten-minute job
timeout bounds one job; monthly spend control requires a separate
account-level guard. The allocation ledger keeps
both GitLab resources explicitly held outside focus pools until namespace
plan, live usage, runner class, and an owner-approved allocation are verified.
The public dashboard therefore reports the entitlement with unknown account
consumption rather than manufacturing remaining quota.

The lane remains gated by `TERMUX_GITLAB_CI_ENABLED=true`. Keep that variable
unset until the existing GitLab project and namespace are verified, a live
quota reading is captured, and the expected runner class is confirmed. This
keeps the compute backend ready for controlled activation while preserving
the current zero-admission posture.
