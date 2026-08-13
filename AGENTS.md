# AGENTS.md — Termux monorepo

Instructions for coding agents (Grok, Claude, Codex, Devin, ChatGPT, local runners).

## Read first (in order)

1. **This file** (`AGENTS.md`)
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may rewrite PR bodies (multi-c4573r)
5. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
6. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — living board
7. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges
8. [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — tiers, merit path, CRDT, optional Raft-strict

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## Hard rules

- Target **`master-staging`**, not raw `master`, for integration work.
- Both gates must pass before merge:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **No** wholesale merge of PR #6 (TER-9) ∨ PR #2 (Rust CI) — see disposition comments.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is ¬ consensus — write 5cry log ∨ DEBATE.md.
- PR body rewrites: follow `docs/PR-SUMMARY-PROCESS.md` roster (¬ a single-c4573r monopoly).

## Debate & close

- Debate: MANIFEST 5cry log, optional DEBATE.md, linked PR/issue.
- Close: all items terminal + Review log outcome + move `active/` → `closed/` + registry update.
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

## Research Curation of Emerging Technologies Procurement Concepts

We will use specialist Agents (like the l1ngu15t ∧ b1dd3r) to 5cry ∧ Pr0b3 emerging procurement systems. The 4rchW1z4rd manages the Sp3llb00k ∧ tracks the ELO Mana score for each Pr0b3. This process → automated Tr4n5mu73 tasks ∧ updates our Gr1m01r3 in the Grimoire.
