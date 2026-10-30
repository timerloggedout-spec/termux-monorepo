# Cadence tick ledger — HFT-style per-request quota telemetry (QAC-009)

`[MUSEai]@{role:{cadence-optimizer}}` ∵ owner order 2026-10-30 ("log like it's HFT").
Spec refs: #320 (notation) ∘ #1734 (claim-level evidence) ∘ RATE-LIMIT-2026-10-29.

## Claim ∘ evidence

- Every GH API response ⊃ `x-ratelimit-{limit,used,remaining,reset,resource}`
  headers ⇒ the measurement EXISTS on every request instance, cost = ∅ extra
  calls ↦ live proof 2026-10-30: PAT-helper ticks show `used` 548→549→550
  across 3 consecutive calls (2 counted ∧ 1 uncounted `/rate_limit`).
- Snapshot sampling (lead-lag cadence checks, 3h-class intervals) ⇒ burn
  attribution NOT ESTABLISHED through every PAT wall ↦ docs/ops/RATE-LIMIT-2026-10-29.md.
- Tick stream ⇒ burn = measured; per-session attribution = ESTABLISHED for
  tick-emitting consumers; Δ`used` between consecutive ticks of one resource
  measures TOTAL fleet burn in the interval (incl. non-emitting consumers).

## Tick schema (append-only JSONL, one tick per request instance)

`{ts, principal, session, method, endpoint, resource, limit, used, remaining, reset, status, counted}`

- `endpoint` = normalized route class (`/repos/{o}/{r}/pulls/{n}`) — route
  shapes aggregate; raw paths ∉ ticks (no id leakage into telemetry).
- `counted=false` ⇔ uncounted instance (`/rate_limit` reads, 304s).
- Tick write = fail-silent: telemetry NEVER breaks the request it rides on.

## Chokepoints

| Phase | Surface | State |
|---|---|---|
| 1 | PAT helper (`custom.github-pat/bin/github_pat.py` `_tick`) | LANDED 2026-10-30 — every lane call via the helper ticks; `pat_publish` ∘ orchestrator chat-side calls inherit |
| 2 | App-token consumers (`scripts/github_app_token.py` minters; principal = `app_collector`/`app_publisher`/…) | adoption — AppID lane |
| 3 | Workflow steps (installation bucket ticks via a shared emit step) | adoption — workflow owners |
| 4 | Tick ingest ↦ Neon lane-events (durable, queryable) | adoption — DB lane; local JSONL = interim store |

Local store (phase 1): the helper's `ticks.jsonl` beside its spend ledger —
one VM, all chat lanes ⇒ the file IS the fleet's chat-side tick stream.

## Consumer

`scripts/cadence_tick_ledger.py` — `check` (schema-validate) ∘ `summarize`
↦ `cadence-tick-ledger/v1` feed: counted calls per principal × resource,
per endpoint class, per-minute burn series, latest remaining per resource.
Feeds: cadence flow pacing (measured burn vs replenishment flow), the
gearbox RPM layer (Viz — per-slice RPM was NOT ESTABLISHED under sampling),
rate-limit incident attribution.

## Invariants

- Ticks are EVIDENCE, never control: no gate reads ticks to spend quota.
- Buckets stay separate ∀ aggregates (PAT core ∘ search ∘ graphql ∘
  per-app installations ∘ Actions installation) — never one merged line.
- Headers only: no tokens, no bodies, no raw ids in the tick stream.
