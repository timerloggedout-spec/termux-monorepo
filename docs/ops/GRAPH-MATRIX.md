# Graph Matrix — commits × issues × PRs × branches linkage integrity

[MUSEai]@{role:{graph-matrix}} · Repo Organization tree (mgr `ec42d7e8`) · single-writer: Graph lane
Machine census: `ops/graph-matrix/census.json` (schema `graph-matrix/v1`) · generator: `scripts/graph_matrix_census.py`
Scope: linkage integrity ONLY. ¬ narrative (Repo-Story / Commit Replay) · ¬ activity rollup (Tracking lane consumes this, not vice versa).

## Axes

| axis | node class | census v0 n |
|---|---|---|
| C | commits (PR commits; master DAG owned by Commit Replay) | — |
| I | issues (open + closed) | 453 |
| P | pull requests (open / merged / closed-unmerged) | 2,795 |
| B | branches (`refs/heads/*`) | 2,664 |

## Cell semantics

Edge layers, kept separate everywhere:

- **strict** — GitHub-native link: PR `closingIssuesReferences`.
- **surface-issue** — authored `#n` in title/body where `n` is an issue.
- **any-ref** — authored `#n` in title/body, any target (issue or PR).
- Timeline auto cross-references do **not** count as authored backlinks.

Cell states: `linked | surface-only | strict-only | unlinked | one-way | residual | missing`.

| cell | meaning | complete ⇔ |
|---|---|---|
| I→P | issue claimed by a PR | every open issue has ≥1 PR edge, or an explicit no-PR disposition |
| P→I | PR linked to an issue | strict > 0, or surface-issue present |
| P→C | PR carries commits | commits ≥ 1 |
| B→P | branch has associated PRs | ≥ 1 (0 = orphan) |
| P→B | open PR head branch exists | headRefName ∈ live refs |
| B×P lifecycle | merged/closed PR ⇒ head branch deleted | residual head = leak (v0: name-match signal; v1 gate: tip-SHA match before any deletion list) |
| I↔I, P→P | authored cross-refs | symmetric; A→B ∧ B↛A = one-way backlink |

