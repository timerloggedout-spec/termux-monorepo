# Public-surface publishing and branch reconciliation — 2026-11-15

**Status:** RECON complete for the targeted public-web lanes; implementation plan proposed.  
**Authority:** repository refs, pull requests, compare results, existing version manifests and deployment contracts.  
**Boundary:** this record is observational and design-only. It does not authorize merging, deleting branches, or publishing a deployment.

## 1. Executive finding

The public-web estate has several overlapping but distinct evidence layers:

1. Git refs and PRs establish candidate source changes.
2. The generated docs-branch index records 277 `docs/*` / `docs-lane-*` branches and their registry/PR relationships.
3. Tribute's `version-manifest.json` identifies the exact built dashboard source SHA and page-content hashes.
4. `SURFACES-MAP.md` records page ownership, source dependencies and release-layer semantics.
5. `DEPLOYMENT-LANES.md` distinguishes configured hosting from a verified deployed artifact.

These are complementary, not interchangeable. A branch name is not a release; a PR is not a deployment; a green workflow is not proof that the expected URL serves the expected SHA.

The next improvement should connect these existing systems in a single read-only **Public Publishing / Release Reconciliation** view. Do not create a competing version registry, duplicate the docs-branch index, or introduce another publisher.

## 2. Current evidence snapshot

### 2.1 GitHub Pages repository

