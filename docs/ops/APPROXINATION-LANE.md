# Approxination Lane (Production)

**Status:** LIVE skill + cohort card (docs/skills extract). Gitlink pin optional (APPROX-005 backlog).
**Forks:** [Approxination-Benchmark_fork](https://github.com/timerloggedout-spec/Approxination-Benchmark_fork) · [Inverse-Arena_fork](https://github.com/timerloggedout-spec/Inverse-Arena_fork)

## Why

Tool-layer comparison and skill ranking belong in AEF **Oversight** + MoneyBall/3L0, same class as SWE-agent reference treatments. Approxination supplies:

1. Ranked **skill search** (find)
2. **Skill creation** from top refs (generate)
3. **Contribution** via execution reports → ELO
4. Fixed **A/B/C/D** arms for blind pairwise evaluation

## Components

| Path | Role |
|------|------|
| `.agents/skills/approxination-lane/SKILL.md` | Agent load |
| `docs/evaluations/approxination/COHORT.md` | AEF cohort + pin policy |
| `docs/proposals/active/approxination-integration/` | ITEMS + registry |
| Benchmark fork | 67 tasks × modes + judge + ELO scripts |
| Inverse-Arena fork | Pairwise fuzzy + ELO engine reference |

## Cadence

| Action | When |
|--------|------|
| Skill find/generate/feedback | On demand during agent work |
| Formal A/B/C/D run | Explicit cohort experiment (DOE item) |
| Upstream mode/task PR | Via help-wanted-execute or manual on fork |
| Pin advance | PR only; dual-gate |

## Secrets

| Secret | Use |
|--------|-----|
| Approx registration / `APPROX_TOKEN` | Hosted find/generate/feedback |
| `OPENROUTER_API_KEY` | Benchmark solver/judge (fork runs) |
| `BRAVE_SEARCH_API_KEY` | Modes B/C/D web tool |

Never commit keys. Actions secrets only.

## Delivery hierarchy (contribution)

1. **Feedback** — execution report to arena (primary continuous contribution)
2. **Fork PR** — new mode or task on Approxination-Benchmark_fork
3. **Monorepo evidence** — digest under `docs/evaluations/approxination/`

BIUDL. Agent-Identity: Grok (Administrator)
