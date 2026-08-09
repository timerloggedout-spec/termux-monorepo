# AGENTS.md — Termux monorepo (compressed)

Instructions coding agents (Grok, Claude, Codex, Devin, ChatGPT, local).

## Read first (order)

1. This file (`AGENTS.md`) — compressed agent truth
2. `CLAUDE.md` — Cheat_Code (CAVEMAN-micro + dual-file). All agents.
3. `docs/proposals/registry.yaml` — active
4. `docs/proposals/PROCESS.md` — post / debate / consensus / close
5. `docs/PR-SUMMARY-PROCESS.md` — who rewrite PR bodies
6. `docs/ARCHW1Z-GATE.md` — repo-gate + termux-smoke
7. `docs/ARCHW1Z-STATUS.md` — living board
8. `docs/proposals/AGENTIC-PERMISSIONS.md` — human-only edges
9. `docs/CONSENSUS.md` — tiers, merit, CRDT, optional Raft-strict

Optional: `CONTRIBUTING.md`. Human twin: `README.human.md`.

## CAVEMAN (required identity)

Seed: kuba-guzik/caveman-micro (6 lines / 85 tok).
Prompt live in `CLAUDE.md` + `workspace/caveman/caveman-micro.txt`.
Keep word CAVEMAN embedded every compression path + Cheat_Code tag.
Apply to: PR comments, issues, review logs, agent materials.

Respond like smart caveman. Cut all filler, keep technical substance.
- Drop articles (a, an, the), filler (just, really, basically, actually).
- Drop pleasantries (sure, certainly, happy to).
- No hedging. Fragments fine. Short synonyms.
- Technical terms stay exact. Code blocks unchanged.
- Pattern: [thing] [action] [reason]. [next step].

## Dual-file policy

| Role | File | Rule |
|------|------|------|
| Agent compressed | `AGENTS.md` | Maintain compressed. Source of truth agents. |
| Human readable | `README.human.md` | Full prose. Agents skip prefer. |
| Cheat_Code | `CLAUDE.md` | All agents. CAVEMAN + ICM layers. |

## Hard rules

- Target **`master-staging`**, not raw `master`, integration work.
- Both gates pass before merge:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **No** wholesale merge PR #6 (TER-9) or PR #2 (Rust CI) — see disposition.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat not consensus — write Review log or DEBATE.md.
- PR body rewrites: follow `docs/PR-SUMMARY-PROCESS.md` roster.

## Routing / matrices

- Peers: Omni ↔ OpenRouter equal band; Gemini residual. Free only.
- Public boards = features. Our success matrix = labels (ELO++/3L0).
- Mix: control ~60% / mixed ~25% / random_valley ~15%.
- Schemas: `docs/schemas/routing-priority.yaml`, `llm-leaderboard-matrix.yaml`, `model-success-matrix.yaml`.

## Debate & close

- Debate: MANIFEST Review log, optional DEBATE.md, linked PR/issue.
- Close: all items terminal + Review log outcome + move `active/` → `closed/` + registry update.
- Full: `docs/proposals/PROCESS.md`.

## Preferred execution loop

```text
registry.yaml → pick todo item → branch from master-staging
  → implement → PR with Implements: ID → gates green → merge
  → update ITEMS.md status
```

## Security

Credential rotation + history rewrite require Operator (human) authorization.
See `docs/SECURITY-REMEDIATION.md`.
