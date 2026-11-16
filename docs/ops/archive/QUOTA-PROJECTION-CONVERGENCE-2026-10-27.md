# Quota Projection Convergence (2026-10-27)

Closes the remaining half of the coordination ask on PR #1504 (comment
6335746305): a future publisher can now feed the quota panel from the
probe workflow's public projection without a hand-seeded file.
Companions: `QUOTA-READINGS-GAPS-2026-10-27.md` (#1764 — `record()` stamps
`observed_at` for live reads only; readings snapshot regenerated) and
PR #1826 (G-12c — the projection itself converged at the source). This
change adds the last missing piece, the publisher converter. Registry
records, the committed readings snapshot and `quota.txt` are unchanged.

## State after #1826 (verified against master)

`scripts/quota_poll.py --public` now emits `quota-public-status/v2`:
rows carry the readings contract's evidence shape (`observed_at` /
`horizon` / `evidence_status`, derived exactly as `record()` derives
them) and, for live reads, a coarse display status derived in-memory
from the private reading (`ok` / `watch` / `exhausted` / `cap_tripped`;
model lane stays `private_preflight`; observed-but-unclassifiable stays
`unknown`). No used/limit/reset values, notes or hashes are exported.
An unobserved service carries `observed_at: null` / H1.

What was still missing: the v2 rows are *panel-shaped*, but the readings
file (`3l0.quota-readings.v1`) also needs `used` / `limit` / `unit` /
`reset` / `note` per row and the top-level `schema` / `generated_at` /
`source` — so a publisher still had to hand-assemble the snapshot.

## This change: the publisher converter

`readings_snapshot(public, services)` in `scripts/quota_poll.py`, CLI:

```
python3 scripts/quota_poll.py --from-public quota-public-status.json \
    --registry ops/quota/registry.json --out <dir>   # writes <dir>/quota-status.json
```

Conversion rules (all pinned by tests):

- Accepts `quota-public-status/v1` and `/v2`; any other input schema is
  refused. V1 artifacts that predate the evidence fields are re-derived
  by `record()`'s own rule from the row's status + observation time.
- `used: null`, `reset: null` on **every** row — the projection exports
  no values, and no reset is ever inferred (the pinned
  `openrouter.free_models` shape — status unknown, used null, reset
  null — falls out of this rule for its `private_preflight` row).
- `limit` / `unit` copied from the public registry — documented
  entitlements, never balances.
- A coarse display status is carried **only** on genuine live evidence
  (H0 + confirmed + an observation time) — exactly what the consumers'
  fail-closed gate requires anyway. `private_preflight` and `unknown`
  rows convert to `unknown`; the panel derives "private" from the model
  lane itself. `horizon` / `evidence_status` / `observed_at` are copied,
  never upgraded.
- `source` states the conversion and carries the contract phrase
  "not a live quota feed".

## Publisher procedure (the durable loop, unchanged in kind)

1. Dispatch `vercel-quota-probe.yml` (dispatch-only; artifact-only,
   7-day retention — poller output is still never a commit).
2. Download the `quota-readings` artifact (`quota-public-status.json`).
3. Run the converter (above); review the resulting `quota-status.json`.
4. Land it through the established generated-file PR path at **both**
   snapshot paths, byte-identical: `docs/ops/generated/quota-status.json`
   and `apps/help-wanted-dashboard/data/quota.json`. Regenerate
   `quota.txt` with `scripts/quota_tui.py` in the same PR.
5. Promote promptly, and know what a promotion replaces: a converted
   snapshot is complete (one row per registry record), not a merge — it
   supersedes the previous snapshot's attributed/hand-promoted rows.
   A live row is inside the panel's 15-minute H0 window only if viewed
   within 15 minutes of the probe run; after that it honestly renders
   `stale`, as the gate intends.

## What did not change, deliberately

- **The fail-closed gate is untouched.** `quota-evidence.js` still
  requires `observed_at` ≤ 15 min old + H0 + confirmed + a supported
  status; `quota_tui.py` mirrors it. Converted rows are pinned against
  both consumers (`test_quota_dashboard.py`, TUI + Node parity): fresh
  `ok` surfaces, model rows render private, unobserved rows stay
  unknown, aged live rows go stale.
- **The probe workflow is untouched**: dispatch-only, `contents: read`,
  uploads only `quota-public-status.json`.
- **The committed snapshot is untouched.** This change builds the
  converter; it does not run a probe or promote a converted snapshot —
  doing so would discard the hand-promoted H0 readings of the gap fill.
  The first promotion is a future generated-file PR from a real probe
  artifact, per the procedure above.
- **Privacy is preserved end to end.** No balances or values enter the
  projection (#1826, canary-pinned) or the converted snapshot
  (canary-tested here: a private `used` value planted in a converter
  input artifact does not survive conversion).

## Note on the superseded PR #1819

An earlier version of this convergence (status-only v1 projection +
converter) was published as PR #1819 from the pre-#1826 master and
conflicted once #1826 landed its v2 design. It was closed unmerged;
this change is its rebased-by-content successor, keeping #1826's
projection design intact and adapting the converter to it (v1 + v2
inputs, coarse statuses carried on live evidence only).

## Tests

- `tests/test_quota_poll.py`: converter contract (schema refusal,
  generated_at/source, unknown/null pins, documented-limit sourcing,
  status-carry rule incl. a forged-evidence row, v1 re-derivation),
  `--from-public` CLI writes only `quota-status.json` and drops planted
  private values.
- `tests/test_quota_dashboard.py`: converted rows feed `quota_tui.py`
  and `quota-evidence.js` with no hand-seeding, fresh and aged.
