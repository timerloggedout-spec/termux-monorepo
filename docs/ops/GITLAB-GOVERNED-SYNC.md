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

## Current evidence

The repository's actions-refinements record documents a recent external GitLab failure independently of repository-owned validation: on the 2026-08-20 master revision, context `ci/gitlab/gitlab.com` pointed at GitLab pipeline `2776955893`. That record explicitly treats the GitLab result as an external status observation rather than evidence that the associated GitHub change failed.

Issue #95 also records the historical merge-friction pattern: a GitLab mirror failure could block an otherwise corrected pull request, motivating an explicit policy to audit whether that external status is production-critical.

## Operating rule

GitHub `master` remains the promotion spine. A GitLab-origin commit becomes part of `master` only after the normal GitHub gates and review path accept the reconciliation PR.

If GitLab should instead become authoritative, change that policy explicitly and replace this controller with a GitLab pull-mirror design. Do not silently convert the repository into bidirectional mirroring: GitLab documents that bidirectional mirroring can cause conflicts.
