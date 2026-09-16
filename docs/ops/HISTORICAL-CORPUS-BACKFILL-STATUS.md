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

## Current next action

**Resume at page `2`, but first replace the stale `master-staging` continuation target with a fresh current-master lineage.** The exact historical collection cannot be executed from this conversation because the available GitHub connector exposes workflow inspection/write primitives but not a workflow-dispatch operation. The control-plane change should therefore be made before the next operator dispatch rather than pretending a run occurred.
