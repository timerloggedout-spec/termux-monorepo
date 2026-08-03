# AGENTS.md — Termux monorepo

Instructions for coding agents (Grok, Claude, Codex, Devin, ChatGPT, local runners).

## Read first (in order)

1. **This file** (`AGENTS.md`)
2. [`docs/LINEAR-AGENT-PROTOCOL.md`](docs/LINEAR-AGENT-PROTOCOL.md) — **Linear hooks for every agent action**
3. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
4. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
5. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may rewrite PR bodies (multi-agent)
6. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
7. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — living board
8. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges
9. [`docs/SENTRY_LINEAR.md`](docs/SENTRY_LINEAR.md) — Sentry multi-project + Linear bridge

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## Hard rules

- Target **`master-staging`**, not raw `master`, for integration work.
- Both gates must pass before merge:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first **and** a Linear `TER-*` issue.
- Cite **`Implements: TER-N`** (and proposal item IDs) on PRs/commits.
- **Linear is mandatory for agent actions** — see protocol:
  - Start work → Linear **In Progress**
  - Open PR → comment on TER-* with PR URL
  - Merge to `master-staging` → Linear **Done** + evidence
  - MCP: `linear___save_issue` / `linear___list_issues`  
    CLI: `python3 -m archwiz.linear_client start|done|status|comment TER-N`
- **No** wholesale merge of PR #6 (TER-9) or PR #2 (Rust CI) — see disposition comments.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is not consensus — write Review log or DEBATE.md (and Linear comment if execution-related).
- PR body rewrites: follow `docs/PR-SUMMARY-PROCESS.md` roster (not a single-agent monopoly).

## Debate & close

- Debate: MANIFEST Review log, optional DEBATE.md, linked PR/issue.
- Close: all items terminal + Review log outcome + move `active/` → `closed/` + registry update.
- Close related **Linear TER-*** explicitly (Done / Canceled) — proposal close does not auto-close Linear.
- Full rules: `docs/proposals/PROCESS.md` §§ consensus / closing · `docs/LINEAR-AGENT-PROTOCOL.md`.

## Preferred execution loop

```text
registry.yaml + Linear list_issues → pick todo
  → linear_client start TER-N (or MCP save_issue In Progress)
  → branch from master-staging (prefer Linear gitBranchName)
  → implement → PR with Implements: TER-N[, ITEM-ID]
  → comment on Linear issue with PR URL
  → gates green → merge
  → linear_client done TER-N --pr <n>
  → update ITEMS.md status
```

## Security

Credential rotation and history rewrite require Operator (human) authorization.
See `docs/SECURITY-REMEDIATION.md`.
