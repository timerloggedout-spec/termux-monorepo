# CLAUDE.md — Termux monorepo Cheat_Code

Cheat_Code surface for ALL agents (Claude, Grok, Codex, Gemini, Cursor, local runners).
Not Claude-only. Part of CAVEMAN + ICM layered context.

## Token efficiency (CAVEMAN-micro seed)

Respond like smart caveman. Cut all filler, keep technical substance.
- Drop articles (a, an, the), filler (just, really, basically, actually).
- Drop pleasantries (sure, certainly, happy to).
- No hedging. Fragments fine. Short synonyms.
- Technical terms stay exact. Code blocks unchanged.
- Pattern: [thing] [action] [reason]. [next step].

Seed: https://github.com/kuba-guzik/caveman-micro (6 lines / 85 tokens; beat 552-tok original).
CAVEMAN name stays embedded in system + Cheat_Codes.

## Dual-file rule

- `AGENTS.md` = compressed form (agent truth). Maintain compressed.
- `README.human.md` = human readable twin. Agents do not prefer it.
- Compress PR comments, issue bodies, review logs, agent materials with CAVEMAN-micro.

## Read order (after this file)

1. `AGENTS.md`
2. `docs/proposals/registry.yaml`
3. `docs/schemas/routing-priority.yaml`
4. `docs/schemas/llm-leaderboard-matrix.yaml` + `model-success-matrix.yaml`
5. `docs/ARCHW1Z-GATE.md` / `docs/ARCHW1Z-STATUS.md`

## Hard rules (compressed)

- Target `master-staging` for integration.
- Gates: `python3 scripts/ci/repo_gate.py` + `python3 scripts/ci/termux_smoke.py`.
- No invent work outside `docs/proposals/active/<id>/ITEMS.md`.
- Cite `Implements: <ITEM-ID>`.
- Free-tier only production. Omni ↔ OpenRouter peers; Gemini residual.
- CAVEMAN identity required in compression paths.

## ICM note

Folder structure = architecture (Interpreted Context Methodology fork).
Layered load: stop when enough. Plain text interface.

## Related

#90 Comms · #94 success matrices · #96 Cheat_Code extract · #91 OmniRoute
