# Publish Preflight Standard (Event Audit F1)

Owner standard via Event Audit audit-001 finding F1 (burst-publish):
bulk publishes ride the **Publisher App bucket** (Termux Fleet
Publisher, own 5000/h) as primary. The shared PAT bucket is
fallback-only, and **no batch starts on any principal without the
derived-reserve preflight** (QAC-007).

## The gate

`scripts/quota_preflight.py` — one batched `/rate_limit` read per
principal (a single call returns every resource bucket), then:

- **reserve** = max(250, 10% of limit) must remain *after* the
  planned batch lands. A batch may never create the wall it hits.
- **bulk** = batch ≥ 25 calls → Publisher primary. PAT carrying a
  bulk batch is the degraded path and prints `DEGRADED-GO`,
  never a silent GO.
- Verdicts: `GO` · `GO-PUBLISHER` · `DEGRADED-GO` · `NO-GO`
  (exit 3). A failed read is NO-GO (exit 2) — unknown is not GO.

## Adoption

- Promotion/publish pipelines (Convergence) run the gate before
  any batch ≥ 25 and record the verdict line with the batch.
- Lane-local publishers call the gate with their planned call
  count; the PAT helper's own circuit breaker remains as the
  second line, not the standard.

Evidence for the finding: rate-limit events
`wall-2026-10-28T23:41:00Z-pat` (155-row promotion hit the wall
mid-batch on PAT) in `ops/quota/rate-limit-events.json`; audits in
`ops/quota/rate-limit-event-audits.json`.
