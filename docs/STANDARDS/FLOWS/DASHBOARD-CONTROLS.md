# Dashboard + Controls Design

## Controls (start/stop/assign)

| Control | Command | Effect |
|---------|---------|--------|
| Start pipeline | `hs-pipe start` | Launches rotator watch + sovereign loop on codespace |
| Stop pipeline | `hs-pipe stop` | Kills sovereign + mvt-seed; keeps APIs and rotator |
| Restart | `hs-pipe restart` | stop + start, fresh logs |
| Status | `hs-pipe status` | UP/DOWN per process |
| Rotate model now | `hs-stack rotate` | Picks next with headroom, restarts :8888 |
| Assign bank | `hs-bank-assign <provider> <model> <role>` | Writes to active.json so next tick uses it |

## Bank viewing + assignment

| Action | Command |
|--------|---------|
| List all banks | `hs-facts count` |
| Show lane metrics | `hs-facts count '%::mvt::%'` |
| Inspect one | `hs-facts get BANK UUID` |
| Edit metadata | `hs-facts set-meta BANK UUID '{"key":"v"}' "reason"` |
| Soft-delete | `hs-facts del BANK UUID "reason"` |
| History | `hs-facts hist BANK UUID` |
| Assign new lane | write role/model to `/tmp/hs-stack/active.json` |

## File upload / ingest

| Action | Command |
|--------|---------|
| Ship file to codespace | `hs-upload LOCAL_PATH [DEST]` |
| Retain from a file | POST to `/memories` with items from parsed rows |
| Bulk CSV/JSONL | `hs-upload` splits by line or array, batches into retain calls |
| Whole bank import | `hindsight-admin import-bank <zip>` |

## Per-run stats

Written to `/tmp/mvt-run-state.json` on every batch completion:

    source, provider, model, bank, ok, fail, 429, abort, elapsed_s

Dashboard section `[ RUN STATE ]` reads it live. Shows what's running,
which source, which provider, and completion counters.

For long runs, `hs-dash` also shows `[ MVT SEED — last 8 batch outcomes ]`
from `/tmp/mvt-seed.log`.

## Completion %

Two levels:

1. **Per-tick %** — items processed / total items in current source batch.
   Currently logged as `produced=N qsize=M`. Full % needs the total count
   from the generator before it starts (pending).

2. **Per-source %** — items retained to a bank vs total documents for
   that source. Query:
   `SELECT count(*) FROM memory_units WHERE bank_id = '<bank>'` vs
   `SELECT count(*) FROM documents WHERE bank_id = '<bank>'`.

   If memory_units / documents < 1.0, extraction is partial.

## Quotas + usage (all providers)

| Provider | Endpoint | Live? |
|----------|----------|-------|
| Gemini | 1-token probe on active model | yes (429 body) |
| Gemini (derived) | state.json per-model counters | yes |
| OpenRouter | /api/v1/auth/key + /api/v1/credits | yes |
| OpenRouter (per-model) | llm_requests rows for OR provider | yes |
| Codespace | gh codespace list + billing | limited to personal accounts |

All shown in dashboard. Add `hs-quota-model` when we expand beyond Gemini + OR.

## Tests / batch / no-batch

| Mode | When to use |
|------|-------------|
| **Single item** | Latency baseline, isolation from batching |
| **Batch (N)** | Default. N computed from model input/output limits |
| **No batch (N=1)** | When Hindsight's serializer makes batching slower than serial singles |
| **Parallel batch** | N>1 with concurrent POSTs (4 workers x N) |

Toggle via `MVT_BATCH_SIZE` env:
- `MVT_BATCH_SIZE=1` = no-batch mode
- `MVT_BATCH_SIZE=auto` = hs-batch-plan.py picks
- `MVT_BATCH_SIZE=N` = fixed N

## Dynamic batch size (from model token specs)

`hs-batch-plan.py` reads `/tmp/hs-stack/limits.json`:
- `inputTokenLimit` (per model)
- `outputTokenLimit` (per model)

Computes:
- `by_input = inputTokenLimit // avg_item_tokens`
- `by_output = outputTokenLimit // out_tokens_per_item`
- `planned = min(16, min(by_input, by_output))`

Example for gemini-3.5-flash-lite:
- input=1048576, avg_item=2200 → by_input=476
- output=65536, out/item=110 → by_output=595
- planned = min(16, 476) = **16** (but Hindsight concurrency caps effective at 8)

Env overrides:
- `MVT_AVG_ITEM_TOKENS` (default 2200)
- `MVT_OUT_TOKENS_PER_ITEM` (default 110)

## What else belongs (backlog)

| Feature | Priority | Notes |
|---------|----------|-------|
| Start/stop as dashboard one-liners | done | hs-pipe |
| Run % progress bar | medium | needs total count from source |
| Bank assign UI | low | write active.json via `hs-bank-assign` |
| File upload + auto-bank routing | medium | `hs-upload --bank X --role Y` |
| Test mode (single-item no-batch) | done | env toggle |
| Dynamic batch from token limits | done | hs-batch-plan.py |
| Live cost estimate per run | low | tokens x $/M from llm_requests |
| Retention/aging policy | low | auto-soft-delete facts > N days |
| Webhooks (Slack/Discord) on abort | low | Hindsight supports /webhooks |
| Cross-vendor MVT leaderboard | medium | observatory + leaderboard wired |
| Persistence to memory-bank branch | medium | hs-drain exists, schedule it |
| Codespace idle auto-stop | medium | lower idle_timeout to 30m |
