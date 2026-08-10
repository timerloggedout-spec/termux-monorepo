# AGENTS dual-file convention (merge measurement)

## Mandate

| File | Role |
|------|------|
| **`AGENTS.grimoire.md`** | **Main agent entry** — compressed Grimoire form (token-efficient). Temporary name during migration from `AGENTS.cedr.md`. |
| **`AGENTS.conv.md`** | **Conventional / human-readable** expansion (standard convention). |
| **`AGENTS.md`** | **Transitional SSOT pointer** — until migration completes, points agents to dual-file + hard rules. Long-term: `AGENTS.md` may become the grimoire entry with `AGENTS.conv.md` as the readable twin. |

## Round-trip (merge gate)

```text
AGENTS.conv.md  --compress→  AGENTS.grimoire.md  --expand→  reconstruct
assert reconstruct == AGENTS.conv.md   (modulo documented normalizations)
```

- Round-trip tests are **part of measurement on merge** for Linguist / Grimoire PRs (#126 and successors).
- Perfect reconstruction is the acceptance bar (same spirit as existing converter tests).
- CI should fail merge to `master-staging` when dual-file drift is detected without an explicit OPERATOR waiver comment.

## Migration steps

1. On #126 (or follow-up): rename `AGENTS.cedr.md` → `AGENTS.grimoire.md` (or generate both).
2. Ensure `AGENTS.conv.md` (or current human-readable twin) is the expansion source.
3. Wire test: compress/expand identity.
4. Update AGENTS.md read-first list to mandate grimoire entry for agents, conv for humans/reviewers.

## Related

- [`GRIMOIRE-NAMING.md`](GRIMOIRE-NAMING.md)
- #90 Comms · #126 Linguist
- `workspace/compression_sandbox/cedrlang/` (pre-rename)

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-agents-dual-file
