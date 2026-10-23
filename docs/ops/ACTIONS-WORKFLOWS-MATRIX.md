# Actions Workflows Consolidated Matrix (CADE)

**CADE** = Continuously Autonomous Development Environment.

## What was fixed this branch (honest ledger)

| Item | Before | After |
|------|--------|-------|
| Device ID in public manifest | Missing, then brand/model labels | **Opaque only:** `device_id` = operator token (`tmx-node-primary` default or `tmx-node-<hex>`); **no** make/model/#1/#2 |
| Pinggy publisher | schema v2, no node identity | schema v3 + `device_id` + `device_role` |
| Seed `ops/termux-bridge/current.json` | schema v2, no device fields | **schema v3 + opaque device_id** (status unknown until live publish) |
| n8n SHE bridge parents | 4 parents including Sweep + backfill → skip/cancel storms | **Dual-gate parents only**; concurrency **per SHA** (not per parent name) |
| Skipped/Cancelled policy | Treated as “expected noise” | **Validation-audit required**; notification edge stays failure/timeout only |
| Matrix SSOT | Absent / partial | This file + diagrams + Lead/Lag cadence |
| Help-wanted dashboard concurrency | Manual dispatch storms cancel previous; script fail on status refresh | Documented class; concurrency group preserved; next: continue-on-error on non-critical refresh or script harden |
| Watcher skip-spam | workflow_run trigger always listed runs | **Dispatch-only**; incidents emitted by cadence Lead/Lag */4 |
| Test contract | Asserted old queue:max | Aligned to dispatch-only + cadence emission |
| High-volume observers | Always emit on any conclusion | Conclusion filters (`if: success`) on lane-events-recorder + agent-throughput-evidence (branch) |

**Still open (not fixed until device-side + dual-gate promote):**

- Live Pinggy tunnel on primary node must publish `status: active` (current seed is `unknown`). Alternatives documented (Cloudflare, secondary node, pure Actions).
- Operator must set unique opaque `TERMUX_DEVICE_ID` per physical unit (primary broken screen → secondary or headless).
- Broader workflow fan-out (context audit concurrency, high-volume schedule/workflow_run watchers like lane-events-recorder, agent-throughput-evidence) — next consolidation slices via modular issue-comment / workflow_run router. ~196 workflows total; modular reduction of notification edges is ongoing.
- Residual zero-job startup_failure on cadence-lead-lag when evaluated on push (despite no push trigger); platform observation, not functional failure.
- Tailscale-bridge-probe join failures (e.g. run 39873162670 on tip e9e236b5): OIDC/ephemeral or platform latency; fails red by design when origin unreachable. Device-side Tailscale app reconnect required for tmx-node-primary.

## Opaque device identity (public)

Published JSON may contain **only** opaque tokens:

```json
{
  "device_id": "tmx-node-a7f3c91e",
  "device_role": "bridge"
}
```

- **Not public:** make, model, serial, IMEI, MAC, sequential “#1/#2”, street location.
- **Operator local map** (device-side env / private note): `tmx-node-a7f3c91e` ↔ physical unit. Never commit that map.
- Defaults if unset: `tmx-node-primary`. Second unit: set `TERMUX_DEVICE_ID=tmx-node-secondary` or a random hex suffix.
- Primary BLU B160V#1 (broken screen) and #2 replication use distinct opaque IDs only.

## Skip/cancel spam — how it is reduced (refined)

GitHub still **lists** skipped runs in the Actions tab (platform limitation: `workflow_run` always starts a run). Spam reduction layers (improved):

