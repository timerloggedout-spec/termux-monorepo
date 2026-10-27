# Quota Projection Convergence (2026-10-27)

Closes the coordination ask on PR #1504 (comment 6335746305): converge the
probe workflow's status-only public projection (`quota-public-status/v1`)
with the dashboard readings contract (`3l0.quota-readings.v1`) so a future
publisher can feed the panel from the probe projection without a
hand-seeded file. Companion to `QUOTA-READINGS-GAPS-2026-10-27.md`, whose
source fix (live reads only carry `observed_at`) this builds on. Registry
records, the committed readings snapshot and `quota.txt` are unchanged.

## The gap (verified against master)

| Shape | Fields per row | Problem |
|---|---|---|
| Probe projection (`scripts/quota_poll.py --public`, artifact of `vercel-quota-probe.yml`) | `resource_id`, `provider`, `status` ∈ {`private_preflight`, `unknown`}, `observed_at` | No `horizon`, no `evidence_status` — the two fields both public consumers (`quota-evidence.js`, `quota_tui.py`) gate on. Not the readings contract, so the panel could not consume it. |
| Readings snapshot (`docs/ops/generated/quota-status.json` == `apps/help-wanted-dashboard/data/quota.json`) | `resource_id`, `status`, `used`, `limit`, `unit`, `reset`, `note`, `evidence_status`, `horizon`, `observed_at` | Could only be produced by hand-seeding/promoting individual readings (the 2026-10-27 gap fill). |

## Design

Two minimal changes, both in `scripts/quota_poll.py`; no workflow,
consumer or gate changes.

1. **The projection speaks the readings contract's evidence language.**
   `public_snapshot()` rows now also carry `horizon` + `evidence_status`,
   derived by a new shared helper `evidence_for()` — the exact rule
   `record()` already used, now shared by construction:
   - live-read row → `H0` / `confirmed` (a genuine live read is the
     evidence; the row's *status* stays `private_preflight` — values and
     the real status remain withheld);
   - unobserved row → `H1` / `attributed_claim` (or `early_signal` for a
     non-URL source), `observed_at: null`.
2. **A publisher converter.** `readings_snapshot(public, services)` (CLI:
   `quota_poll.py --from-public quota-public-status.json --out <dir>`)
   converts a downloaded probe artifact into a readings-contract
   `quota-status.json`:
   - `status: "unknown"`, `used: null`, `reset: null` on **every** row —
     the projection withholds real statuses and values, so the public row
     must not gain one, and no reset is ever inferred (the pinned
     `openrouter.free_models` shape falls out of this rule);
   - `limit` / `unit` copied from the public registry — documented
     entitlements, never balances;
   - `horizon` / `evidence_status` / `observed_at` copied from the
     projection, never upgraded (pre-convergence artifacts missing the
     new fields are re-derived by the same `evidence_for` rule from the
     row's own status/`observed_at`);
   - `source` states the conversion and carries the contract phrase
     "not a live quota feed"; input with any other schema is refused.

## Publisher procedure (the durable loop, unchanged in kind)

1. Dispatch `vercel-quota-probe.yml` (dispatch-only; artifact-only,
   7-day retention — poller output is still never a commit).
2. Download the `quota-readings` artifact (`quota-public-status.json`).
3. `python3 scripts/quota_poll.py --from-public quota-public-status.json --out <dir>`
4. Review `<dir>/quota-status.json`, then land it through the established
   generated-file PR path at **both** snapshot paths, byte-identical:
   `docs/ops/generated/quota-status.json` and
   `apps/help-wanted-dashboard/data/quota.json`. Regenerate `quota.txt`
   with `scripts/quota_tui.py` in the same PR if the rows changed.
5. Promote promptly: a converted live row is only inside the panel's
   15-minute H0 window if it is viewed within 15 minutes of the probe
   run; after that it honestly renders `stale`, as the gate intends.
   A conversion therefore replaces the attributed/hand-promoted rows of
   the previous snapshot only when the publisher means it to — the
   converter output is a complete snapshot (one row per registry
   record), not a merge.

## What did not change, deliberately

- **The fail-closed gate is untouched.** `quota-evidence.js` still
  requires `observed_at` ≤ 15 min old + `H0` + `confirmed` + a supported
  status. `private_preflight`/`unknown` are not display statuses, so a
  converted snapshot renders every non-model row `unknown` (model lane:
  `private`) and `stale` once aged — pinned by new tests against both
  consumers (`test_quota_dashboard.py`, TUI + Node parity).
- **The probe workflow is untouched**: dispatch-only, `contents: read`,
  uploads only `quota-public-status.json`.
- **The committed snapshot is untouched.** This change builds the
  converter; it does not run a probe or promote a converted snapshot —
  doing so would discard the hand-promoted H0 readings of the gap fill
  for all-unknown rows. The first promotion is a future generated-file
  PR from a real probe artifact, per the procedure above.
- **Status-only is preserved.** No balances, values, hashes or reader
  log lines enter the projection or the converted snapshot (canary-
  tested: a private `used` value planted in a converter input artifact
  does not survive conversion).

## Tests

- `tests/test_quota_poll.py`: projection row shape + evidence derivation
  (live vs unobserved), converter contract (schema, source phrase,
  unknown/null pins, documented-limit sourcing, evidence copying),
  legacy-artifact re-derivation, non-projection rejection, `--from-public`
  CLI writes only `quota-status.json` and drops planted private values.
- `tests/test_quota_dashboard.py`: converted rows classify fail-closed
  in `quota_tui.py` and in `quota-evidence.js` (Node), fresh and aged.
