# Skills Inventory (termux-monorepo)

**Version:** 2026-09-21 15:07 PDT · **Master tip:** post-skill-extract
**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)
**Collaborator short entry:** [`SKILLS.md`](../../SKILLS.md)

## Collaborator access (parity)

All skills below are **in-repo** under `.agents/skills/` or `.github/skills/`.
Local agent mirrors (e.g. `.grok/skills/`) are convenience only — **not** a second policy source.

| Entry | Purpose |
|-------|---------|
| [`SKILLS.md`](../../SKILLS.md) | Short collaborator pointer |
| This file | Full inventory + role matrix |
| Each `**/SKILL.md` | Executable skill body |

## Role load matrix

| Role | Load first | Then |
|------|------------|------|
| **Admin / Grok Administrator** | `evidence-led-monorepo-ops` + `adaptive-wait` + **`stepie-stepwise-ops`** | `review-loop` · `help-wanted-lane` · `github-pages-operator` · `approxination-lane` |
| **Collaborator** | `adaptive-feedback-cycle` | dual-gate · `find-skills` |
| **Oversight / external contrib** | `help-wanted-lane` | evidence-led + adaptive-wait · living status board |
| **Dashboard / Pages** | `github-pages-operator` | help-wanted-lane · deploy workflow |
| **Evaluation / DOE** | `multivariate-doe` + `blind-agent-evaluation` | `approxination-lane` · `mvt-experiment` |
| **CI / production recon** | `production-reconciliation` | `action-effectiveness-ledger` · `workflow-orchestration` |

## `.agents/skills/` (agent loadable)

| Skill | Path |
|-------|------|
| adaptive-feedback-cycle | `.agents/skills/adaptive-feedback-cycle/SKILL.md` |
| adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` |
| approxination-lane | `.agents/skills/approxination-lane/SKILL.md` |
| blind-agent-evaluation | `.agents/skills/blind-agent-evaluation/SKILL.md` |
| context-relationship-graph | `.agents/skills/context-relationship-graph/SKILL.md` |
| evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| find-skills | `.agents/skills/find-skills/SKILL.md` |
| gemini-performance-psychology | `.agents/skills/gemini-performance-psychology/SKILL.md` |
| github-pages-operator | `.agents/skills/github-pages-operator/SKILL.md` |
| help-wanted-lane | `.agents/skills/help-wanted-lane/SKILL.md` |
| multivariate-doe | `.agents/skills/multivariate-doe/SKILL.md` |
| review-loop | `.agents/skills/review-loop/SKILL.md` |
| **stepie-stepwise-ops** | `.agents/skills/stepie-stepwise-ops/SKILL.md` |
| termux-monorepo | `.agents/skills/termux-monorepo/SKILL.md` |
| termux-monorepo-agentic-governance | `.agents/skills/termux-monorepo-agentic-governance/SKILL.md` |

## `.github/skills/` (CI / production)

| Skill | Path |
|-------|------|
| action-effectiveness-ledger | `.github/skills/action-effectiveness-ledger/SKILL.md` |
| evidence-envelope | `.github/skills/evidence-envelope/SKILL.md` |
| evidence-provenance | `.github/skills/evidence-provenance/SKILL.md` |
| forensic-recovery | `.github/skills/forensic-recovery/SKILL.md` |
| github-pages-operator | `.github/skills/github-pages-operator/SKILL.md` |
| mvt-experiment | `.github/skills/mvt-experiment/SKILL.md` |
| pr-evidence-evaluation | `.github/skills/pr-evidence-evaluation/SKILL.md` |
| production-reconciliation | `.github/skills/production-reconciliation/SKILL.md` |
| workflow-orchestration | `.github/skills/workflow-orchestration/SKILL.md` |

## Help-wanted companion docs

| Doc | Role |
|-----|------|
| [`HELP-WANTED-LANE.md`](HELP-WANTED-LANE.md) | Production execute |
| [`HELP-WANTED-PARALLEL.md`](HELP-WANTED-PARALLEL.md) | Roster + limits |
| [`HELP-WANTED-STATUS.md`](HELP-WANTED-STATUS.md) | Living human-review surface |
| [`HELP-WANTED-DASHBOARD.md`](HELP-WANTED-DASHBOARD.md) | Live surfaces + deploy |
| [`HELP-WANTED-EVIDENCE-FEED.md`](HELP-WANTED-EVIDENCE-FEED.md) | Receipts → evaluation |

## Cycle snapshot (2026-09-21 15:07 PDT)

- New skill: **stepie-stepwise-ops** — Stepie as production planning surface (goal 2087).
- Preferred extract: #713 slim ML pipelines; #682 remains EXTRACT/WAIT.
- Dual-gate contract unchanged; Vercel rate-limit non-gate.
- Credential inventory: issue **#184** (notes only; no secret values).

Agent-Identity: Grok (Administrator)
