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

GitHub compare previously classified `master...master-staging` as **diverged**, with staging 50 commits ahead and 455 behind current master. Therefore the larger corpus is useful evidence but **must not be promoted wholesale**.

## Control-plane finding

The historical collector was previously operator-dispatched and resumed against `master-staging`. That was an automation defect for a system whose canonical source is `master`.

The successor workflow is now implemented on the collaboration branch:

- scheduled + explicit dispatch;
- current `master` checkout;
- `next_start_page` read from the canonical manifest;
- one bounded continuation window per run;
- page-advance validation;
- manifest/summary hashes emitted in run evidence;
- direct canonical delta commit to `master` after validation;
- concurrency lock on the canonical writer;
- no `master-staging` read/promotion path.

**Runtime status:** the successor workflow has been **COMMITTED**, but no new backfill Actions run is claimed by this document. `next_start_page = 2` remains the latest observed corpus state until an actual run proves otherwise.

## Continuation model

```text
canonical master SHA
      |
      +--> read manifest.next_start_page
                |
                +--> bounded page N
                |
                +--> validate advancement + hashes
                |
                +--> commit corpus delta to master
                |
                +--> next scheduled continuation
```

Do not:

- merge the stale `master-staging` branch wholesale;
- infer completeness from node/edge growth;
- turn missing history into zeroes;
- overwrite prior evidence;
- skip manifest/checkpoint validation between windows.

## Promotion/validation invariants

A bounded continuation is valid only when:

1. source SHA/ref is recorded;
2. start and next pages are recorded;
3. manifest/input/schema hashes are preserved;
4. corpus reconciliation/metadata validation passes;
5. the diff is limited to the intended corpus delta and required metadata;
6. the resulting commit is based on current master;
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

## Current state

**Canonical evidence:** partial, next page `2`.  
**Automation:** successor implemented on the integration branch.  
**Execution:** not yet observed.  
**Completion:** not established.
