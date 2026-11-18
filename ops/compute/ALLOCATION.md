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
