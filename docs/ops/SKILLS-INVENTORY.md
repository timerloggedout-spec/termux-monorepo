# Skills Inventory (termux-monorepo)

**Version:** 2026-09-25 14:10 PDT · **Master tip:** `a3423d97`
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
| **Admin / Grok Administrator** | `evidence-led-monorepo-ops` + `adaptive-wait` + `ml-pipeline-ops` | `review-loop` · `help-wanted-lane` · `github-pages-operator` · `icm-cctv-ops` |
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
| **github-pages-operator** | `.agents/skills/github-pages-operator/SKILL.md` |
| help-wanted-lane | `.agents/skills/help-wanted-lane/SKILL.md` |
| **icm-cctv-ops** | `.agents/skills/icm-cctv-ops/SKILL.md` |
| **ml-pipeline-ops** | `.agents/skills/ml-pipeline-ops/SKILL.md` |
| multivariate-doe | `.agents/skills/multivariate-doe/SKILL.md` |
| review-loop | `.agents/skills/review-loop/SKILL.md` |
| termux-monorepo | `.agents/skills/termux-monorepo/SKILL.md` |
| termux-monorepo-agentic-governance | `.agents/skills/termux-monorepo-agentic-governance/SKILL.md` |

## `.github/skills/` (CI / production)

| Skill | Path |
|-------|------|
| action-effectiveness-ledger | `.github/skills/action-effectiveness-ledger/SKILL.md` |
| evidence-envelope | `.github/skills/evidence-envelope/SKILL.md` |
| evidence-provenance | `.github/skills/evidence-provenance/SKILL.md` |
| forensic-recovery | `.github/skills/forensic-recovery/SKILL.md` |
| **github-pages-operator** | `.github/skills/github-pages-operator/SKILL.md` |
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

## Cycle snapshot (2026-09-19 17:26 PDT)

- Live master: `826dc1e4`.
- #655: dual-gate jobs green; Vercel hobby rate-limit non-gate; base lag vs tip.
- HOLD dirty: #648, #641. Observe Jules: #649, #657.
- ML: keep #432/#601 extract-only (Issue #175).
- Prefer GitHack over jsDelivr for HTML (MIME).
- Credential inventory: issue **#184** (notes only; no secret values).

Agent-Identity: Grok (Administrator)


## Adaptive-wait + evidence-led cluster

- adaptive-wait — evidence-driven asynchronous cadence, stall detection, disjoint work, terminal states.
- evidence-led-monorepo-ops — current-SHA reconstruction, evidence hierarchy, provenance, mutation/promotion discipline.
- context-relationship-graph — exact-root metadata-only relationship evidence; verified/candidate separation.
- review-loop — review ingestion and attribution.
- production-reconciliation — ref/base reconciliation.
- action-effectiveness-ledger — action-to-outcome measurement.
- evidence-envelope + evidence-provenance — normalized observation identity.
- workflow-orchestration — modular Actions and retry/stale-event discipline.

See `docs/ops/SKILL-DISCOVERY-MATRIX.md` for focused discovery and session-scoped .skill provenance.
