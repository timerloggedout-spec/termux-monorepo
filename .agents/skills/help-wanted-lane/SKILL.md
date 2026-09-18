---
name: help-wanted-lane
description: Select and execute external help-wanted / good-first-issue tasks. Complexity Perception Prediction Heuristics (CPPH). Oversight scout expansion. Triggers on help-wanted, good-first-issue, external contribution, task selection, or /continue when folding OSS help into workload. Load with evidence-led-monorepo-ops + adaptive-wait.
---

# Skill: help-wanted-lane

**Owner:** Grok Administrator / Oversight Scout population.

**Canonical paths:**
- `.agents/skills/help-wanted-lane/SKILL.md` ← agent load path
- `docs/ops/HELP-WANTED-LANE.md` ← operator card + CPPH
- `scripts/ci/help_wanted_scout.py` ← ranking + catalog emitter
- `.github/workflows/help-wanted-scout.yml` ← scheduled + dispatch scan

**Related:** `docs/ops/SCOUT-MISSIONS.md` (Oversight row), `docs/ops/SCOUT-ROSTER.md`, Issue #342 evaluations.

## Posture

- External contribution is a **workload lane**, not ad-hoc. Select → rank (CPPH) → claim → PR → evidence.
- Prefer unassigned `help wanted` / `good first issue` with clear acceptance criteria.
- Dual-gate remains internal; external PRs follow target-repo norms + our evidence envelope.
- Rate-limit aware: GitHub search 30/min unauth, higher with token. Debounce catalog writes.
- Multi-platform later (GitLab / Bitbucket / Gitea). Provider interface stays abstract.

## Complexity Perception Prediction Heuristics (CPPH)

Score each candidate issue 0–100 (higher = better fit for agent lane):

| Signal | Weight | Rule |
|--------|--------|------|
| Label tier | 25 | `good first issue` / `good-first-issue` = 25; plain `help wanted` / `help-wanted` = 18; `beginner` / `easy` / `difficulty/easy` = 15; `up-for-grabs` = 12 |
| Unassigned | 15 | no assignee → +15; single stale assignee → +5 |
| Body clarity | 15 | has acceptance criteria / steps / "expected" / checklist → +15; body length 80–2000 chars preferred |
| Activity freshness | 10 | updated < 30d → +10; < 90d → +6; > 365d → −5 |
| Comment load | 10 | 0–3 comments → +10; 4–12 → +5; > 30 → −5 (noise) |
| Repo health | 10 | stars 50–50k + recent push → +10; archived / zero activity → 0 |
| Language match | 10 | matches preferred languages (Python, TypeScript, Go, Rust, Shell, Markdown) → +10 |
| Linked work | 5 | no open linked PR that already solves it → +5 |

Clamp 0–100. Emit ranked JSON catalog. Manager (or agent) picks top-N for execution.

## Operating loop

1. Run scout (workflow or `python3 scripts/ci/help_wanted_scout.py`).
2. Review `docs/ops/generated/help-wanted-catalog.json` (or stdout).
3. Claim: comment on target issue, fork if needed, branch, implement, open PR with evidence.
4. Track attribution in monorepo ledger / ACTION-EFFECTIVENESS when material.
5. Prefer extract-only; never force-merge external.

## Seed anchors

- Upstream: https://github.com/mac-s-g/github-help-wanted (React/Redux Semantic-UI help-wanted search UI)
- Fork: https://github.com/timerloggedout-spec/github-help-wanted_fork
- Labels of interest: `help wanted`, `help-wanted`, `good first issue`, `good-first-issue`, `up-for-grabs`, `beginner`, `hacktoberfest`

## BIUDL

Agent-Identity: Grok (Administrator)
