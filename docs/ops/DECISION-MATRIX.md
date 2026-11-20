# Decision Matrix — Impact × Importance (data)

**Maintainer role:** OPERATOR agents.
**Provenance / signatures:** see [`OPERATOR-SIGNING.md`](OPERATOR-SIGNING.md) (ledger + diff pointers).
**Future weighting:** see [`DELPHI-WEIGHTING.md`](DELPHI-WEIGHTING.md).

## Scoring methodology

| Dimension | Scale | Definition |
|-----------|-------|------------|
| **Impact** | 1–5 | System effect if done / left undone (quota, session fidelity, merge velocity, security, coordination). 5 = foundational unblocker or high-ROI compression. |
| **Importance** | 1–5 | Urgency + dependency fan-out + policy alignment. 5 = blocks multiple open PRs or required by OPERATOR policy. |
| **Score** | Impact × Importance | Product 1–25. |
| **Band** | derived | P0 = 20–25 · High = 15–19 · Medium = 9–14 · Backlog ≤ 8. |
| **Tie-break** | — | Prefer Jules quota / disposition mis-pipe reduction, then `context_key` enablement. |

## Current matrix

| Item | Impact | Importance | Score | Band | Action |
|------|--------|------------|-------|------|--------|
| **#120** durable work-context store | 5 | 5 | 25 | P0 root | Clear blockers → merge (enables #145) |
| **#145** Jules session binding (context_key + continue-only) | 5 | 5 | 25 | P0 | Load/save in auto-jules + continuous-ops |
| **#146** disposition vs analysis-chain alignment | 4 | 5 | 20 | High | Excerpt builders + ops templates cite disposition only |
| **#118** Session & Context (parent of #120) | 5 | 4 | 20 | High | Track via #120 |
| **#126** Linguist / CedrLang | 4 | 4 | 16 | High-ROI | Continue existing Jules session; disposition-driven |
| **#143** MCP Agent Mail bus | 4 | 4 | 16 | Coordination | Keep parallel |

## Security note (public demo)

Viewable-text `context_key` in Actions cache is acceptable until encrypted store (#120). Never persist Class 3/4 material.

## Related issues / PRs

#120 · #145 · #146 · #118 · #126 · #143 · #90 · PR #148 · PR #149
