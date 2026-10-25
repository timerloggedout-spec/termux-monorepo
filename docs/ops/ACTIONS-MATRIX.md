# Actions Workflows Consolidated Matrix (2026-10-25)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18`  
**Goal:** Zero Failures · 100% Success · Reduced Notification Spam · Feature Preservation · C.A.D.E.  
**Audit Focus:** Skipped / Cancelled / Stale / Timed out / Failure / Action Required / Queued / Neutral — all require attentive validation audits (not silent). Residual run records from job-level `if` still notify; conversion to scheduled pollers is the modular cut.

## Current State (2026-10-25 23:00Z RECON)

**Master tip:** `0bd2bff6105abefa74bb5bdd1967aa3109043726` (chore(ops): record sweep accountability receipt). Success-dominant for dual-gate / promotion / continuous-improve / n8n SHE / context-relationship-audit.

Recent completed runs on tip (sampled):
- **Skipped (high volume residual spam):** lane-events-recorder (dozens per minute on workflow_run cascades), residual agent-throughput-evidence, delphi-*, issue_comment bot cascades (ecc-tools[bot]), concurrency cancels. Job-level `if: conclusion == 'success'` prevents full jobs; run records still notify. Audited as intentional filter/concurrency, **not** silenced failures.
- **Cancelled:** concurrency races on PR paths — expected lag_operational.
- **Success:** dual-gate, Sweep Accountability, Context Relationship Audit, n8n SHE bridge, etc.
- **Failures:** residual device/auth canary class (lag classified notice). Feature-branch only otherwise. Quota/capacity soft non-gate.

**Primary Spam Source:** High-volume `workflow_run` + `issue_comment` cascades. Job-level success filters live → full jobs no longer start on non-success. Residual: every trigger still creates a run record that can notify.

**Next modular cut (active):** Shared scheduled poller (`observer-poller-scheduled.yml`) queries recent successful runs via API every 20 min and emits consolidated evidence. Eliminates per-event run records for observers. Currently expanded to query lane-events-recorder success. High-volume `workflow_run` triggers can be retired once poller is proven dual-gate green.

## Repeated Issues Matrix

| Issue Class | Workflows Affected | Root Cause | Current Handling | Recommended Fix / Consolidation | Status |
|-------------|--------------------|------------|------------------|---------------------------------|--------|
| Cascade Notification Spam | lane-events-recorder, agent-throughput-evidence, delphi-*, issue_comment routers | Broad `workflow_run`/`issue_comment` + job-level if still starts run record | Individual runs + notices | Job-level `if`; **convert residual to scheduled pollers** (shared batched emitter); concurrency per-SHA | **Filters DONE**; poller cut **active** (queries real success) |
| Device / Tunnel (Pinggy / Tailscale) | tailscale-bridge-probe, tunnel-canary, agentic-auth-canary | BLU B160V#1 broken screen; node offline | Probe notice (intentional) | Opaque `tmx-node-primary`; **operational Pinggy/alt MUST be on #1** | Device-side residual (requirement enforced) |
| Quota / Capacity | Vercel, observatory, free-tier | Rate limits | Soft classification, non-gate | Ledger + caching + adaptive backoff + Moneyball | Ongoing |

## Flowchart: Cascade Reduction + Poller Cut + Audit (Mermaid)

```mermaid
flowchart TD
    A[Source Workflow Completes] --> B{Conclusion == success?}
    B -->|No| C[No Observer Trigger<br/>Audit Log Only<br/>No Run Record]
    B -->|Yes| D[Scheduled Poller<br/>queries API every 20m]
    D --> E[Batched Ledger Emit<br/>Concurrency: batch or SHA]
    E --> F[Single Notification / Dashboard]
    C --> G[Zero Skip-Run Spam · Validated Audit]
    F --> G
    H[Residual Device Probe] --> I{Node Online / Heartbeat?}
    I -->|No| J[Notice · Classify Residual<br/>tmx-node-primary]
    I -->|Yes| K[Success]
    L[Pinggy Publisher on #1] --> M[current.json with device_id]
```

## Cadence, Cache & Adaptive Telemetry (3L0 Moneyball)

- **Adaptive-wait:** re-fetch on material SHA delta only.
- **Dynamic telemetry:** this matrix SSOT + ledger. Moneyball selects high-value low-cost actions.
- **Cadence refinement:** high-volume observers moving to 20 min pollers.
- **Cache:** versioned by SHA + Pacific day; never authoritative for live quota. Cache hit never skips current-SHA validation.
- **Modular:** reusable actions + public-obfuscated device ID.
- **Quota planning:** soft-class 403/429; no hard fail on non-gate.

## Device Identification (Public Obfuscation)

- Device #1 (original BLU B160V, broken screen): opaque ID `tmx-node-primary` (**MUST** have operational Pinggy or alternative)
- Device #2: replication only
- Manifests include `device_id` publicly; no secrets/IPs/hardware IDs
- Evidence and credential names (no values) in issue #184

**What was refined this cycle:** Live recon on tip `0bd2bff6`. Residual skip spam quantified. Poller confirmed querying real success runs. Pinggy operational requirement on #1 reaffirmed. Matrix updated for C.A.D.E.

Next: expand poller targets; retire residual workflow_run post dual-gate. Device validation parallel.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
C.A.D.E. Continuously Autonomous Development Environment.
