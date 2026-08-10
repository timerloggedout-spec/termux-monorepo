# AGENTS.md — Termux monorepo (transitional SSOT)

Instructions for coding agents (Grok, Claude, Codex, Devin, ChatGPT, Jules, local runners).

## Dual-file entry (mandate)

| File | Audience |
|------|----------|
| **`AGENTS.grimoire.md`** | **Main agent entry** (compressed). Migrate from `AGENTS.cedr.md`. |
| **`AGENTS.conv.md`** | Conventional human-readable twin. |

Round-trip compress↔expand with perfect reconstruction is a **merge measurement** for Grimoire/Linguist PRs. See `docs/ops/AGENTS-DUAL-FILE.md` · `docs/ops/GRIMOIRE-NAMING.md`.

Until both files exist on the default branch, this `AGENTS.md` remains the readable hard-rules source.

## Read first (in order)

1. **This file** + dual-file pair when present
2. [`docs/ops/DECISION-MATRIX.md`](docs/ops/DECISION-MATRIX.md) — **mandatory** priority data
3. [`docs/ops/OPERATOR-SIGNING.md`](docs/ops/OPERATOR-SIGNING.md) — session/msg signatures + diff ledger
4. [`docs/ops/ROLES-SKEPTIC-CRITIC-11TH.md`](docs/ops/ROLES-SKEPTIC-CRITIC-11TH.md) — challenge roles
5. [`docs/ops/DELPHI-WEIGHTING.md`](docs/ops/DELPHI-WEIGHTING.md) — Delphi (critical)
6. [`docs/ops/MATRIX-QUEUE.md`](docs/ops/MATRIX-QUEUE.md) — Actions cue/queue
7. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml)
8. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — debate / consensus / close
9. [`docs/CONSENSUS.md`](docs/CONSENSUS.md)
10. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) · [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md)

## Hard rules

- Target **`master-staging`**, not raw `master`, for integration work.
- Gates: `python3 scripts/ci/repo_gate.py` · `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **No** Class 3/4 artifacts in git.
- Unposted chat is not consensus — write Review log or DEBATE.md.
- **Participate in Debate + Decision Matrix** when touching P0/High band items.
- **Grimoire naming:** do not brand new work as CEDARLang; CEDARScript is seed-only; prefer Grimoire + `cid.py` conventions.
- **OPERATOR** signs ops/matrix commits per signing ledger.
- **Jules:** continue-existing `context_key` session; disposition-first.
- **Skeptic / Critic / 11th Man** required on P0 matrix and security/session merges.

## Preferred execution loop

```text
registry + matrix → debate if P0/High → branch from master-staging
  → implement → PR Implements: ID → gates + round-trip if Grimoire
  → disposition → merge → ledger + matrix update if scores change
```

## Security

Credential rotation and history rewrite require Operator (human) authorization.
See `docs/SECURITY-REMEDIATION.md`.
