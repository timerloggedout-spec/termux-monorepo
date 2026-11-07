# Current authority and chronology — 2026-11-07

> **Authority rule:** `workspace/llm_map/context_relationships/manifest.json` on canonical `master` is the source of truth for current corpus state. This document is a dated operational history, not a live dashboard. Older tables and addenda below are historical observations; they must never override a later manifest observation.

## Latest directly verified manifest

Fetched from canonical `master` on 2026-11-07; the manifest's latest observation is **2026-10-26T13:04:26.270236Z**:

| Signal | Value |
|---|---:|
| Nodes | 35,221 |
| Edges | 57,358 |
| Verified edges | 52,416 |
| Candidate edges | 4,942 |
| Unresolved internal references | 120 |
| Source parser failures | 12 |
| Excluded files | 1,392 |
| History coverage | `PARTIAL_CONTINUATION_REQUIRED` |
| Next history page | 2 |
| Issues complete | false |
| Pull requests complete | false |
| Checkpoint eligible | false |

**Interpretation:** the corpus is not complete and is not checkpoint eligible. Do not use the older 2026-10-20 addendum's 2026-10-15 observation (which reported pagination exhausted) as current state: the later 2026-10-26 manifest supersedes it and again records page 2 with incomplete issue/PR coverage.

## Current automation paths verified on master

- Collector: `.github/workflows/context-relationship-backfill.yml`
- Runtime observer: `.github/workflows/context-relationship-backfill-watcher.yml`
- The legacy `.github/workflows/historical-backfill-promotion-gate.yml` path is absent.

A current-master workflow definition is not proof of runtime execution. No new backfill execution or promotion is claimed by this reconciliation. The next evidence receipt must include run ID/attempt, immutable source SHA, job conclusions, artifacts, validation output, and the resulting manifest observation.

## Outstanding acceptance work

1. Run a bounded continuation from current master using the canonical manifest checkpoint.
2. Confirm the build was not deferred and no stale artifacts were consumed.
3. Validate manifest/input/schema hashes, corpus reconciliation, artifact set, and page advancement.
4. Record watcher receipt and resulting manifest; repeat until `next_start_page=null`.
5. Resolve/disposition parser failures and unresolved references before checkpoint eligibility.
6. Preserve each observation as dated history; never overwrite or silently relabel older measurements.

---

> **Current-state reconciliation (2026-11-02):** This document contains dated historical observations and must not be read as a continuously refreshed live dashboard. The canonical manifest currently available on `master` was last observed at **2026-10-26T13:04:26.270236Z** and reports **35,221 nodes, 57,358 edges, 52,416 verified edges, 4,942 candidate edges, 120 unresolved internal references, 12 source parser failures, and 1,392 excluded files**. Its history coverage is `PARTIAL_CONTINUATION_REQUIRED`, `history_window.next_start_page=2`, both issues/PR completeness flags are false, and `github_report.checkpoint_eligible=false`. Do not infer that the corpus is complete or checkpoint-eligible. Runtime review found run [40058473861](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/40058473861) failed validation after a deferred HTTP 403 build, while [39962654795](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39962654795) concluded successfully with the build and coverage-summary steps skipped. See [the 2026-11-02 continuous audit](CONTINUOUS-REPOSITORY-AUDIT-2026-11-02.md) for evidence and remediation criteria.

---

# Historical Corpus Actions Backfill — Live Status

**Tracking:** #522
**Authority:** `workspace/llm_map/context_relationships/manifest.json`
**Rule:** `next_start_page` must reach `null` before the corpus can be called complete.

## Master — canonical production corpus

Observed manifest: **2026-08-19T07:53:15Z**

| Metric | Value |
| --- | ---: |
| Nodes | 8,339 |
| Edges | 15,120 |
| Verified edges | 13,041 |
| Candidate edges | 2,079 |
| PRs in current history window | 20 |
| Issues in current history window | 20 |
| PR commits | 282 |
| PR comments | 392 |
| Reviews | 172 |
| Review comments | 246 |
| Explicit references | 157 |
| Timeline cross-references | 9 |
| Next page | **2** |

**Coverage:** `PARTIAL_CONTINUATION_REQUIRED`

## master-staging — newer but not promotable as a branch

Observed manifest: **2026-09-07T12:33:24Z**

