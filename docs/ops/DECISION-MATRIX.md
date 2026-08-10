# Decision Matrix — Impact × Importance (data)

**Maintainer:** OPERATOR + mandated skeptic/critic/11th-man on P0; #129 roster may propose via queue.
**Provenance:** [`OPERATOR-SIGNING.md`](OPERATOR-SIGNING.md) · **Queue:** [`MATRIX-QUEUE.md`](MATRIX-QUEUE.md) · **Delphi:** [`DELPHI-WEIGHTING.md`](DELPHI-WEIGHTING.md) · **Roster:** [`ROLES-ROSTER.md`](ROLES-ROSTER.md)

## Scoring methodology

| Dimension | Scale | Definition |
|-----------|-------|------------|
| **Impact** | 1–5 | System effect if done / left undone. |
| **Importance** | 1–5 | Urgency + dependency fan-out + policy alignment. |
| **Score** | Impact × Importance | 1–25. |
| **Band** | derived | P0 = 20–25 · High = 15–19 · Medium = 9–14 · Backlog ≤ 8. |
| **Tie-break** | — | Quota/disposition, context_key, Grimoire dual-file gates, then roster rotation health. |

## Current matrix

| Item | Impact | Importance | Score | Band | Action |
|------|--------|------------|-------|------|--------|
| **#120** durable work-context store | 5 | 5 | 25 | P0 root | Hygiene-clean head → merge |
| **#145** Jules session binding | 5 | 5 | 25 | P0 | #148 / coordinate #147 |
| **#90 / Grimoire dual-file + rename** | 5 | 5 | 25 | P0 | AGENTS.grimoire + conv; rename cedr* |
| **#129 team roster + rotation** | 4 | 5 | 20 | High | ROLES-ROSTER; continuous eval; MoneyBall link |
| **#146** disposition alignment | 4 | 5 | 20 | High | #149 |
| **Delphi + challenge + l337/haxor** | 4 | 5 | 20 | High | Weights live in DELPHI + ROSTER |
| **Matrix cue/queue Actions** | 4 | 4 | 16 | High | agent-matrix-queue.yml |
| **#126** Linguist / Grimoire compiler | 4 | 5 | 20 | High | Round-trip merge measurement |
| **#131** MoneyBall / betting arena | 3 | 4 | 12 | Medium | Feed scout/bettor priors |
| **#118** Session parent | 5 | 4 | 20 | High | Via #120 |
| **#143** MCP Agent Mail | 4 | 4 | 16 | Coordination | Parallel |

## Security note (public demo)

Viewable-text `context_key` OK until #120 encrypted store. Never Class 3/4 in git.

## Related

#120 · #145 · #146 · #90 · #126 · #129 · #131 · #118 · #143 · PR #148 · #149 · #147