Repository: [timerloggedout-spec/timerloggedout-spec.github.io](https://github.com/timerloggedout-spec/timerloggedout-spec.github.io)  
Default branch: `main`  
Branch inventory observed: **53 refs**.

The following targeted branches were compared against `main`. This is a selected reconciliation sample, not a claim that every branch was compared.

| Branch | Ahead | Behind | Observed disposition |
|---|---:|---:|---|
| `brand/ai-elves-site-identity-20261112` | 0 | 2,031 | No unique commit to publish; no PR found |
| `automate-studysprint-pages-release-sync-20261105` | 2 | 2,192 | Diverged; PR #45 exists, not in current open-PR result |
| `delphi-video-embed` | 0 | 2,405 | No unique commit to publish; historical PR #25 |
| `delphi-youtube-swap` | 0 | 2,384 | No unique commit to publish; historical PR #27 |
| `feat/repo-story-xlink` | 0 | 2,701 | No unique commit to publish |
| `fix/tribute-navigation-sitemap` | 7 | 2,696 | Diverged; historical PR #21 |
| `fix/agent-readability-p0-discovery` | 52 | 1,625 | Strongly diverged; historical PR #46 and later readability PRs exist |
| `awesome-muse-feature` | 0 | 2,287 | No unique commit to publish |
| `studysprint-version-refresh-051` | 0 | 2,244 | No unique commit to publish |
| `studysprint-web-sync-0.5.1` | 0 | 2,246 | No unique commit to publish |
| `studysprint-demo-final2` | 0 | 2,321 | No unique commit to publish |
| `main-landing-studysprint-link` | 0 | 0 | Identical to current `main` |

The comparisons show why branch names and old PR existence are insufficient promotion signals. Several named feature branches contain no commits beyond current `main`; others contain old, divergent deltas that require file-level review and a deliberate port/rebase decision. Do not wholesale-merge these branches.

### 2.2 AI ELVES branch finding

Two likely AI ELVES sources were checked:

- Pages branch `brand/ai-elves-site-identity-20261112`: **0 ahead / 2,031 behind** `main`, with no PR found.
- Monorepo branch `docs/ai-elves-readme-and-experiments-20261112`: **0 ahead / 4,189 behind** `master`; the generated `DOCS-BRANCH-INDEX.md` lists it as an **orphan lane**, with no PR or registry proposal.

Neither branch currently exposes a unique commit delta to publish. The current public landing page remains branded **Autonomous AI Employees**. The branch names alone do not establish that a new AI ELVES identity or content update is ready. If there is a different source branch or repository, it must be discovered and compared before publication.

### 2.3 Existing promotion PR reconciliation

The original single-Short promotion branches were based on older source tips. They have been superseded by fresh current-default-branch PRs:

| Repository | Current PR | State | Branch comparison |
|---|---|---|---|
| [GitHub Pages site](https://github.com/timerloggedout-spec/timerloggedout-spec.github.io) | [#51 — curated teaser and demo library](https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/pull/51) | Open | 5 ahead / 0 behind |
| [Termux monorepo](https://github.com/timerloggedout-spec/termux-monorepo) | [#5450 — promote video library across public surfaces](https://github.com/timerloggedout-spec/termux-monorepo/pull/5450) | Open | 3 ahead / 0 behind |

Superseded PRs were closed without merging and their branches retained:

- Site PR [#50](https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/pull/50) → replaced by #51.
- Monorepo PR [#5449](https://github.com/timerloggedout-spec/termux-monorepo/pull/5449) → replaced by #5450.

At the time of this snapshot, the monorepo PR's checks were queued. The site connector returned no PR workflow runs. These are not deployment receipts. Neither new PR has been merged or published by this work.

## 3. Existing systems to reuse

| Existing source | What it proves | What it does not prove |
|---|---|---|
| `docs/ops/DOCS-BRANCH-INDEX.md` + `scripts/ops/generate_docs_branch_index.py` | Inventory of 277 docs branches; open PR and proposal links | Branch divergence, code health, web deployment |
| `apps/tribute-dashboard/pr-lanes.html` + `data/pr-lane-feed.json` | Descriptive classification of open monorepo PRs | Full branch census or deployment status |
| `apps/tribute-dashboard/versioning.js` + `version-manifest.json` | Exact dashboard build source SHA, page IDs and page hashes | Candidate branch readiness before a preview exists |
| `apps/tribute-dashboard/versioning.html` | Production-versus-preview artifact comparison | Whether a branch should be merged |
| `docs/ops/SURFACES-MAP.md` | Page ownership, dependencies, code layers and release semantics | Current PR or branch state |
| `docs/DEPLOYMENT-LANES.md` | Hosting lane identity and documented publication posture | Live deployment correctness without current receipts |
| `docs/ops/DASHBOARD-VERSIONING-AND-PREVIEW-STANDARD.md` | Preview → compare → merge → production verification contract | Automatic authorization to promote |

Important deployment constraint: `DEPLOYMENT-LANES.md` currently records GitHub Pages as configured but publication verification as unverified. Do not upgrade that label without a successful deployment and a live source-SHA check.

## 4. Proposed unified view

Add a read-only Tribute surface tentatively named **Publishing**. It should join evidence without becoming another authority.

### 4.1 Source inputs

- GitHub Pages repository branch list and open PR list.
- Compare results for PR heads against their declared base branches.
- Existing monorepo docs-branch index, linked as the authoritative docs-lane inventory.
- Existing monorepo PR-lanes view, linked as the authoritative descriptive PR classifier.
- Existing production/preview `version-manifest.json` values.
- Existing deployment workflow receipts and public URL verification where available.

### 4.2 Minimum record shape

Each candidate record should expose:

- repository, default branch, branch/ref, immutable head SHA;
- base ref/SHA, merge-base SHA, ahead/behind counts and changed paths;
- linked PR number, URL, state, draft flag and updated timestamp;
- exact-head check state, including `UNKNOWN` when unavailable;
- preview URL and preview source SHA, if created;
- deployed URL, deployment run/receipt and deployed source SHA, if verified;
- generated-at timestamp, source provenance and warnings;
- explicit disposition, with reason.

### 4.3 State vocabulary

Use independent lifecycle states rather than one misleading green/red badge:

- `UNLINKED` — branch has no matching PR.
- `NO_DELTA` — branch has no unique commits relative to its baseline.
- `AHEAD` — candidate is ahead and not behind its baseline.
- `DIVERGED` — both candidate and baseline contain unique commits; requires reconciliation.
- `BEHIND` — candidate lacks baseline changes; do not promote as-is.
- `PR_OPEN`, `PR_CLOSED`, `PR_MERGED` — PR lifecycle, separate from branch state.
- `CHECKS_PENDING`, `CHECKS_PASS`, `CHECKS_FAIL`, `CHECKS_UNKNOWN`.
- `PREVIEWED`, `PREVIEW_VERIFIED`, `MERGED`, `DEPLOYED`, `LIVE_VERIFIED`.

A missing check, missing deployment receipt, or stale feed must remain `UNKNOWN`, never silently count as success.

### 4.4 Promotion policy

1. Resolve refs to immutable SHAs before comparing.
2. Stop on divergence or missing source identity; never force-push or wholesale-merge an old branch.
3. Use small PRs from current default branches for additive work.
4. Preview the exact candidate SHA using the existing Tribute preview workflow.
5. Compare preview and production using the existing version manifests and per-page hashes.
6. Merge only under repository protections and the established human approval boundary.
7. Verify the post-merge deployment's source SHA and public URL.
8. Preserve closed branches and historical PRs as evidence; cleanup is a separate, explicitly authorized operation.

## 5. Implementation plan

### Phase A — branch and PR evidence
- Add a read-only collector for the public Pages repository.
- Enumerate branches and open PRs; calculate ahead/behind only for PR-linked branches to keep API use bounded.
- Preserve API errors, rate limits and incomplete pagination as explicit warnings.
- Unit-test state classification and malformed/missing API fields.

### Phase B — Tribute Publishing surface
- Add `publishing.html` and a text-first Markdown mirror.
- Reuse `versioning.js`, the shared navigation, dashboard CSS and existing release manifest builder.
- Link the Publishing surface to PR Lanes, Version Comparison, Surfaces Map and the generated docs-branch index.
- Show branch inventory and open-PR evidence separately from preview/deployment evidence.

### Phase C — verification and publication
- Add the page and its source contract to the dashboard verification suite and Surfaces Map generator.
- Run the existing dashboard regression suite and manifest builder.
- Use the existing preview workflow and verify the preview's exact source SHA.
- Merge and publish only after the normal repository gates and approval; then verify the public URL and manifest.

### Non-goals
- No automatic PR merge or branch deletion.
- No new secrets or GitHub App registration.
- No duplicate version registry.
- No replacement of the existing docs-branch index, PR-lanes classifier, or Tribute version manifest.
- No claim that an AI ELVES branch is publishable until a unique, reviewed source delta is identified.

## 6. Decision

Proceed with the unified read-only Publishing view as an extension of the existing Tribute control surface. Keep branch reconciliation, PR review, preview comparison, merge, deployment, and live verification as separate observable steps.
