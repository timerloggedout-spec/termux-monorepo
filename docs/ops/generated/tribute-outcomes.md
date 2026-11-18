## Tribute outcome SLO: **FAIL** (30d window)

real merges **1** · stake-only merges **2** (weight 0) · closed-unmerged **35** · real merge rate **0.0263** · open now **7** · days since real merge **30.0**

- FAIL `real_merge_rate_below`: real merge rate 2.6% < 10% over 38 decided PRs (30d)
- FAIL `real_merge_drought`: last real merge 30.0d ago (> 21d)
- WARN `stake_only_merges_weight_0`: 2 stake-only merges in 30d counted at weight 0
- WARN `closed_unmerged`: 35 PRs closed without merge in 30d (counted as failures)

System 1 threads 208: yielded 62 · retired 61 · dropped 3 · placeholder merges 0

| window | real | stake (w0) | self (excl) | closed-unmerged | rate |
|---|---|---|---|---|---|
| 7d | 0 | 0 | 0 | 0 | None |
| 14d | 0 | 0 | 0 | 1 | 0.0 |
| 30d | 1 | 2 | 0 | 35 | 0.0263 |
| 90d | 2 | 14 | 4 | 98 | 0.0175 |