1. **Fewer triggers** — n8n listens only to dual-gate workflows.
2. **One concurrency group per SHA** — duplicate parents cancel into one lane; successor success = audit PASS.
3. **Job `if:`** — emit only on success/failure; skip is intentional non-emit with documented condition.
4. **Watcher** — now dispatch-only; incidents only for `failure` / `timed_out` via cadence Lead/Lag. Cancelled/skipped = observation only, **no issue spam**.
5. **Lead/Lag index** — correctness > latency; skipped route ≠ model failure (`docs/ops/LEAD-LAG-INDEX.md` + `cadence-lead-lag.yml`). Dynamic adaptive telemetry plane. Cadence */4.
6. **Adaptive cache / WAIT** — re-fetch only on material delta; backoff on no-progress; disjoint work while quiet.
7. **In-process queued/skipped** — concurrency groups + reaper + Lead/Lag classify as operational lag (no notification).
8. **Modular router candidate** — central issue-comment / workflow_run classifier to early-exit unmatched bots and reduce high-volume skipped listings (lane-events-recorder, agent-throughput-evidence, fix-on-failure).
9. **Conclusion filters** — observers emit only on success (implemented on branch for high-volume).

Current master tip `e9e236b5` (2026-10-22T23:45Z window) shows success + intentional skipped/cancelled with one residual probe failure (device reachability).

## Validation audit rule (enforced)

Skipped / Cancelled / Stale / Timed out / Queued / Neutral require **attentive validation audits** (not ignore or silence).

