# Help-Wanted Foreign-Repo Continuous Evaluation

**Updated:** 2026-09-20  
**Related:** `docs/ops/HELP-WANTED-DASHBOARD.md`, `docs/ops/generated/help-wanted-status.md`, issue lanes under help-wanted workflows.

## Problem

Foreign-repo comments (stake + contribute, redirects, diverged forks) go stale without a feedback loop. Status JSON counts `foreign_open` but operators need **rules** for what to do next.

## Continuous eval loop

1. **Ingest** — generated status lists foreign open PRs + tributes.
2. **Classify** each foreign PR:
   - `engage` — aligned; leave constructive contribution note
   - `redirect` — work belongs in monorepo / governed fork; link + rules
   - `diverge` — intentionally separate build; do not absorb
   - `stale` — closed upstream or no response; drop from active list on next generate
3. **Upgrade feedback** — contribution rules: dual-gate, no secrets, cite `docs/ops/LANE-MATRIX.md` when inviting monorepo PRs.
4. **Alternate repos** — `gh-aw_fork`, `termux-mcp`, `android-mcp`, research hubs remain valid diverged surfaces; mirror policy, do not force single-repo monopoly.

## Anti-patterns

- One-shot help-wanted spam with no follow-up scoring
- Treating Copilot / any single peer as the foreign-repo authority
- Pasting secrets or PATs into foreign comments

Agent-Identity: Grok (Administrator)
