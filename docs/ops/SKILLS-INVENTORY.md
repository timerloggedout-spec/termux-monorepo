# Skills Inventory (termux-monorepo)

**Version:** 2026-09-23 · Wingman + session skill adoption
**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)
**Collaborator short entry:** [`SKILLS.md`](../../SKILLS.md)

## Role load matrix

| Role | Load first | Then |
|---|---|---|
| Admin / stewardship | `termux-mcp-project-steward` + `evidence-led-monorepo-ops` | `adaptive-wait` · `context-relationship-graph` |
| Collaborator | `adaptive-feedback-cycle` | dual-gate · `find-skills` |
| Wingman adaptation | `wingman-project-integration` | `adaptive-wait` · `context-relationship-graph` |
| Oversight / external contrib | `help-wanted-lane` | evidence-led + adaptive-wait |
| Evaluation / DOE | `multivariate-doe` + `blind-agent-evaluation` | `approxination-lane` |
| CI / production recon | `production-reconciliation` | `action-effectiveness-ledger` · `workflow-orchestration` |

## `.agents/skills/` (agent loadable)

| Skill | Path |
|---|---|
| adaptive-feedback-cycle | `.agents/skills/adaptive-feedback-cycle/SKILL.md` |
| adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` |
| approxination-lane | `.agents/skills/approxination-lane/SKILL.md` |
| blind-agent-evaluation | `.agents/skills/blind-agent-evaluation/SKILL.md` |
| context-relationship-graph | `.agents/skills/context-relationship-graph/SKILL.md` |
| evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| evolutionary-replay | `.agents/skills/evolutionary-replay/SKILL.md` |
| find-skills | `.agents/skills/find-skills/SKILL.md` |
| gemini-performance-psychology | `.agents/skills/gemini-performance-psychology/SKILL.md` |
| github-pages-operator | `.agents/skills/github-pages-operator/SKILL.md` |
| help-wanted-lane | `.agents/skills/help-wanted-lane/SKILL.md` |
| multivariate-doe | `.agents/skills/multivariate-doe/SKILL.md` |
| review-loop | `.agents/skills/review-loop/SKILL.md` |
| skill-evaluation | `.agents/skills/skill-evaluation/SKILL.md` |
| termux-mcp-project-steward | `.agents/skills/termux-mcp-project-steward/SKILL.md` |
| termux-monorepo | `.agents/skills/termux-monorepo/SKILL.md` |
| termux-monorepo-agentic-governance | `.agents/skills/termux-monorepo-agentic-governance/SKILL.md` |
| wingman-project-integration | `.agents/skills/wingman-project-integration/SKILL.md` |

## `.github/skills/`

Existing CI/production skills remain authoritative for CI execution, evidence, reconciliation, and workflow orchestration.

## Submodule template

`refTemplates/smods/Wingman_fork` is the pinned Wingman reference/customization source. See [`docs/ops/WINGMAN-FORK-INTEGRATION.md`](WINGMAN-FORK-INTEGRATION.md).

## Session adoption

The supplied steward and context-relationship skill packages were adopted into checked-in `SKILL.md` surfaces. The supplied Loopy material was adapted for loop semantics only; it is not an external policy dependency.
