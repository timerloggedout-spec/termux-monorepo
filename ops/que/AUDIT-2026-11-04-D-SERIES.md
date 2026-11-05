# QUE-docs audit — D-series fix order (owner order 2026-11-04 20:25 PT)

Packet of record: D1 diagnostics escalation @ manager seat. Closure receipts collect here; per-defect, evidence-bound. Custody folds: cadence #4977/#4979.

## D-h — dispatch-hand gap (claimed, trigger never instantiated) — FIRST
- State: TAKEN at QUE → #4977 Fix 5 (comment 6649638623): watchdog scans dispatch-claimed filings for route evidence (run/branch/PR) ≤15 min → aging; 30 min → escalate producer + Desk.
- Evidence of the defect: #4965/#4966 claimed 2026-11-05T03:52Z, ∅ branch ∧ ∅ PR @04:20Z; live queue read (feeds @04:21:03Z) = 12 active, tier 3 0/0 — stall = producer-hand, ¬ queue starvation.
- Closure: OPEN (build routed Desk QUE → Swarm under #4977).

## D-c — admission collection (live pagination under shared token)
- State: root read of record (cadence, swarm-admission.yml @master firsthand) → #4979: evaluator reads the collector picture (freshness-gated) instead of re-collecting; fallback names failed page + error class; non-flow tiers never defer on picture failure. Token leg (github.token 1,000/h exhaustion → Swarm App mint, own 5,000/h) folded into #4977 (comment 6649237311).
- Closure: OPEN (#4979 build routed Desk QUE → Swarm). Desk record stands: admission collection leg unresolved until an ADMITTED re-eval lands.

## D-f — collector starvation (que-feed-collect */10 cron; success gaps 4–5.5h; ∅ error signal)
- State: root = GitHub schedule starvation under run churn (executed runs ∀ SUCCESS; scheduled cycles never instantiated). Interim heal = manual workflow_dispatch from the cadence seat (runs 41963970976 → picture @03:49:46Z; 41967229502 → @04:21:03Z; next → @04:23:54Z). Durable fix → #4977: watchdog feed-picture aging + self-heal dispatch at >20 min stale (comment 6649233534).
- Closure: OPEN (durable leg); interim heal PROVEN ×3.

## D-g — priority-window fiction (window ruled but absent from machinery)
- State: CLOSED on Desk evidence: PR #4740 merged `6681aeba5f5d` (dispatch-tiers.json priority_window stanza) + window flip verified in feeds @04:23:54Z (priority-windows.json windows = [d1-studysprint ABSOLUTE til freeze verifies], collector cycle dispatched by the cadence seat).
- Closure: **CLOSED ✓** (evidence above).

## Admission set — folded defects (custody #4977)
- Phantom drain: DEFERRED stamps claimed a "drain re-evaluates" that had ∅ implementation → Fix 3a stamp text corrected ("recovery = manual reopen + producer claim (no automatic drain)") + Fix 3b drain spec (picture-flip trigger) — comment 6649198061.
- Watchdog intake-incomplete scan + admission ¬ADMITTED on intake-fail (false-green) → Fixes 1/2 + Oversight spec fold (comment 6649251450, incl. NEW edited-trigger leg).
- Label reconciliation (adds-only stamps; #4965/#4966 carried swarm-admitted ∧ deferred-by-tier) → Fix 4 (comment 6649240025).

## D-i — INVOKE ≠ PRODUCTION (false-green invoke receipts)
- State: TRACKED in this audit (Desk addendum, 2026-11-04 20:40 PT). Evidence: the gemini-dispatch chain {router → OpenRouter free gemma-4-31b → 429 → incomplete} stamps job SUCCESS = false-green; the route is text-only (∅ build capability) and its invoke receipts carry ∅ repo-visible production heartbeat.
- Closure class: an invoke receipt reads HAND-OFF ONLY unless it carries production evidence {branch · PR · run output}. An invoke with no production evidence never closes a filing.
- Closure: OPEN (class rule stands in this audit; enforcement rides the admission/watchdog set #4977/#4979 — receipts without production evidence stay visible as hand-offs in V5/V6).

## Desk legs (owned at the Desk seat, tracked here for the set)
- D-a filing-form discipline — Desk.
- D-e stale reads (both directions) — Desk.
- D-b — per packet of record @ manager; no cadence-custody leg.
