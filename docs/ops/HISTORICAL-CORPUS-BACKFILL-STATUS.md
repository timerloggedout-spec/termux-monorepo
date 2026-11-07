# Historical Corpus — current authority and reconciliation (2026-11-07)

> **Authority:** `workspace/llm_map/context_relationships/manifest.json` on canonical `master` is authoritative for corpus measurements. This document is a dated operational record, not a live dashboard. Historical tables and addenda below remain useful as snapshots but never override a later manifest.

## Latest directly verified manifest

Fetched from canonical `master` on 2026-11-07; latest observation: **2026-10-26T13:04:26.270236Z**.

| Signal | Value |
|---|---:|
| Nodes / edges | 35,221 / 57,358 |
| Verified / candidate edges | 52,416 / 4,942 |
| Unresolved internal references | 120 |
| Source parser failures | 12 |
| Excluded files | 1,392 |
| History coverage | `PARTIAL_CONTINUATION_REQUIRED` |
| Existing coverage window | page 1, 50 issues + 50 PRs |
| Next history page | 2 |
| Issues / PRs complete | false / false |
| Checkpoint eligible | false |

The canonical manifest already contains a page-one coverage ledger. A separate page-one bootstrap request based on the older October 15 late-page snapshot is therefore obsolete. The current next action is a page-two continuation that preserves the established `max_items=50` page size. The corpus is **not complete** and is **not checkpoint eligible**.

## Runtime evidence and automation

The 2026-11-02 audit cited run [40058473861](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/40058473861), which failed validation after a deferred HTTP 403 build, and [39962654795](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39962654795), which completed with the build and coverage-summary steps skipped. Neither proves a successful corpus continuation.

Current workflow paths on master:
- Collector: `.github/workflows/context-relationship-backfill.yml`
- Runtime observer: `.github/workflows/context-relationship-backfill-watcher.yml`

The workflow is anchored to canonical `master`, resumes from the manifest, validates before committing, and serializes its writer. Its continuation page size must remain consistent with the established page-one window.

## Acceptance evidence required

1. Run the next bounded continuation from current master using page 2 and `max_items=50` for both issue and pull-request families. Keep this page size for subsequent automatic windows.
2. Record immutable source SHA/ref, run ID/attempt, requested and resulting page bounds, and the effective page size.
3. Confirm the build actually executed (not deferred/skipped) and no stale artifacts were consumed.
4. Validate manifest/input/schema hashes, corpus reconciliation, expected artifact set, and page advancement.
5. Record watcher receipt and resulting manifest; repeat until `next_start_page=null`. Before accepting completion, independently reconcile the collected issue and pull-request number sets against the corresponding GitHub REST pages and record the compared IDs/counts; a contiguous page ledger alone does not prove that mutable `updated` ordering omitted no items.
6. Resolve or explicitly disposition parser failures and unresolved references. Record the collector report's `checkpoint_eligible` value; page exhaustion from a continuation beginning at page 2 or later does not by itself establish checkpoint eligibility.
7. Preserve every observation as dated history; never overwrite or silently relabel older measurements.

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
