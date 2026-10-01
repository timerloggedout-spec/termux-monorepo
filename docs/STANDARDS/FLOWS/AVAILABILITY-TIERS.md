# Hindsight Availability — Remote-First Doctrine

## DO statements

- **DO** expose the codespace as a public HTTPS endpoint on port 8888.
  Auth = `Authorization: Bearer $HINDSIGHT_API_KEY`.
- **DO** route remote reads: codespace public URL → cloud → git snapshot.
- **DO** push the bank snapshot to `memory-bank` every N writes.
- **DO** treat Git as the durable shared substrate. The codespace is cache.
- **DO** keep FTS5 as owner-local accelerator only. Not remote.
- **DO** write pending items to `~/.deepcli/pending/` when no writer is reachable.

## Reader matrix

| Reader | Primary | Fallback |
|---|---|---|
| Owner (Termux) | FTS5 `bank-local.db` | SSH tunnel to codespace :8888 |
| Workflow (Actions) | `https://<cs>-8888.app.github.dev` + bearer | git snapshot from `memory-bank` |
| Collaborator | same public URL | their own FTS5 clone |

## Writer matrix

| Writer | Targets |
|---|---|
| Owner retain | FTS5 + codespace (tunnel) + cloud (if up) |
| Workflow retain | codespace public URL |
| Collaborator retain | codespace public URL |
| Codespace cold | append `~/.deepcli/pending/*.jsonl`; replay on `hs-up` |

## Public URL contract

- Port 8888 → visibility: public
- Endpoints unchanged (`/v1/default/banks/...`)
- All writes require `Authorization: Bearer $HINDSIGHT_API_KEY`
- URL cached at `~/.deepcli/cs-hindsight-url.txt`
- URL refreshes when codespace changes (hs-up does this)

## Git substrate contract

- Branch: `memory-bank`
- Contents:
    bank-latest.zip        (last drain)
    LAST-DRAIN.md          (ts, source, size)
    bank-local.db.lfs      (optional; FTS5 snapshot)
    pending/*.jsonl        (unreplayed writes, if any)
- Cadence:
    on hs-drain (pre-idle, manual)
    on hs-down (before stop)
    on every 100 successful retains (auto)

## Wake policy

- Cold start accepted: 60–90s
- Remote clients retry 3× with 30s backoff before falling to git snapshot
- `hs-up` warms codespace; the first caller pays the wake cost
- Cron keep-warm: opt-in via `HS_KEEPWARM=1` (costs ~240 core-hrs/mo)

## FROZEN state (all writers down)

- Owner appends to `~/.deepcli/pending/owner-<ts>.jsonl`
- Workflows fail closed; return git-snapshot read-only
- On next `hs-up`, `hs-replay` drains `pending/*.jsonl` into codespace + FTS5
