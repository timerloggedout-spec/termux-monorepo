## Tribute outcome SLO: **FAIL** (30d window)

real merges **0** · stake-only merges **1** (weight 0) · closed-unmerged **25** · real merge rate **0.0** · open now **7** · days since real merge **33.5**

- FAIL `zero_real_merges`: 0 real foreign merges in the last 30d
- FAIL `real_merge_rate_below`: real merge rate 0.0% < 10% over 26 decided PRs (30d)
- FAIL `real_merge_drought`: last real merge 33.5d ago (> 21d)
- WARN `stake_only_merges_weight_0`: 1 stake-only merges in 30d counted at weight 0
- WARN `closed_unmerged`: 25 PRs closed without merge in 30d (counted as failures)

System 1 threads 208: yielded 62 · retired 61 · dropped 3 · placeholder merges 0

| window | real | stake (w0) | self (excl) | closed-unmerged | rate |
|---|---|---|---|---|---|
| 7d | 0 | 0 | 0 | 0 | None |
| 14d | 0 | 0 | 0 | 0 | None |
| 30d | 0 | 1 | 0 | 25 | 0.0 |
| 90d | 2 | 14 | 0 | 98 | 0.0175 |