| Metric | Value |
| --- | ---: |
| Nodes | 11,597 |
| Edges | 20,985 |
| Verified edges | 18,443 |
| Candidate edges | 2,542 |
| PRs in current history window | 50 |
| Issues in current history window | 50 |
| PR commits | 275 |
| PR comments | 378 |
| Reviews | 105 |
| Review comments | 159 |
| Explicit references | 127 |
| Timeline cross-references | 14 |
| Next page | **2** |

GitHub compare currently classifies `master...master-staging` as **diverged**, with the staging branch 50 commits ahead and 455 behind current master. Therefore the larger corpus is useful evidence but **must not be promoted wholesale**.

## Control-plane finding

`.github/workflows/context-relationship-backfill.yml` is deliberately manual and page-bounded, which is correct for a historical collector. The current implementation, however, checks out `master-staging` and pushes its generated corpus back to that branch.

That is now the primary operational defect: the continuation target is stale/diverged from the canonical branch.

## Correct continuation model

```text
current master SHA
      |
      +--> fresh bounded backfill ref
                |
                +--> page N
                |
                +--> validate corpus
                |
                +--> record next_start_page
                |
                +--> review/promote only the corpus delta
                |
                +--> next bounded ref
```

Do not:

- merge the stale `master-staging` branch wholesale;
- infer completeness from node/edge growth;
- turn missing history into zeroes;
- overwrite prior evidence;
- skip the manifest/checkpoint validation between windows.

## Promotion gate

A bounded continuation is promotable only when:

1. source SHA/ref is recorded;
2. start and next pages are recorded;
3. manifest/input/schema hashes are preserved;
4. corpus reconciliation passes;
5. the diff is limited to the intended corpus delta and required metadata;
6. the resulting branch is based on current master;
7. the resulting `next_start_page` is retained for the next continuation.

## SHE contract

SHE should render:

- canonical master coverage separately from staging/research coverage;
- `PARTIAL_CONTINUATION_REQUIRED` while `next_start_page != null`;
- the newest observed corpus timestamp;
- source branch and source SHA;
- validation/promotion state;
- unresolved references and parser/collection exclusions;
- explicit `UNVERIFIED` state where runtime evidence is absent.

The dashboard must not silently substitute the larger staging corpus for master.

## Implemented continuation upgrade

The continuation control plane is now anchored to canonical `master`. `.github/workflows/context-relationship-backfill.yml` no longer checks out or pushes the diverged `master-staging` branch. When no page is explicitly supplied, it reads `history_window.next_start_page` from the canonical manifest and resumes that page.

The builder now also emits an L2 temporal evidence layer under `workspace/llm_map/context_relationships/temporal/`: immutable snapshots, structural deltas, and append-only lineage. Snapshot identity includes source SHA/ref, observation/page bounds, and graph content hashes. The latest observation is exposed through `temporal-current.json` and summarized by `snapshot_id`, `previous_snapshot_id`, `coverage`, and `delta` in `build-summary.json`.

The next collection window should therefore resume from the canonical manifest's current `history_window.next_start_page` (currently documented as page `2` in the historical evidence above), validate the new temporal artifacts, and continue until `next_start_page` is `null`. No claim of live completion is made by this documentation update.


---

## Reconciliation addendum — 2026-10-20

The earlier tables above are dated snapshots, not current measurements. The latest inspected canonical `master` manifest is observed at `2026-10-15T19:16:02.945529Z` and reports:

| Metric | Current manifest |
| --- | ---: |
| Nodes | 30,978 |
| Edges | 52,624 |
| Verified edges | 47,845 |
| Candidate edges | 4,779 |
| History start page | 13 |
| Next start page | null |
| Issues complete | true |
| Pull requests complete | true |
| Unresolved internal references | 1 |
| Source parser failures | 14 |
| Checkpoint eligible | false |

This means **history pagination is exhausted, but checkpoint/promotion eligibility is still false**. The remaining validation debt is not to be hidden by the pagination-complete flags.

The current collector is `.github/workflows/context-relationship-backfill.yml` and targets canonical `master`; the current observer is `.github/workflows/context-relationship-backfill-watcher.yml`. The legacy `historical-backfill-promotion-gate.yml` path is absent on current master, so no dedicated workflow-level final promotion gate should be claimed until one is implemented and observed.

Next steps are tracked in [issue #522](https://github.com/timerloggedout-spec/termux-monorepo/issues/522): investigate each parser failure, resolve or disposition the unresolved internal reference, attach exact Actions run/attempt receipts, rerun corpus validation, and only then reconsider checkpoint eligibility. This addendum supplements rather than rewrites the historical measurements above.
