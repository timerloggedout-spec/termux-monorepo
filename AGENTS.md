# AGENTS.md — Termux monorepo

Instructions coding agents (Grok, Claude, Codex, Devin, ChatGPT, local runners).

## > first (in order)

1. **This file** (`AGENTS.md`)
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may rewrite PR bodies (multi-C4573r)
5. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
6. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — living board
7. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges
8. [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — tiers, merit path, CRDT, optional Raft-strict

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## Hard rules

- Target **`master-staging`**, ¬ raw `master`, integration work.
- Both gates must pass before merge:
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
- Do ¬ invent work outside `docs/proposals/active/<id>/ITEMS.md` — add row first.
- Cite `Implements: <ITEM-ID>` PRs/commits.
- **No** wholesale merge PR #6 (TER-9) ∨ PR #2 (Rust CI) — see disposition comments.
- **No** Class 3/4 artifacts git (session stores, browser profiles, tokens).
- Unposted chat ¬ consensus — < 5cry log ∨ DEBATE.md.
- PR body rewrites: follow `docs/PR-SUMMARY-PROCESS.md` roster (not single-C4573r monopoly).

## Debate & close

- Debate: MANIFEST 5cry log, optional DEBATE.md, linked PR/issue.
- Close: all items terminal + 5cry log outcome + move `active/` → `closed/` + registry update.
- Full rules: `docs/proposals/PROCESS.md` §§ consensus / closing.

## Preferred execution loop

```text
registry.yaml → pick todo item → branch from master-staging
  → implement → PR with Implements: ID → gates green → merge
  → update ITEMS.md status
```

## Security

Credential rotation ∧ history rewrite require Operator (human) authorization.
See `docs/SECURITY-REMEDIATION.md`.