# Publishing reconciliation — Tribute

Read-only live view for public website branches and open pull requests.

- [Open Publishing reconciliation](https://timerloggedout-spec.github.io/tribute/publishing.html)
- [Website repository branches](https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/branches)
- [Open website pull requests](https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/pulls?q=is%3Apr+is%3Aopen)
- [Monorepo docs branch index](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/DOCS-BRANCH-INDEX.md)
- [Monorepo PR Lanes](https://timerloggedout-spec.github.io/tribute/pr-lanes.html)
- [Tribute version comparison](https://timerloggedout-spec.github.io/tribute/versioning.html)
- [Tribute surfaces map](https://timerloggedout-spec.github.io/tribute/surfaces-map.html)
- [Deployment lanes](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/DEPLOYMENT-LANES.md)

## State vocabulary

- DEFAULT: repository default branch.
- UNLINKED: branch has no matching open PR; this is not by itself a stale/obsolete judgement.
- AHEAD: PR head has unique commits and is not behind its base.
- DIVERGED: both head and base have unique commits; reconcile before promotion.
- BEHIND: candidate has no unique commits and is behind its base.
- NO_DELTA: head and base are identical.
- UNKNOWN: comparison unavailable or incomplete.

The browser reads the public GitHub API without credentials. It lists up to 100 branches and 100 open PRs, compares up to 20 PR heads per refresh, and performs targeted comparisons for branches whose names contain ai-elves. The PR table shows base ref/SHA, merge-base SHA, and head SHA. Other unlinked branches are listed without full history comparison.


The live dashboard compares `main-landing-studysprint-link` (the legacy Pages source) directly with the website repository's default branch and shows whether it is aligned, fast-forwardable, diverged, or ahead.

The live dashboard also reads the latest `tribute-dashboard-deploy.yml` runs from the monorepo and the latest GitHub Pages deployment runs from the public website repository. Each row exposes workflow status, conclusion, source SHA, event, timestamp, and a link to the run. A queued run is not a deployment receipt; a successful run still requires a fresh live-URL check.

The cross-repository publisher is serialized under the `tribute-dashboard-publish` concurrency group. An active publish is allowed to finish; newer pending snapshots replace older pending snapshots so publication order converges on the latest source.

Deployment and publication remain separate evidence steps. This view never approves, merges, deletes branches or claims that a live URL serves a particular SHA.
