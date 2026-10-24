# Actions Workflows Consolidated Matrix (2026-10-23 evening)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18`  
**Goal:** Zero Failures · 100% Success · Reduced Notification Spam · Feature Preservation · C.A.D.E.  
**Audit Focus:** Skipped / Cancelled / Stale / Timed out / Failure / Action Required / Queued / Neutral — all require attentive validation audits (not silent). Residual run records from job-level `if` still notify; next cut moves high-volume observers to scheduled pollers.

## Current State (2026-10-23 RECON)

**Master tip:** recent success-dominant (sweep receipts, promotion queue, continuous-improve, etc.).

Recent completed runs on tip (success-dominant):
- **Success:** Merge Promotion Queue v3, Continuous CI Sweep, continuous-improve, Issue Observatory, context backfills, hygiene-sweep, DeepCLI, lane-events on success, etc.
- **Skipped:** intentional on job-level `if: conclusion == 'success'` (lane-events-recorder, agent-throughput-evidence, etc.) — audited as filter/concurrency, not silenced failures. **Residual:** job-level if still creates a workflow run record (conclusion=skipped) which can notify. Further reduction requires fewer triggers, shared batched observer, or conversion to schedule-only pollers.
- **Cancelled:** concurrency races expected (lag_operational). Suppress pure cancel notices where possible; validate they are not masking failures.
- **Failures:** residual device probes (Tailscale OIDC 403 on tmx-node-primary) classified honest RED when unreachable. Not YAML. Quota/capacity soft non-gate (Vercel, observatory, GitLab recon).

**Primary Spam Source:** High-volume `workflow_run` cascades — **mitigated on this branch** but residual run-start notifications remain.
- Filters live: jobs only run on `conclusion == 'success'`. Non-success no longer start observer jobs → spam reduced while preserving success ledger.
- Modular `issue-comment-router` early-classifies bot comments.
- Next: shared emitter + concurrency-per-SHA + convert residual high-volume observers to batched scheduled pollers (eliminates run records for non-success).

**Historical Pattern:** Cancelled/skipped = concurrency or intentional filters (validated). True failures = quota/capacity (soft, non-gate) or device (residual). Silenced failures require explicit audit trail + artifact.

## Repeated Issues Matrix

| Issue Class | Workflows Affected | Root Cause | Current Handling | Recommended Fix / Consolidation | Status |
|-------------|--------------------|------------|------------------|---------------------------------|--------|
| Cascade Notification Spam | lane-events-recorder, agent-throughput-evidence, context-relationship-audit, delphi-* | Broad `workflow_run` on all conclusions + job-level if still starts run | Individual runs + notices | Job-level `if: conclusion == 'success'`; batch; narrow lists; shared observer + concurrency per-SHA; **convert residual to schedule-only pollers** | **Implemented** (filters); residual run records — next cut planned |
| Concurrency Cancel | help-wanted-*, sweep, others | Rapid triggers | cancel-in-progress | Granular groups (SHA); or false + queue; orchestrator | Ongoing |
| Watcher Skip | actions-run-watcher | Pre-dispatch-only | Dispatch-only | Fixed; residual aging | Fixed |
| Device / Tunnel (Pinggy / Tailscale) | tailscale-bridge-probe, device tests, bridges | BLU B160V#1 broken screen; node offline / OIDC 403 trust | Probe fails RED (intentional) | Opaque `tmx-node-primary`; **operational Pinggy/alt MUST be on #1**; evidence #184; soft-class residual | Device-side residual (requirement enforced) |
| Queue / Stale | actions-queue-reaper, Merge Promotion Queue | Zero-job holds / ghosts | Reaper + v3 | Expand adaptive threshold; do not open new workflow IDs | Active |
| Quota / Capacity | Vercel, observatory, quota-registry, GitLab recon | Rate limits, API 403/429 | Soft classification, non-gate | Ledger + caching + path filters + adaptive backoff + Lead/Lag telemetry + Moneyball prioritization | Ongoing |
| Silenced Failures | Historical | Cancel without diagnosis | Policy | Explicit artifact + issue on non-intentional | Policy |

## Superseded / Combined Workflows

- Multiple observers → single batched ledger emitter with conclusion filter (partial on branch) → further to scheduled poller
- Help-wanted-* → matrix orchestrator where possible
- Device tests → consolidated matrix with `device_id` injection (`tmx-node-primary`)
- Ghosts (e.g. 37655538554 on disabled workflow) remain; do not spawn new IDs