Anomaly classes: merged-but-unclosed (merged PR's closing issue still OPEN — disposition stays with the issue owner; this lane comments backlinks only, never closes) · closed-but-unmerged (disposition queue, not auto-error) · stale branch (tip committedDate < census − 30d) · orphan branch (associatedPullRequests = 0).

## Census v0 — 2026-11-01T20:17–20:26Z (firsthand, PAT GraphQL, all nodes paginated)

Window note: merged total drifted +3 vs census-start totals (live churn).

### Branches — total 2,664

| metric | n |
|---|---|
| stale | 854 |
| orphan (no associated PR) | 346 |
| stale ∧ orphan | 78 |
| fresh (< 30d) | 1,810 |

Top prefixes: `ops` 450 · `feat` 314 · `fix` 270 · `docs` 184 · `backup` 62. Full stale∧orphan list: census.json. Branch deletion is **list-only** — no lane deletes branches on census evidence alone.

### PRs — total 2,795 (open 171 · merged 2,151 · closed-unmerged 473)

| cell | open | merged |
|---|---|---|
| no closing ref (strict ∅) | 165 | 2,122 |
| unlinked (no closing ∧ no surface-issue ref) | 138 | 1,260 |
| unlinked (any-ref layer) | 114 | 691 |

P→C: open PRs with 0 commits = 0. P→B: open PR head missing from refs at census = 1 (PR #3253 — resolved 2026-11-01T21:24Z: merged `47a7d1363f98`, head deleted on merge = clean lifecycle).
B×P residual (name-match, v0 signal only): merged-PR head name still in refs 2,078 / 2,151; closed-unmerged head 467 / 473 — auto-delete-head-branches is evidently off.

### Issues — total 453 (open 380 · closed 73)

| metric | n |
|---|---|
| open, surface-unlinked (any-ref) | 170 |
| open, strict-unlinked (∅ ref ∧ ∉ any PR closing set) | 151 |
| open, linked by PR closing only (no authored ref) | 19 |

### Anomalies v0

- **Merged-but-unclosed ×18** — issues #122, #129, #130, #150, #157, #158, #164, #175, #179, #181, #192, #201, #268, #320, #529, #2626, #2728, #3082. Fix tranche-1 = authored backlink comment on each (comment-only; closing disposition = issue owners — several are living references).
- **One-way I↔I pairs: 319** vs mutual pairs: 2. Exemplar (verified): PR #2489 (merged 2026-10-30) body → #1801; #1801 body refs = {#1792} only.
- Closed-but-unmerged PRs: 473 (queue, census.json per-PR state via generator re-run).

## Maintenance

Re-run `scripts/graph_matrix_census.py` (token: `GH_TOKEN`/`GITHUB_TOKEN`), refresh census.json + the tables above in one PR, report delta ↑ Repo Organization manager. Counts are always firsthand from the API at census time — never copied forward.

## Freeze note (2026-11-01) — deletion framing superseded-by-freeze

> Owner correction via main (2026-11-01): **DELETION IS PROHIBITED repo-wide.** Rationale: keep + archive + back up — the datasets are not compiled yet; all repo content is uncompiled dataset material for the ML pipelines, so nothing in the tree is surplus or prunable until the datasets exist. Sanctioned retirement = **ARCHIVE** (content kept in-tree, preserved, additive notes only; issue #3280 pattern). Consolidation = additive notes only; in-tree blob-identical moves allowed.
>
> Effect on this document (annotation only — the v0 text above stays in place): every deletion-oriented phrase is **superseded-by-freeze**, including "Branch deletion is list-only", the B×P lifecycle wording "residual head = leak … before any deletion list", and the stale∧orphan branch list in census.json as any kind of removal queue. Branch lists remain census records only; branches are not content files, and branch-deletion stays HELD until main speaks to branches specifically.
>
> Language rule for future censuses: "stale" / "orphan" are descriptive linkage states only — they imply no pruning candidacy. Census and backlink (additive) work is unaffected by the freeze.

## Signal note (2026-11-01) — branch lists = dataset signal, KEPT-AS-SIGNAL

> Owner refinement via main (2026-11-01): **"list+only is a signal for the dataset."** The branch lists produced by this matrix — stale / orphan / linkage classifications, incl. the stale∧orphan list and head-residual counts in census.json — are **dataset material, retained as data permanently**: branch linkage and staleness metadata feeds dataset compilation. They are not deletion candidates and not a work queue, and no deletion semantics attach to them anywhere.
>
> Status conversion: branch lists move from HELD (freeze note above, "until main speaks to branches specifically") to **KEPT-AS-SIGNAL, permanently** — main has now spoken. The census keeps producing these lists as signal at each pass; nothing downstream of them is an action queue.

## Wiring note (2026-11-01) — census automation live

> Census refresh is automated: `.github/workflows/graph-matrix-census.yml` — triggers = workflow_dispatch + weekly floor (Thu 07:23Z) + push on the census inputs (`scripts/graph_matrix_census.py`, the workflow itself); cadence per the decision-tree model (event + weekly floor), not the fixed-cron class. Runtime auth = Termux Fleet Swarm app token (SEC-03 mint-before-checkout, own 5000/h bucket); commit-back of `ops/graph-matrix/census.json` direct to master, single-writer = this workflow. The Maintenance section above ("re-run … report delta") now runs through this workflow; lane re-runs remain possible on mgr demand.

## Cadence amendment (2026-11-01) — weekly struck, drift-gated dynamic check

> Owner correction via main (2026-11-01): the weekly schedule in the wiring note above is **struck** (annotation — original text stays): a fixed clock fails the quota-optimization and dynamic-cadence conventions. Amended cadence := { workflow_dispatch · push-on-script · **drift-gated dynamic check** }: `.github/workflows/graph-matrix-probe.yml` runs on master push (bursts coalesce, cancel-in-progress) and executes `scripts/graph_matrix_probe.py` — one GraphQL totals query comparing live totals vs the census.json baseline plus the GraphQL headroom returned by the same query; it dispatches this census workflow only when drift ≥ threshold on any axis (branches 20 · PRs 25 · merged 20 · open issues 10, derived from observed v0→#2 churn) **and** headroom ≥ 1,000 points. Quota-aware timing; state-driven, never clock-driven.
