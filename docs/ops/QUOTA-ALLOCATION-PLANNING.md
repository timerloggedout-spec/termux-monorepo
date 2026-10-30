# Advanced quota allocation — planning (lead: Quota Specialist lane)

Owner order 2026-10-29: this lane leads planning in advanced allocation.
Model of record stays Pool × Focus × % (issue #1884, SSOT
`ops/quota/allocations.json`). This doc is the planning layer above it:
how pools are classed, paced, reserved, harvested, and re-split.

## 1. Pool taxonomy (registry: 155 records, 52 pools, 0 excluded)

| Class | Definition | Count (2026-10-29) | Planning treatment |
|---|---|---|---|
| A — documented, numeric | registry limit is a number from a primary source | 94 records | paced spend (§3), safety factor per record |
| B — documented, status-only | limit null, vendor publishes state/counter semantics | part of 61 null | state-driven: act on readings (ok/watch/exhausted), no numeric pacing |
| C — not established | no published limit (incl. 43 g4f web wrappers) | part of 61 null | inference-only (usage-log evidence on record); unmetered-until-429; experiment label; never a planned entitlement |
| M — meta-pool | shared bucket consumed by the fleet's own operations | 1 (GitHub API core, PAT) | arbitration (§4); the binding constraint in practice |

Focus ladder (standing, #1884): Winning ≈100% standing on every
non-excluded pool → repo-development leftover-only → research
leftover-only → BOINC leftover-only, GitHub-provider pools only.
Codespaces excluded-interim, reserve 100 explicit.

## 2. Horizons

- **H0 — intraday / hourly:** meta-pool PAT core (rolling hourly
  replenishment, 5000/hr); probe and collector pacing live here.
- **Daily:** UTC-midnight resets (OpenRouter free, most free tiers,
  g4f established dailies: Airforce 1,000/day, KiloCode 200/hr/IP,
  GeminiCLI 1,000/day…).
- **Rolling 24h:** Vercel deployments 100/day (API undercounts
  enforcement ≥13 — plan against 87, not 100).
- **Monthly:** billing-month pools (Render minutes, Neon CU-hours,
  ElevenLabs credits, Pinecone units, GitHub Copilot premium requests).
- **Event horizon:** challenge slate deadlines; Gantt plan end = D4
  close 2026-12-04. Winning sub-focus narrows as deadlines approach (§5).

## 3. Pacing rule (extends the registry's own planned_use rule)

Per class-A pool, per window:

- Budget for the window = `safety × limit` (safety on the record,
  default 0.9; 0.85 data pools; 0.8 tight pools).
- Routing multiplier = remaining-budget fraction ÷ remaining-time
  fraction, capped at 2, 0 when exhausted, 1.0 when no live reading
  (registry rule, unchanged).
- Burn-rate input = readings snapshots + collector cost accounting;
  a pool with no reading is paced at 1.0 and flagged to the gaps lane —
  observability before optimization.

## 4. Meta-pool arbitration (GitHub API core — the proven wall)

Evidence: 0-remaining walls 2026-10-28 23:41Z (multi-lane polling)
and 2026-10-29 ~18:32 PT (reset 01:42Z); storm burn 2026-10-29
(delphi-gate 143 runs/25min → ~750-call collects, fixed by PR #2341's
15-min freshness gate).

Rules:
1. **Derived reserve** (QAC-007, cadence lane): reserve =
   10% of limit (= 500 @ 5000) unless a collector-cost forecast
   demands more; derived, never a magic constant.
2. **Priority classes** when remaining < reserve: (1) gates / merge
   operations, (2) readings & probes, (3) scheduled collectors,
   (4) speculative cadence (reviewer-metrics collects, availability
   probes) — classes 3–4 defer until replenishment.
3. **Freshness gates everywhere** (QAC-008 proposal): every
   workflow_run collector on the user token gets a freshness gate +
   single-flight concurrency; gate interval derived from collect cost.
4. **Polling discipline:** batch reads, head-SHA check-runs over list
   scans, no per-step gate polling (standing fleet lesson).

## 5. Stranded-quota harvest + re-split triggers

Leftover-only focuses may draw only quota Winning **cannot consume
before expiry**. At each cadence tick, per class-A/B pool:

`stranded = remaining − forecast(Winning consumption to window end)`

- stranded > 0 → release to repo-dev, then research, then BOINC
  (GitHub pools only), in ladder order, for that window only.
- stranded ≤ 0 → leftover focuses stay at 0 for that pool/window.

Re-split triggers (any one forces an out-of-cycle re-plan PR citing
#1884): readings state change (exhausted / cap-tripped / recovered);
pool added or removed (registry delta); quota-wall event on the
meta-pool; T-72h before a challenge deadline (Winning sub-focus
narrows to the imminent event's pools); owner focus change.

## 6. The automated revision-adaptive process (owner requirement)

Planning is **not** a manual ritual — it runs as repo automation
(VM = sandbox only; always-on work lives in GitHub Workflows):

- **Engine:** `scripts/quota_allocation_planner.py` (stdlib only).
  Inputs: registry + allocations SSOT + readings snapshot
  (`docs/ops/generated/quota-status.json`) + challenge countdowns
  when present. Output: `ops/quota/allocation-plan.json`
  (`quota-allocation-plan/v1`) — per pool: class, window state,
  pacing multiplier (§3), stranded estimate (§5), release target,
  triggers fired. A pool with no numeric reading gets
  `stranded: null` (NOT ESTABLISHED) — the process never invents a
  release.
- **Runner:** `.github/workflows/quota-allocation-planner.yml` —
  weekly schedule + `workflow_dispatch` + push on `ops/quota/**`
  and the readings path. It runs the planner + its tests and opens
  a **refresh-PR** (branch `quota/allocation-plan-refresh`, never a
  direct commit) only when the plan changed.
- **Adaptivity:** the plan is recomputed from live inputs every
  run — readings state changes, registry deltas, and deadline
  proximity (T-72h trigger) change the output without any human
  re-planning. Re-split *proposals* for `allocations.json` ride the
  same refresh-PR when a §5 trigger fires, citing #1884; the SSOT
  itself changes only through that PR's gates.
- **Per-window close:** burn-down vs plan (Gantt plan-vs-actual in
  the allocations feed) reviewed against the Visualization lane's
  burn-down + replenishment-stamp graphs.

## 7. Lane roles

| Lane | Role in allocation |
|---|---|
| Quota Specialist (lead) | this plan; re-split proposals; pool taxonomy; reconcile |
| Quota convergence | allocations table execution (validate/feed/gantt), readings promotion |
| Cadence optimizer | pacing levers (QAC-007 reserve, QAC-008 gates), dispatch-event timeline |
| Quota gaps | burn observability gaps vs 155 (readings coverage), gaps ledger refresh |
| Visualization | burn-down graphs + replenishment stamps (for Web Dev surfaces) |
| Challenge entries | demand signal: countdown block = Winning focus demand |

## 8. Open items

- 155-row readings snapshot landing confirmation (convergence lane).
- Collector cost accounting per workflow (feeds §4 reserve forecast).
- Vercel rolling-window pacing (referred to Vercel Specialist with
  the derived-reserve pattern, cadence lane 2026-10-29).
