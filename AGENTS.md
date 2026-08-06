# AGENTS.md — Termux monorepo

Instructions for coding agents (Grok, Claude, Codex, Devin, ChatGPT, local runners).

## Read first (in order)

1. **This file** (`AGENTS.md`)
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may rewrite PR bodies (multi-agent)
5. [`docs/ops/PR-SCOPE-DISCIPLINE.md`](docs/ops/PR-SCOPE-DISCIPLINE.md) — **one intent per PR; no catch-all branches** (PR #42 / `src/db.py` lesson)
6. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
7. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — living board
8. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges
9. [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — tiers, merit path, CRDT, optional Raft-strict

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## Hard rules

- Target **`master-staging`**, not raw `master`, for integration **code**.
- **Exception:** docs-only PRs and default-branch workflow activation may target `master` (issue_comment events only fire from default branch). Keep those diffs minimal.
- Both gates must pass before merge of **code** onto `master-staging`:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
  - These scripts live primarily on `master-staging`; do not expect them on a pure docs checkout of `master`.
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **One intent per PR** — workflows ≠ app perf ≠ Sentinel ≠ dashboard UX. See `docs/ops/PR-SCOPE-DISCIPLINE.md`.
- **No** wholesale merge of PR #6 (TER-9) or PR #2 (Rust CI) — see disposition comments.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is not consensus — write Review log or DEBATE.md.
- PR body rewrites: follow `docs/PR-SUMMARY-PROCESS.md` roster (not a single-agent monopoly).
- Scan **open agent PRs** before editing; prefer disjoint files; post `<!-- agent-claim -->` when claiming work.

## Debate & close

- Debate: MANIFEST Review log, optional DEBATE.md, linked PR/issue.
- Close: all items terminal + Review log outcome + move `active/` → `closed/` + registry update.
- Full rules: `docs/proposals/PROCESS.md` §§ consensus / closing.

## Preferred execution loop

```text
registry.yaml → pick todo item → branch from master-staging
  → implement (minimal, single-intent diff) → PR with Implements: ID
  → gates green → merge → update ITEMS.md status
```

## Security

Credential rotation and history rewrite require Operator (human) authorization.
See `docs/SECURITY-REMEDIATION.md`.

## Agentic command surface (ADE — intentional)

Agents **may** run shell / `gh` / tools inside trusted CI runs. That is required for an Automated Agentic Development Environment. Mitigations: association gates (OWNER/MEMBER/COLLABORATOR), fork exclusion, GEMINI.md hard rules, no secret interpolation from untrusted bodies. See `docs/AGENTIC-CICD-FREE-TIER.md`. Security scanners (e.g. Aikido) flagging “agent passes commands” should treat this as **in-scope product behavior**, not accidental exposure — whitelist / exclude with that understanding.
