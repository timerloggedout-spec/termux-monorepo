# Compute Backlog Registry — consolidated 2026-11-18

One registry for the fleet's compute backlog, gathered from the scattered surfaces {QUE filings - compute-jobs dirs - goal workspaces - RFPs}. VM capacity card: 4 vCPU - ~8 GB RAM - CPU-only - <=2 GB RAM/job - 0% tokens for VM-local work. Intake route: QUE -> QDesk -> VM seat.

| # | Item | Home | State 2026-11-18 | Route |
|---|------|------|------------------|-------|
| 1 | Wired-89 stress test + pool participation vs 100% | QUE #5587 | First invoke wave fired 2026-11-18 (8 providers) - fraction unestablished | provider-invoke / provider-batch |
| 2 | Brain 21-family wiring + E2E receipt | QUE #5588 | Kernel landed (PR #5525) - wiring claimed, build failed on dead arms | QUE machinery + VM host |
| 3 | Rate-limit consolidation build | QUE #5309 | Claimed + escalated - 4 build attempts failed - route = pool selection | DoE pool selection pipeline |
| 4 | Pool alias reconciliation (3,443 unmapped endpoints-db rows) | ops/quota/endpoints-db.csv | Measured 2026-11-18 | vm-pool-refresh + vm-endpoints-db-rebuild crons |
| 5 | BRR x commits x regressions x comment-graph join | QUE #5640 | Filed 2026-11-18, claim-class stamped | vm-brr-delta cron + machinery |
| 6 | BRR delta cycles | BRR v2 registry (store) | v2 landed 2026-11-17 (4,103 branches) | vm-brr-delta cron |
| 7 | DreamBeans mapping fold-in | QUE #5588 input | Map complete (200) at compute-jobs/2026-11-17-dreambeans-map | VM read + register |
| 8 | Jules harvest publish-2 verification | compute-jobs/2026-11-17-jules-harvest | Collection 417/417 - publish unverified | VM |
| 9 | PR #5518 AWS Emulator pull-forward | QUE #5639 | Filed - admitted - queued | QUE machinery |
| 10 | D5 Understudy build | QUE #5580 | STALLED (lease-release stall-events) - wall Nov 19 12:00 PT | QUE machinery |
| 11 | Local small-model participants (model-layer matching) | QUE #5549 stamp c.6985076966 | Design stamped - placement unbuilt | VM local inference |
| 12 | Ranking step-2 cohort (v1 binding + L-shadow) | QUE #5546 | Unblocked - sequenced after #5587 | DoE scoring |
| 13 | clf-lab tier replication | PR #5609 | Tier1 replicated on Muse VM 2026-11-18 (12/12 cells) - further tiers gated on token-scope answer | VM |
| 14 | ML Ops daily + HindSight census | vm-mlops-daily cron | Running daily | VM |
| 15 | Mesh probe + availability census | #5549 | Probe-watch cron hourly - schedule starvation on the Actions leg | VM cron + Actions |

| 16 | BOINC-template adoption: registry cadence jobs as cross-surface work units | refTemplates boinc-distributed-compute-template | Template of record 2026-11-18 - adoption unbuilt | VM + Hark VM hosts |

| 17 | ADE-SYNAPSE brain architecture integration: rebase + land the diverged package, wire the brain-region registry into the #5588 family wiring | branch feat/ade-synapse-brain-architecture (head 67a6435129ba; owner-quoted 240812da5d59 in history) | DIVERGED ahead 22 / behind 167 - 15 files all-additive - status proposed_architecture - unlanded | QUE machinery |

Rules: a backlog item leaves this registry only with done-evidence (receipt + landed state). New compute work registers here at intake.
