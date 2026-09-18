# Help-Wanted Lane (Production)

**Status:** live via feat/help-wanted-lane  
**Anchors:** [mac-s-g/github-help-wanted](https://github.com/mac-s-g/github-help-wanted) · [timerloggedout-spec/github-help-wanted_fork](https://github.com/timerloggedout-spec/github-help-wanted_fork)  
**Scout family:** Oversight (see `docs/ops/SCOUT-MISSIONS.md`)  
**Skill:** `.agents/skills/help-wanted-lane/SKILL.md`

## Why this exists

Fold external open-source **help wanted** / **good first issue** work into the monorepo workload as a first-class lane. Select tasks, predict complexity, execute, and feed evidence back. Eventually expand parity to GitLab, Bitbucket, Gitea, and similar.

This is **not** a rewrite of the 2017 React help-wanted UI; it is an agentic selection + ranking + execution lane that can consume the same label surface those tools surface.

## Complexity Perception Prediction Heuristics (CPPH)

| Signal | Weight | Rule |
|--------|--------|------|
| Label tier | 25 | `good first issue` = 25; `help wanted` = 18; beginner/easy = 15; up-for-grabs = 12 |
| Unassigned | 15 | no assignee +15 |
| Body clarity | 15 | acceptance criteria / steps / checklist +15 |
| Freshness | 10 | updated <30d +10; <90d +6; >365d −5 |
| Comment load | 10 | 0–3 +10; 4–12 +5; >30 −5 |
| Repo health | 10 | active non-archived + stars band +10 |
| Language match | 10 | preferred langs +10 |
| No competing open PR | 5 | +5 |

Score 0–100. Catalog ranked. Manager/agent selects top-N.

### Preferred labels (GitHub)

`help wanted`, `help-wanted`, `good first issue`, `good-first-issue`, `up-for-grabs`, `beginner`, `easy`, `difficulty/easy`, `hacktoberfest`, `contributions welcome`

### Preferred languages (initial)

Python, TypeScript, JavaScript, Go, Rust, Shell, Markdown, YAML

## Components

| Path | Role |
|------|------|
| `.agents/skills/help-wanted-lane/SKILL.md` | Agent load |
| `scripts/ci/help_wanted_scout.py` | Search + CPPH rank + JSON catalog |
| `.github/workflows/help-wanted-scout.yml` | Cron + workflow_dispatch |
| `docs/ops/generated/help-wanted-catalog.json` | Last ranked snapshot (artifact or committed optionally) |

## Operating rules (YOLO / no HITL)

1. Scout produces ranked candidates only. Does not open external PRs autonomously without explicit claim step.
2. Claim via public comment on the target issue before heavy work.
3. Keep monorepo dual-gate green; external contribution is orthogonal.
4. Rate limits: respect GitHub Search API. Prefer authenticated token in Actions.
5. Evidence: link monorepo PR or ledger entry when the external contribution is material to our learning loop.

## Multi-platform roadmap

| Platform | Status | Notes |
|----------|--------|-------|
| GitHub | **P0 live** | Search API + labels |
| GitLab | planned | Issues API + labels |
| Bitbucket | planned | Issues / work items |
| Gitea / Forgejo | planned | compatible issue labels |

Provider interface stays abstract in the scout script so parity is additive.

## Relation to Oversight scout

`docs/ops/SCOUT-MISSIONS.md` already lists Help Wanted under Oversight. This lane is the concrete execution surface for that mission: ranking heuristics, catalog, workflow, and skill so agents can load and act.

## Seed interaction

User and upstream author (mac-s-g) exchanged activity on the help-wanted surface; the fork exists under `timerloggedout-spec/github-help-wanted_fork`. Lane treats that history as provenance, not as a hard dependency.

## BIUDL

Agent-Identity: Grok (Administrator)
