# Skills Inventory (termux-monorepo)

**Version:** 2026-09-18 · **Last refreshed SHA:** post-#614 (`a55a5689`)
**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)

## Role load matrix

| Role | Load first | Then |
|------|------------|------|
| **Admin / Grok Administrator** | `evidence-led-monorepo-ops` + `adaptive-wait` | `review-loop` · `help-wanted-lane` · `approxination-lane` |
| **Collaborator** | `adaptive-feedback-cycle` | dual-gate |
| **Oversight / external contrib** | `help-wanted-lane` | evidence-led + adaptive-wait · `approxination-lane` |
| **Evaluation / DOE** | `multivariate-doe` + `blind-agent-evaluation` | `approxination-lane` |

## Active ops skills

| Skill | Path |
|-------|------|
| evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` |
| help-wanted-lane | `.agents/skills/help-wanted-lane/SKILL.md` |
| approxination-lane | `.agents/skills/approxination-lane/SKILL.md` |

## Routing / orchestration pointers (post-#611)

| Need | Path |
|------|------|
| Three-plane map (review / chat / MCP) | [`docs/ops/ROUTING-ORCHESTRATION-MAP.md`](ROUTING-ORCHESTRATION-MAP.md) |
| Model rotation + free-tier policy | [`docs/schemas/model-rotation.yaml`](../schemas/model-rotation.yaml) |
| Provider capability matrix | [`docs/schemas/provider-capabilities.md`](../schemas/provider-capabilities.md) |
| MCP host catalog (incl. bifrost evaluation) | `mcp-hub/catalog.json` |
| Bifrost proposal | `docs/proposals/active/bifrost-gateway-integration/` |
| BIFROST-006 runbook | `docs/proposals/active/bifrost-gateway-integration/BENCHMARK-SMOKE.md` |
| Approxination A/B/C/D cohort | `docs/evaluations/approxination/COHORT.md` |
| Approxination ops | [`docs/ops/APPROXINATION-LANE.md`](APPROXINATION-LANE.md) |

## Cycle snapshot (2026-09-18)

- Help-wanted lane: skill + CPPH + scout + execute workflows; upstream vedantnimbarte/zero#81 shipped.
- **#611 MERGED:** Bifrost integration slice. No Bifrost source merge.
- **#613 MERGED:** BIFROST-006 benchmark smoke runbook (results still pending).
- **#614 MERGED:** Approxination skill + A/B/C/D cohort + registry/inventory/fork pins (APPROX-001–004 done; gitlink + formal smoke backlog).
- Dual-gate still required for merge to master. Ledger intermittent (#608 class) is not dual-gate alone.
- Vercel deploy rate-limit observed on some PRs — non-blocking for docs/skills when gates green.

BIUDL. Agent-Identity: Grok (Administrator)
