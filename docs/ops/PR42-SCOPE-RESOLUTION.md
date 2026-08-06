# PR #42 Scope Resolution Record

**Date:** 2026-08-06  
**Agent:** Grok  
**Implements:** CE-22

## Question answered

> Why is `src/db.py` in this PR for Actions Workflows?

**Answer:** It should not be. Accidental scope creep on branch `feature/agentic-cicd-gemini-free`. The file changes are Jules **Bolt** SQLite batching + FTS5, unrelated to Gemini/Jules GitHub Actions workflows.

## Related open PRs (do not duplicate)

| PR | Intent | Overlap with #42 noise |
|----|--------|-------------------------|
| #44 | Sentinel local permissions (db, telemetry, config) | Security chmod on db paths |
| #45 / #66 | Bolt telemetry incremental I/O | dashboard.py |
| #46 / #65 | Palette pulse + a11y status | dashboard.py |
| #63 | curl_cffi Termux symbol fallback | Issue #39 |
| #36 | Early Gemini CLI workflow experiment | Workflow lineage |
| #37 | Bolt fuzzy clustering CodexIndex | Index perf |

## Review threads on #42 that are **out of scope**

Treat as informational for extract PRs; do **not** require #42 to land them:

- `src/db.py` FTS5 without capability check
- `src/db.py` FTS insert de-duplication
- `termux-multi-agent/src/db.py` shared-conn partial failure
- `cli-synthegration/synthegration_index.py` blob path vs text, hash width, reverse_lookup placement
- `termux-multi-agent/dashboard.py` hard-fail without `rich`
- `.Jules` vs `.jules` case collision

## In-scope workflow items (keep fixing on #42 or thin follow-up)

- Gemini dispatch / triage / review / invoke wiring
- Jules on-issues + coordination inventory
- Association gates, free-tier quota hygiene
- `GEMINI.md` + free-tier docs

## Process update

See **`docs/ops/PR-SCOPE-DISCIPLINE.md`** — mandatory for all agents.

Signed-off-by: Grok <grok@x.ai>
