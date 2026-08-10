# AGENTS.md — Termux monorepo

Instructions for coding agents (Grok, Claude, Codex, Devin, ChatGPT, local runners).

## Read first (in order)

1. **This file** (`AGENTS.md`)
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may rewrite PR bodies (multi-agent)
5. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
6. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — living board
7. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges
8. [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — tiers, merit path, CRDT, optional Raft-strict
9. **Ops (OPERATOR + Jules):**
   - [`docs/ops/DECISION-MATRIX.md`](docs/ops/DECISION-MATRIX.md) — priority scores (clean data)
   - [`docs/ops/OPERATOR-SIGNING.md`](docs/ops/OPERATOR-SIGNING.md) — session/msg signatures + diff ledger
   - [`docs/ops/jules-session-management.md`](docs/ops/jules-session-management.md) — context_key + continue-only
   - [`docs/ops/review-signal-alignment.md`](docs/ops/review-signal-alignment.md) — disposition vs probe

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## Hard rules

- Target **`master-staging`**, not raw `master`, for integration work.
- Both gates must pass before merge:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **No** wholesale merge of PR #6 (TER-9) or PR #2 (Rust CI) — see disposition comments.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is not consensus — write Review log or DEBATE.md.
- PR body rewrites: follow `docs/PR-SUMMARY-PROCESS.md` roster (not a single-agent monopoly).
- **OPERATOR agents** sign material ops/matrix changes per `docs/ops/OPERATOR-SIGNING.md`.
- **Jules / continuous-ops:** prefer continue-existing session for a PR `context_key`; act on disposition, not analysis-chain scripts.

## Debate & close

- Debate: MANIFEST Review log, optional DEBATE.md, linked PR/issue.
- Close: all items terminal + Review log outcome + move `active/` → `closed/` + registry update.
- Full rules: `docs/proposals/PROCESS.md` §§ consensus / closing.

## Preferred execution loop

```text
registry.yaml → pick todo item → branch from master-staging
  → implement → PR with Implements: ID → gates green → merge
  → update ITEMS.md status
```

## Security

Credential rotation and history rewrite require Operator (human) authorization.
See `docs/SECURITY-REMEDIATION.md`.
Viewable-text `context_key` in Actions cache is acceptable on this public demo until encrypted store (#120).
