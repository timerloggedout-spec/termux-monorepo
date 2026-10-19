# GitHub ↔ GitLab governed reconciliation

## Authority and scope

GitHub `master` is the canonical promotion spine. GitLab is an external change source to inspect, not an implicitly trusted mirror or a second autonomous writer. This workflow compares **GitHub master SHA ↔ the selected GitLab branch SHA**. A GitHub feature-PR head is not a synchronization baseline.

Workflow: `.github/workflows/gitlab-governed-reconciliation.yml`

## Runtime behavior

- Runs on a six-hour UTC schedule and by manual dispatch.
- Requires the GitHub Actions secret `GITLAB_TOKEN`; if absent, it fails closed rather than silently switching to unauthenticated fetch.
- Validates the requested Git ref and fetches only that branch.
- Classifies the pair as `aligned`, `gitlab-behind`, `gitlab-ahead`, or `diverged`.
- Does nothing when aligned or when GitLab is behind GitHub.
- When GitLab is ahead or histories diverge, attempts an ordinary merge on a uniquely named review branch and opens a normal PR against `master`.
- Stops on merge conflicts. It never force-pushes, resets the canonical branch, writes to GitLab, or auto-merges.
- Reuses an existing reconciliation branch only when ancestry proves it contains both exact source SHAs.
- Records the observed source pair and decision in the Actions summary.

## Credentials

- `GITLAB_TOKEN`: GitHub Actions secret used only for GitLab fetch. Do not echo it, write it to repository files, or place it in artifacts/comments.
- `OPERATOR_GITLAB_TOKEN`: operator-only credential; never substitute it into routine workflow jobs.
- `GITHUB_ALLOW_GITLAB`: do not assume this name is a token or authorization primitive. If a separate feature-flag is intended, define its boolean semantics and test it independently; it does not replace authentication.
- The workflow uses the default `GITHUB_TOKEN` for branch/PR writes intentionally. GitHub suppresses most recursively triggered workflow runs from this token, which prevents unreviewed GitLab-origin code from immediately fanning out into secret-bearing CI. Consequently, automated PR checks are **not promised**; a trusted operator must inspect the diff and explicitly initiate safe validation before promotion.

The GitHub token is supplied by Actions and is limited by the workflow's declared `contents: write` and `pull-requests: write` permissions. These permissions exist to publish a review branch and PR; no automatic merge is performed.

## Explicit non-goals

This is not bidirectional mirroring, a GitLab push workflow, a CodeRabbit enforcement mechanism, or proof that the GitLab pipeline validates GitHub changes. Review-ownership labels/comments alone do not prevent external agents from writing. Enforced single-writer behavior requires an actual provider-side control or an enforced write gate; until then coordination metadata must be described as advisory.

## Evidence and promotion

Treat every run as an observation bound to the GitHub SHA, GitLab SHA, ref, run ID, and attempt. A successful workflow conclusion is not sufficient by itself: verify the PR/branch or no-op classification in the run summary. Promotion remains a separate human/repository-policy decision.
