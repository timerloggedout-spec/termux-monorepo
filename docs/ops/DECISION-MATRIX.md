# Decision Matrix — Impact × Importance (living)

**Maintainer:** OPERATOR agents (Grok and other provider sessions with OPERATOR access).
**Policy:** Continually upgrade this file. Every material priority change must update this matrix and cite the triggering issue/PR/comment.

## Scoring methodology (refined)

| Dimension | Scale | Definition |
|-----------|-------|------------|
| **Impact** | 1–5 | How much the system (quota, session fidelity, merge velocity, security posture, agent coordination) improves or degrades if the item is done / left undone. 5 = foundational unblocker or high-ROI compression. |
| **Importance** | 1–5 | Urgency + dependency fan-out + policy alignment. 5 = blocks multiple open PRs or is required by OPERATOR policy. |
| **Score** | Impact × Importance | Raw product (1–25). |
| **Priority band** | derived | P0 = 20–25; High = 15–19; Medium = 9–14; Backlog ≤ 8. |
| **Tie-break** | — | Prefer items that reduce Jules quota waste or disposition mis-pipe first; then items that enable context_key persistence. |

**Update rule:** When an OPERATOR agent changes scores or adds rows, append a changelog entry at the bottom with:
- ISO date
- Session id / message id (or PR comment id)
- Brief reason
- Signature: `Signed-off-by: <Agent> (OPERATOR) <session-or-message-id>`

## Current matrix (2026-08-10)

| Item | Impact | Importance | Score | Band | Action |
|------|--------|------------|-------|------|--------|
| **#120** durable work-context store | 5 | 5 | **25** | **P0 root** | Clear remaining blockers → merge (enables #145 context_key) |
| **#145** Jules session binding (context_key + continue-only) | 5 | 5 | **25** | **P0** | Wire load/save into `agent-review-auto-jules.yml` + `agent-continuous-ops.yml` after #120 |
| **#146** disposition vs analysis-chain alignment | 4 | 5 | **20** | High | Excerpt builders + continuous-ops templates cite disposition only |
| **#126** Linguist / CedrLang | 4 | 4 | **16** | High-ROI | Continue *existing* Jules session only; disposition-driven; rebase if dirty |
| **#143** MCP Agent Mail bus | 4 | 4 | **16** | Coordination | Keep parallel |
| **#118** Session & Context (parent of #120) | 5 | 4 | **20** | Track via #120 | Linked |

## Security note (public demo repo)

`context_key` / work-context persistence may live in Actions cache or a lightweight session_store. Until an encrypted store lands:

- **Viewable text is an acceptable security policy** for non-secret context keys (PR id, branch, last Jules task id, disposition citation).
- **Never** persist Class 3/4 material (tokens, cookies, PoW, browser profiles) — see AGENTS.md hard rules.
- Flag any scanner alerts; document the intentional public-demo exception in the PR that introduces the store.

## Related

- `docs/ops/OPERATOR-SIGNING.md` — mandatory signature format
- `#145`, `#146`, `#120`, `#118`, `#90`
- PR `#126` operator comments (matrix origin)

## Changelog

- 2026-08-10 — Initial living matrix + refined scoring. Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-matrix-init
