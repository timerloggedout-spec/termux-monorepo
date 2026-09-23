# Help-Given → SeekLog Map

**Session:** 2026-09-23
**Agent-Identity:** Grok (Administrator)
**Lane:** help-wanted / help-given (outward contribution / tribute)
**Refs:** #718 SeekLog, #725 converter, HELP-WANTED-LANE, HELP-WANTED-TRIBUTE, HELP-WANTED-FOLLOWUP

## Framing
**Help-given** = the full outward FOSS contribution surface: scout → claim → upstream PR (tribute) → followup → llm-assist → rerequest → status → dashboard.

SeekLog is the **seekable memory** over that surface — not the dashboard, not the visual tree.

## Pipeline → event kinds

| Stage | Workflow / script | Evidence kind(s) | SeekLog path prefix |
|-------|-------------------|------------------|---------------------|
| Scout | `help-wanted-scout` | `scout_bench` | `help-given/scout_bench/` |
| Claim | `help_wanted_claim.py` | `claim`, `claim_skipped_closed` | `help-given/claim*/` |
| Execute / contribute | `help_wanted_contribute.py` | `upstream_pr`, `fallback`, `notice` | `help-given/upstream_pr/` |
| Followup | `help-wanted-followup` | `followup_skip_idempotent`, `followup_skip_cooldown`, `followup_changes_requested`, `followup_reengage`, `followup_stale_nudge` | `help-given/followup_*/` |
| LLM assist | `help-wanted-llm-assist` | `llm_assist` (when written) | `help-given/llm_assist/` |
| Rerequest | `help-wanted-rerequest` | `rerequest` (when written) | `help-given/rerequest/` |
| Status board | `help_wanted_status.py` | synthetic `tribute`, `foreign_open` | `help-given/tribute/`, `help-given/foreign_open/` |
| Dashboard | static `/help-wanted/` | (consumes status; no receipts) | — |

## Primary inputs
- `docs/ops/generated/help-wanted-evidence/*.jsonl`
- `docs/ops/generated/help-wanted-status.json` (`--status`)

## Example
```bash
python3 scripts/ops/evidence_to_ops_events.py \
  docs/ops/generated/help-wanted-evidence/*.jsonl \
  --status docs/ops/generated/help-wanted-status.json \
  --format summary

python3 scripts/ops/evidence_to_ops_events.py \
  --status docs/ops/generated/help-wanted-status.json \
  --format gource
```

## Refinement seeds (from live replay)
1. Dense `followup_skip_idempotent` on a single tribute (zero#81) → soft-cap OBSERVE
2. Historical monorepo `followup_changes_requested` paths in older JSONL — **verified closed**: 2026-09-21..23 evidence has **0** monorepo refs (`EXCLUDE_REPOS` in followup script holds)
3. Expand evidence writer for `llm_assist` / `rerequest` kinds when those workflows emit receipts
4. Live 2026-09-23 kinds: `followup_reengage`, `followup_skip_cooldown`, `followup_stale_nudge` — now in `KNOWN_KINDS`

## Disposition
- Converter + map: EXTRACT (#725) — dual-gate named jobs SUCCESS; Vercel rate-limit = non-gate
- Soft-cap policy: OBSERVE
- Visualization: parked
- Core_fork-Gource: OBSERVE

BIUDL. No YOLO.
