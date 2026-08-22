# GitLab governed synchronization

## Purpose

`a-group2180532/termux-monorepo` is an external change source that has recently advanced independently of GitHub. The repository must therefore be treated as a **governed synchronization pair**, not as a blind one-way status mirror.

The GitHub controller in `.github/workflows/gitlab-governed-sync.yml` periodically fetches the GitLab ref and classifies the relationship with GitHub `master`:

- **GitLab behind** — no action; GitHub already contains the GitLab history.
- **GitLab ahead** — prepare a review branch containing the GitLab commits.
- **Diverged** — attempt a normal merge; if conflicts exist, fail closed and require manual reconciliation.

## Safety model

The controller:

1. never force-pushes;
2. never resets `master` to GitLab;
3. never rewrites GitLab;
4. never treats a GitLab CI result as proof that GitHub code is correct;
5. creates a normal GitHub pull request for review when reconciliation is clean;
6. stops on merge conflicts instead of manufacturing a synthetic resolution.

This is deliberately stronger than a simple mirror because the GitLab side has recent commits that may represent legitimate work rather than a stale replica.

## Agentic development environment coordination

GitHub and GitLab may both host CodeRabbit reviews, but **one revision gets one corrective-write owner at a time**.

The coordination controller in `.github/workflows/agent-platform-coordination.yml` fetches GitLab `master` using the repository's `GITLAB_TOKEN` secret and compares it with the GitHub PR head. It records one of four states:

- `aligned` — same revision; GitHub is the default corrective-write lane.
- `github-ahead` — GitHub owns the corrective-write lane; GitLab is review/shadow-only.
- `gitlab-ahead` — GitLab-origin work owns the corrective-write lane; GitHub is review/shadow-only until reconciliation.
- `diverged` — both platforms are held from automated corrective writes until reconciliation.

The lease is keyed by PR and head SHA and is deliberately **advisory**: it does not invoke CodeRabbit, push commits, or grant cross-platform write authority. This is important because CodeRabbit is already configured for automatic incremental reviews and autofix on GitHub (`.coderabbit.yaml`).

### CodeRabbit operating rule

- CodeRabbit may review on both platforms.
- Do not allow both CodeRabbit instances to perform corrective writes against the same revision concurrently.
- A platform marked `*-primary` is the only automated corrective-write lane for that revision.
- The other platform remains review/shadow-only until the head SHA changes or an operator explicitly transfers ownership.
- `diverged` means no automated corrective writes; resolve the repository relationship first.
- Review comments may be relayed to downstream agents, but provider-control messages (for example review-trigger UI notices or rate-limit notices) are not substantive review feedback. The existing GitHub agent relay in `.github/workflows/agent-review-auto-jules.yml` already distinguishes those cases and debounces provider feedback by source revision.

This prevents the common failure loop where GitHub CodeRabbit fixes a commit, GitLab CodeRabbit sees the mirrored commit and fixes it again, the mirror carries that second change back, and both reviewers re-open each other's work.

## Credential boundary

The coordination workflow consumes `GITLAB_TOKEN` only as a GitLab API/Git transport credential. It does not print the token, write it into repository files, or expose it to review comments.

`OPERATOR_GITLAB_TOKEN` and any GitHub cross-platform credential should remain operator-only credentials. They must not be substituted into ordinary review jobs merely because they can reach the other platform.

## Current evidence

The repository's actions-refinements record documents a recent external GitLab failure independently of repository-owned validation: on the 2026-08-20 master revision, context `ci/gitlab/gitlab.com` pointed at GitLab pipeline `2776955893`. That record explicitly treats the GitLab result as an external status observation rather than evidence that the associated GitHub change failed.

Issue #95 also records the historical merge-friction pattern: a GitLab mirror failure could block an otherwise corrected pull request, motivating an explicit policy to audit whether that external status is production-critical.

## Operating rule

GitHub `master` remains the promotion spine. A GitLab-origin commit becomes part of `master` only after the normal GitHub gates and review path accept the reconciliation PR.

If GitLab should instead become authoritative, change that policy explicitly and replace this controller with a GitLab pull-mirror design. Do not silently convert the repository into bidirectional mirroring: GitLab documents that bidirectional mirroring can cause conflicts.
