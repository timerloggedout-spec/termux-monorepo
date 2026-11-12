## Tribute outcome SLO: **FAIL** (30d window)

real merges **2** · stake-only merges **5** (weight 0) · closed-unmerged **51** · real merge rate **0.0345** · open now **8** · days since real merge **23.8**

- FAIL `real_merge_rate_below`: real merge rate 3.5% < 10% over 58 decided PRs (30d)
- FAIL `real_merge_drought`: last real merge 23.8d ago (> 21d)
- WARN `stake_only_merges_weight_0`: 5 stake-only merges in 30d counted at weight 0
- WARN `closed_unmerged`: 51 PRs closed without merge in 30d (counted as failures)

System 1 threads 208: yielded 62 · retired 61 · dropped 3 · placeholder merges 0

| window | real | stake (w0) | self (excl) | closed-unmerged | rate |
|---|---|---|---|---|---|
| 7d | 0 | 0 | 0 | 2 | 0.0 |
| 14d | 0 | 0 | 0 | 2 | 0.0 |
| 30d | 2 | 5 | 0 | 51 | 0.0345 |
| 90d | 2 | 14 | 4 | 99 | 0.0174 |
