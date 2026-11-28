---
description: Offline self-improvement pass — mines failure patterns, validates advice against retry-success sequences, updates curriculum, and detects body-hint gaps. Run after a batch of /one-shot generations to make the next run smarter.
argument-hint: "[--min-recurrence N] [--prune-age-days N] [--dry-run] [--json]"
allowed-tools: Bash
destructive: false
read-only: false
---

Run the dream consolidator against accumulated bead history:

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/dream_consolidator.py" $ARGUMENTS`

## What it does

1. **Pattern mining** — groups `failures.jsonl` by error signature (auth_401,
   pagination_drift, import_error, etc.), keeps patterns seen ≥ N times
2. **Advice validation** — correlates failure → retry-success sequences from
   `decisions.jsonl`; validated advice gets higher confidence score
3. **Curriculum update** — writes `.beads/curriculum_advice.jsonl`; the next
   `/one-shot` run picks up this file automatically via `beads_curriculum.py`
4. **Hint gap proposals** — clusters unclassified failures and writes
   `.beads/hint_gap_proposals.jsonl` for human review
5. **Stale bead pruning** — removes beads older than N days with no recent
   recurrence (default 90 days)

## When to run

- After 5+ `/one-shot` generations on the same codebase
- When you notice the same class of error recurring
- Before a big feature push (to sharpen the curriculum)

## Examples

```bash
/dream                          # default (min-recurrence=2, prune-age=90d)
/dream --dry-run                # report only, no writes
/dream --min-recurrence 3       # stricter: only act on patterns seen 3+ times
/dream --prune-age-days 30      # more aggressive pruning
/dream --json                   # machine-readable report
```

## Output files

| File | Purpose |
|------|---------|
| `.beads/curriculum_advice.jsonl` | Data-driven advice, loaded by beads_curriculum at runtime |
| `.beads/hint_gap_proposals.jsonl` | Unclassified failure clusters for human review |
| `.beads/dream_report.jsonl` | Append-only log of each dream run |
