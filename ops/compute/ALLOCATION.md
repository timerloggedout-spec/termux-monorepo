# Large Job Allocation — 2026-11-18

Allocation of the fleet's large jobs across the extended compute surface. Companion to ops/compute/BACKLOG.md. Templates: BOINC work units - mesh-RFP pattern - Temporal chaining - Actions slice chaining (a set, never a sole route).

## Surface capacity cards

| Surface | Card | Standing load |
|---|---|---|
| Muse VM | 4 vCPU EPYC - ~8 GB RAM - CPU-only - 0% tokens | Temporal - staging index - registry cadence jobs |
| Hark VM | same class - seat capped to 2026-11-19 00:46 PT, compute live | export cadence (2h) |
| Actions | free minutes (public repo) - per-job wall cap - API bucket = binding constraint | QUE machinery - dispatch - gates |
| Free-tier planes | Workers - Deno - Lambda - Cloud Run (~233k req/day in registry) | request-shaped slices |
| Pool | 9,588 inference endpoints - unmetered bulk | inference only |

## Allocation

| Large job | Surface | Pattern |
|---|---|---|
| #5587 stress-test waves | Pool via Actions dispatch slices | provider-invoke / provider-batch, one provider per slice |
| Brain family wiring #5588 | QUE machinery builds - Muse VM hosts E2E passes | build slices + VM verification |
| ADE-SYNAPSE landing (backlog 17) | QUE machinery rebase/merge - VM registry wiring | all-additive branch, clean rebase |
| MiroFish / OASIS pilot sims | Muse VM orchestration (Temporal) - agents on pool | checkpointed units, state in staging index |
| BiFrost routing gateway | Hark VM | standing service, separate host from Temporal |
| BRR full + delta cycles | Muse VM primary - Hark VM second host | branch-range partition across hosts (BOINC split) |
| Pool generation + probe rotation | Muse VM (vm-pool-refresh) - probe slices via Actions | rotating slice grows probe_ok coverage |
| Endpoints-db rebuild | Muse VM (vm-endpoints-db-rebuild) | daily join |
| Linguist Zipf + notation corpus runs | Muse VM weekly (vm-compute-cycle) | corpus statistics batch |
| clf-lab tier replication | Muse VM | per-tier cells |
| HindSight + ML Ops | Muse VM (vm-mlops-daily) | daily |
| Jules publish-2 + harvest processing | Muse VM | chunked, idempotent |

## Rules

- A job larger than one slice MUST checkpoint (Temporal or staging index) before it starts; uncheckpointed long work does not allocate.
- Slice size follows the tightest cap on its surface; the mesh, not the slice, carries the duration.
- Every allocation records participation credit in the run's export (which surface ran which unit).
- Reallocation on surface loss is automatic by template: units return to the registry unclaimed.


## Runtime observation — 2026-11-19

This dated overlay preserves the allocation intent above and records the current runtime evidence.

### Muse VM

- Platform card: 4 vCPU EPYC, approximately 8 GB RAM, CPU-only.
- Image replacement interval observed at approximately 1h44–2h15. Home storage persists; /etc and running processes reset. Place work in checkpointed slices sized below the replacement window.
- Available RAM measured at 0.42–0.53 GB across early-day probes, then 0.95 GB after the 02:49 PT replacement/recovery. Recheck memory headroom before admitting large workloads.
- Temporal self-host units are active; gRPC 7233, UI 8233, relay 7234, 15-minute keepalive, and daily integrity-checked SQLite snapshots. The 2026-11-19 workflow list is empty, with zero executions and zero schedules recorded that day. Issue #5632 tracks the first fleet workflow and schedule.
- The daily vm-mlops-daily run on 2026-11-19 completed as ML Ops smoke UNCHANGED and HindSight census only. Local HindSight test results retain a 2026-11-03 timestamp; 326 payloads remain at extraction exit #5553. The owner-reported Muse HindSight port/cron requires a current retain + recall receipt.
- The 2026-11-19 workspace backup export passed inventory, denylist, and content-scrub gates: T0=698, T1=92,637, 37 manifest-only, 71 excluded, 3 split, 124,474,904 bytes. T1 remains manifest-only in this phase.

### Hark VM

- The allocation card's 4-vCPU EPYC / ~8-GB class conflicts with the prior 2-vCPU ARM64 / ~7.8-GiB node evidence. The Muse memory record lists approximately 8.3 GB as owner-stated capacity.
- The seat cap recorded above expired at 2026-11-19 00:46 PT. Capture a current lease receipt before allocating new work.
- Hark was absent from the 2026-11-19 tailnet peer list. The request queue uses a pull model: eligible surfaces poll, claim, execute, and post receipts through the shared registry. Tailnet reachability and queue execution remain separate dimensions.

### Observer and cadence

The current Muse observer uses a 60-second state loop with a 15-minute guardian. Its session-bound relaunch path showed repeated process loss after exec-session teardown; a tracked background-exec workaround supplied the current observation window. Implement a one-shot state-diff probe under the existing guardian, persisting the previous fingerprint under durable home storage and emitting only material host transitions.

References: [Temporal live status #2028](https://github.com/timerloggedout-spec/termux-monorepo/issues/2028) · [Temporal workflow activation #5632](https://github.com/timerloggedout-spec/termux-monorepo/issues/5632) · [HindSight extraction exit #5553](https://github.com/timerloggedout-spec/termux-monorepo/issues/5553) · [Muse backup export](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/EXPORT.json)