## Flowchart: Cascade Reduction + Audit (Mermaid)

```mermaid
flowchart TD
    A[Workflow Completes] --> B{Conclusion == success?}
    B -->|No| C[Skip Observer Job<br/>Audit Log Only<br/>Run record may still notify<br/>→ Next: schedule poller]
    B -->|Yes| D[Emit to Shared Ledger<br/>or Modular Router]
    D --> E[Concurrency Group: SHA or Batch]
    E --> F[Single Notification / Dashboard Update]
    C --> G[No Full Job Spam · Validated Audit]
    F --> G
    H[Residual Device Probe] --> I{Node Online / OIDC Trust?}
    I -->|No (403/offline)| J[Fail RED · Classify Residual<br/>tmx-node-primary]
    I -->|Yes| K[Success · Manifest Update]
    L[Pinggy Publisher on #1] --> M[current.json with device_id]
```

## Cadence, Cache & Adaptive Telemetry (3L0 Moneyball)

- **Adaptive-wait:** continue disjoint work during in_progress; re-fetch on material SHA delta only.
- **Dynamic telemetry:** action-effectiveness-ledger + this matrix SSOT for prioritization (Lead/Lag snapshots). Moneyball selects high-value low-cost actions.
- **Cadence refinement:** `*/4` and workflow_run kicks retained for critical; conclusion filters + modular router cut cascade volume. **Further:** convert residual high-volume observers to scheduled pollers (eliminates skip-run notifications). Batch where possible.
- **Cache:** actions/cache on lockfiles; path filters on push; dynamic adaptive for quota planning. Cache hit never skips current-SHA validation. Prefer sparse checkout.
- **Modular:** reusable actions for status emit + public-obfuscated device ID. Issue-comment-router absorbs bot spam early.
- **Quota planning:** soft-class 403/429; ledger records; no hard fail on non-gate (Vercel etc.). Act before exhaustion via adaptive backoff + caching + Lead/Lag Moneyball.

## Device Identification (Public Obfuscation)

- Device #1 (original BLU B160V, broken screen): opaque ID `tmx-node-primary` (**MUST** have operational Pinggy or alternative — scripts enforce publisher)
- Device #2: replication only; do not overwrite origin bridge
- Manifests include `device_id` publicly; no secrets/IPs/hardware IDs
- Probe publishes `ops/termux-bridge/tailscale.json` (additive); current.json owned by device Pinggy publisher
- Scripts: `scripts/termux/publish-pinggy-endpoint.sh`, `diagnose-pinggy-publisher.sh`, `install-pinggy-publisher-job.sh`
- Evidence and credential names (no values) in issue #184

## Next Actions

1. ~~Implement conclusion filters on high-volume observers~~ **DONE on branch**
2. Promote continued refinements (this update) once dual-gate green
3. Device-side Pinggy/Tailscale validation on `tmx-node-primary` (operator; fix OIDC trust credentials if desired) — **requirement: operational on #1**
4. Convert residual high-volume observers to scheduled pollers / shared batched emitter to eliminate skip-run notifications
5. Expand quota soft-class + adaptive cache/telemetry in ledger
6. C.A.D.E. continuous modular consolidation + adaptive cadence / cache / telemetry

**Implements:** Actions matrix upgrade for zero-failure FA-ADE / C.A.D.E. Notification spam reduction via cascade filters + planned poller conversion. Attentive validation audits for all non-success. Residual device probe classified (not silenced). Pinggy operational requirement on device #1 reinforced with public obfuscation.

Agent-Identity: Grok (Administrator)

## Continuation RECON (2026-10-23 evening)

Master tip success-dominant. High-volume skipped on master (pre-full-promote); filters on this branch suppress full observer jobs on non-success. Residual device probe classified. Quota soft. **Pinggy/alt operational requirement on #1 (`tmx-node-primary`) enforced in matrix.** Notification spam from Skipped/Cancelled reduced but residual run records remain — next modular cut (scheduled pollers) required.

**What was refined this cycle:**
- Explicit residual skip-run notification note + planned conversion to scheduled pollers
- Quota/cache/telemetry adaptive planning strengthened (Moneyball)
- Device #1 Pinggy scripts + obfuscation reaffirmed as MUST
- Next actions updated for poller conversion + residual cut

Next: dual-gate on head → promote. Device validation parallel. Disjoint: matrix SSOT refined for C.A.D.E.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