| Outcome | Pass criteria |
|---------|---------------|
| Skipped | Documented condition matched (if: or concurrency) |
| Cancelled | Successor on same concurrency group succeeded |
| Timed out / Stale | Stall class + changed input / reaper |
| Neutral | Explicit non-gate (e.g. Vercel rate-limit #772) |
| Queued (zero-job) | Reaper or concurrency cancel; not silent fail |
| In-process waiting | Adaptive WAIT + Lead/Lag lag_operational; no spam |
| Zero-job startup_failure | Platform evaluation residual; no jobs created; audit as non-functional |
| Probe join failure | Device-side Tailscale reconnect or OIDC tag permission; not silent |

## Repeated-issue classes (historical → current)

| Class | Examples | Status | Superseded / fix |
|-------|----------|--------|------------------|
| Zero-job filename | Ancestor push of incomplete YAML | Historical | Current tip no recurrence; actionlint + surface policy |
| Inventory resilience | v3 queue HTTP 503 / broken pipe | Closed by #1216 | Retry + soft set -e |
| Backfill contradictory URL | Issue node external URL | Closed by #1220 | Prefer canonical |
| n8n fan-out | Sweep + backfill parents | Fixed this branch | Dual-gate only + SHA concurrency |
| Ghost queued | Disabled workflow id still listed | Residual platform | Do not open new ids; reaper observes |
| Dependabot unresolvable | Security update groups | Historical ignore-list | Closed by prior PR |
| Catalog race | Historical correlation --check | Closed by repairs | Current success |
| Skip/cancel spam | High-volume workflow_run | Reduced this branch | Audit + concurrency + Lead/Lag + dispatch-only watcher + conclusion filters; further router next |
| Dashboard deploy script fail | help-wanted-dashboard-deploy status refresh python | Open on master | Concurrency group + continue-on-error candidate; script harden next |
| Zero-job on non-trigger | cadence-lead-lag event:push | Residual | Platform; no functional impact |
| Quota / capacity | observatory 403 (39233561401), peer-review (39234979788), Vercel rate-limit | Historical non-gate | Lead/Lag + adaptive WAIT + cache; no retry storms |
| Tailscale probe join | 39873162670 on e9e236b5 | Residual device | Operator reconnect Tailscale on tmx-node-primary; audit as reachability |

## Cadence / cache / adaptive telemetry (3L0 moneyball equivalent)

| Surface | Role |
|---------|------|
| Lead/Lag Index + cadence-lead-lag.yml | Lead signals vs lag outcomes; latency diagnostic only; GHA-only (no device UI); adaptive snapshot (skip commit if identical); */4 cadence |
| Actions Run Observability | Notification edge policy; capability-gated OTLP; watcher dispatch-only |
| Adaptive WAIT | Re-fetch SHA → runs → jobs; disjoint work while quiet; dynamic backoff |
| Dual-gate | Promote authority only |
| n8n SHE bridge | Optional emit; not correctness |
| Queue reaper | Zero-job / long-queued cleanup |
| Cache | Actions cache + agent-context-store for work context (auth ephemeral); Lead/Lag uses local file cache for delta detection |
| Quota planning | Capacity lag classification; reset-aware cache; no silent failures |

**Lead/Lag + AEF/DOE + Adaptive WAIT** is the moneyball/telemetry plane: measure outcome not activity, adaptive cadence, cache durable context.

## Lifecycle

```mermaid
flowchart TD
  A[Event] --> B{YAML valid?}
  B -->|No| C[Zero-job]
  B -->|Yes| D[Jobs]
  D --> E{Filter / concurrency}
  E -->|Skip| F[Audit skip]
  E -->|Cancel| G[Audit successor success]
  E -->|Run| H[Conclusion]
  H -->|fail/timeout| I[Incident + repair]
  H -->|success| J[Evidence]
  F & G & I & J --> K[Adaptive WAIT → re-fetch SHA]
  L[Lead/Lag cadence */4] --> K
```

## Superseded workflows (notes)

- Merge Promotion Queue v2 → v3 (cron + workflow_run kicks; ghost remains on disabled id).
- High-fanout n8n parents (Sweep Accountability, historical backfill) removed from trigger list.
- Instant-fail path-unfiltered on feature branches classified as noise; dual-gate is authority.
- actions-run-watcher workflow_run trigger superseded by dispatch-only + cadence emission.

## Modular Consolidation Plan (notification reduction)

Target: reduce effective notification edges by combining related schedules into orchestrators and early-exit routers.

| Module | Current workflows (examples) | Proposed | Cadence |
|--------|------------------------------|----------|---------|
| Dual-gate core | repo-gate.yml, termux-smoke.yml | Keep as authority | push + PR |
| Observability | actions-run-watcher (dispatch), cadence-lead-lag | Lead/Lag owns incidents | schedule */4 |
| Bridge/Tunnel | n8n-she-bridge, tunnel-canary, termux-bridge-connect, tailscale-bridge-probe | Keep separate; canary is inventory only; probe fails red on unreachable | */30 or schedule |
| Context graph | context-relationship-*.yml (many) | Single orchestrator with path filters | schedule + workflow_run limited |
| Agent lanes | agent-*-ops, quality, throughput | Group under agent-continuous-ops | schedule staggered |
| Help-wanted | help-wanted-* + dashboard-deploy | Concurrency group + if: on non-critical; script harden | dispatch + path |
| Event router | lane-events-recorder, agent-throughput-evidence, fix-on-failure, many issue_comment | Central classifier early-exit unmatched + conclusion filters | workflow_run / issue_comment |

**Spam reduction levers already applied:**
- n8n parents limited to dual-gate.
- Concurrency per SHA.
- Watcher dispatch-only (no auto skip-run listing).
- Lead/Lag classifies skipped as lag_operational (no incident).
- In-process queued classified as operational lag via adaptive WAIT.
- Cadence */4 reduces schedule volume.
- Conclusion filters on high-volume observers (branch).

Next slice: modular event router for high-volume workflow_run / issue_comment to cut skipped listings further. Audit top schedule workflows by run volume. Harden help-wanted status refresh. Device-side Tailscale/Pinggy publish.

## Additional flowchart: skip/cancel audit

```mermaid
flowchart TD
  Run[Workflow run starts] --> Conc{Concurrency cancel?}
  Conc -->|Yes| Succ{Successor success?}
  Succ -->|Yes| AuditOK[Audit PASS: cancelled by design]
  Succ -->|No| Investigate[Check logs / re-fetch]
  Conc -->|No| Job{Job if: matched?}
  Job -->|Skip| Cond{Documented condition?}
  Cond -->|Yes| AuditOK2[Audit PASS: intentional skip]
  Cond -->|No| Fix[Add if: or remove trigger]
  Job -->|Run| Conc2{Conclusion}
  Conc2 -->|success/failure| Evidence
  Conc2 -->|timeout| Stall class
```

## Device #1 status (opaque)

- Public: device_id=`tmx-node-primary` in seed manifest.
- Status: unknown (no live publish this session). Pinggy or alternative must be operational; publish status:active when verified.
- Requirement: operator sets unique TERMUX_DEVICE_ID on physical units; publisher job updates status to active when tunnel verified.
- Alternatives: Cloudflare tunnel, secondary node, pure Actions runners for non-device work. Redundant paths documented for broken-screen primary.
- Tailscale probe residual: join failure on latest schedule; reconnect app on device.

Observed this session: 2026-10-22T23:45Z (master tip e9e236b5 green-dominant; residual probe failure device-reachability; high-volume skipped audited as intentional; quota capacity non-gate)
Agent-Identity: Grok (Administrator)

## Continuation (2026-10-22T23:45Z)

- Master tip `e9e236b5a0ee69a7c3c31fe60b9290d66107dc59` (help-wanted live status refresh): recent completed runs success or skipped/cancelled (intentional concurrency/filter). Residual failure: tailscale-bridge-probe run 39873162670 (join step failure at OIDC/ephemeral).
- Specific notification runs from prior: 39233561401 repository observatory conclusion=failure (historical capacity 403, non-gate); 39234979788 peer-review-orchestrator failure on quota-registry branch (capacity/non-gate). Current tip green-dominant.
- High-volume skipped from workflow_run triggers remain audit-only; modular central router + conclusion filters proposed/implemented on branch to early-exit unmatched events and further cut notification surface.
- Quota messages and capacity lag addressed via Lead/Lag classification, adaptive WAIT, reset-aware caching; no silent failures or retry storms.
- Pinggy or alternative operational requirement on device #1 preserved with public-obfuscated device_id=`tmx-node-primary`; live status:active awaits device-side publish. Device #2 replication distinct. Tailscale probe is the current reachability signal.
- Cadence */4, cache dynamic adaptive telemetry, concurrency groups refined and retained. C.A.D.E. continuous improvement.
- Next: implement modular event router slice; confirm dual-gate on updated SHA; operator device tunnel + Tailscale reconnect; promote branch once gates green.

Agent-Identity: Grok (Administrator)

## Prior continuations retained (2026-10-20 / 2026-10-21)

(See historical sections above for PR #1292 dual-gate evidence, watcher dispatch-only merge path, Vercel non-gate classification.)

## GitLab reconciliation lane — current integration proposal (2026-10-19)

- **Implementation PR:** [#1288](https://github.com/timerloggedout-spec/termux-monorepo/pull/1288)
- **Workflow:** `.github/workflows/gitlab-governed-reconciliation.yml`
- **Contract:** `docs/ops/GITHUB-GITLAB-GOVERNED-RECONCILIATION.md`
- **Canonical comparison:** GitHub `master` SHA ↔ selected GitLab branch SHA; never PR head ↔ GitLab master.
- **Authentication:** `GITLAB_TOKEN` for GitLab fetch; default `GITHUB_TOKEN` for bounded GitHub writes. Missing GitLab credentials fail closed. The default token intentionally suppresses recursive CI fan-out for unreviewed external code.
- **Promotion:** normal PR checks and review; no force-push, no GitLab writes, no auto-merge.
- **State model:** `aligned`, `gitlab-behind`, `gitlab-ahead`, `diverged`; merge conflicts stop for manual reconciliation.
- **Status:** proposed/under validation. Do not mark operational until an Actions run proves the no-op or PR-publication effect. The old #311 remains the historical design reference until the replacement is accepted.
