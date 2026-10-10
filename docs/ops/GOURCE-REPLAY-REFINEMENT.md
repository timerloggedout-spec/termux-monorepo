# Gource / SeekLog Replay Refinement Notes

**Session:** 2026-09-21  
**Agent-Identity:** Grok (Administrator)  
**Skills:** adaptive-wait + evidence-led-monorepo-ops  
**Refs:** #718 (landed), help-wanted evidence feed, Core_fork-Gource OBSERVE

## What landed
- `OPS-EVENT-GOURCE.schema.json` + Python `SeekLog` on master (#718, dual-gate green)
- Real replay over help-wanted evidence JSONL (85 events, 2026-09-18 → 2026-09-21)

## Observed pattern (refinement seed)
Follow-up arm emits frequent `followup_skip_idempotent` receipts against the same foreign PR (`vedantnimbarte/zero#81`). All `ok: true` — not failures — but high density.

| Signal | Implication |
|--------|-------------|
| Dense idempotent skips on one path | Cadence may be tighter than useful signal |
| No failed receipts in sample window | Lane health OK; noise ≠ error |
| SeekLog slice of last 30% dominated by skips | Saturation candidate for policy, not for panic |

## Proposed refinement (not auto-applied)
1. **Saturated-path soft cap** — after N identical `followup_skip_idempotent` on the same issue within 24h, emit a single rollup receipt instead of per-run lines (or mark `meta.rollup=true`).
2. **SeekLog summary job** — periodic `evidence_to_ops_events.py --format summary` over `docs/ops/generated/help-wanted-evidence/*.jsonl` to surface `saturated_paths` in ops status.
3. **Do not** change foreign follow-up correctness rules without dual-gate + evidence.

## Tooling
```bash
# summary + saturation
python3 scripts/ops/evidence_to_ops_events.py \
  docs/ops/generated/help-wanted-evidence/*.jsonl --format summary

# Gource custom log for optional visual check later
python3 scripts/ops/evidence_to_ops_events.py \
  docs/ops/generated/help-wanted-evidence/*.jsonl --format gource -o /tmp/hw.gource.log

# recent slice only
python3 scripts/ops/evidence_to_ops_events.py \
  docs/ops/generated/help-wanted-evidence/*.jsonl --slice 0.7:1.0 --format jsonl
```

## Disposition
- Converter: EXTRACT candidate (this follow-up)
- Soft-cap policy: OBSERVE until a dedicated dual-gate PR with tests
- Visualization: still parked
- Core_fork-Gource: still OBSERVE

BIUDL. No YOLO.
