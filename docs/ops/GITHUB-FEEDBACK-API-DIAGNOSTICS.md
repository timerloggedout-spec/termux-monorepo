# GitHub feedback: proven cause and repair

The original proposal-checklist failure is confirmed as an exhausted **Actions installation core quota**, not a guessed permission problem. A separate authorized user connector works and reports repository-admin access. These are different authentication contexts; one failing does not establish that every GitHub API route is unavailable.

## What actually failed

[Run 39382314585, attempt 1](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39382314585/attempts/1), `vote-hygiene` job `118493978193`, used the Actions-issued `GITHUB_TOKEN`. Runner logs show effective `Contents: read`, `Metadata: read`, `PullRequests: write`, consistent with the workflow declaration. It did not use an OPERATOR/PAT credential.

The failed request was exactly `GET /repos/timerloggedout-spec/termux-monorepo/pulls/1303/files?per_page=100`. GitHub returned HTTP **403**, message **API rate limit exceeded for installation**, and these headers:

| Header | Recorded value |
|---|---:|
| `X-RateLimit-Limit` | 5000 |
| `X-RateLimit-Remaining` | 0 |
| `X-RateLimit-Used` | 5000 |
| `X-RateLimit-Resource` | core |
| `X-RateLimit-Reset` | 1792479727 |

The reset corresponds to 07:02:07 UTC. [Attempt 2](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39382314585/attempts/2), job `118499282119`, succeeded on the same SHA/event and permission model. Registry validation and the local VOTE scan had already passed in the original attempt. This proves the named failure; it does **not** diagnose unrelated failed checks.

## The working authenticated path

The authorized user connector returned HTTP **200** for PR #1297 and repository permissions `admin`, `maintain`, `pull`, `push`, `triage` all true. Through this path, all paginated review, conversation, inline-comment and commit events were collected and normalized against the same PR head before and after collection. The result remains **0 submitted formal reviews, 21 conversation comments, 0 inline comments, 1 commit**. Access success does not manufacture independent votes or prioritization decisions.

Trusted, manual **default-branch-only** provider observation now selects the existing issue-184 authorized operator credential for GitHub metadata reads, with the job token as a missing-credential fallback. It records the selected context, actual repository permissions and core-quota values in `github-feedback-auth.json`. This credential is scoped to a separate GitHub feedback step: it is never passed to providers, public catalog hosts, PR-code tests or untrusted pull-request workflows. No secret value is copied or published, and no new permission grant is requested.

## Code repair and regression protection

The proposal workflow retains the low-privilege PR token, registry validation and VOTE scan. Only a consistent **403 + explicit installation-quota message + core resource + remaining zero + used at least limit + valid reset** may defer its advisory checklist comment. A deferral states **comment not posted**, includes the checklist in the run summary, and never claims a review, posted comment or vote. Other 401/403 responses still fail rather than being relabeled as quota problems.

The write-capable advisory job does **not** check out or execute PR-controlled repository code: its narrow classifier is inline JavaScript. The separate registry-validation job inherits only `contents: read`. An offline Python diagnostic helper mirrors the same predicate for evidence analysis, but is never executed by the write-token job; regression tests enforce that boundary.

The same handling covers PR-files lookup, comment lookup and comment creation. Offline tests execute the actual workflow JavaScript with mocked GitHub responses, covering quota at every stage, authentication/permission failures, successful posting, deduplication, and absence of administrator secrets in the PR workflow. Existing event IDs, authors, commit/head binding and review states remain the source of truth for feedback provenance.

## Merged-production proof

After [PR #1307](https://github.com/timerloggedout-spec/termux-monorepo/pull/1307) merged, [production run 39396483576](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39396483576) completed the authenticated feedback step. Its `github-feedback-auth.json` reports `configured_operator_credential`, repository permissions `admin/maintain/pull/push/triage` all true, and the observed core-quota snapshot `limit: 5000`, `used: 206`, `remaining: 4794`. Those are values at collection, not a current balance guarantee. The paginated, before/after-head-bound review artifact again contains 0 submitted formal reviews, 21 conversation comments, 0 inline comments and 1 commit. This validates the configured operator path in production without changing PR-job privileges, inventing ballots or leaking a credential.
