# Skills Inventory (termux-monorepo)

**Version:** 2026-09-19 · **Master tip:** post-#640 neighbor-safe help-wanted  
**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)  
**Collaborator short entry:** [`SKILLS.md`](../../SKILLS.md)

Root `AGENTS.md` is **removed**. Do not recreate it as a second governance file.

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
| **Admin / Grok Administrator** | `evidence-led-monorepo-ops` + `adaptive-wait` | `review-loop` · `help-wanted-lane` · `github-issue-pr-graph` · `approxination-lane` · `production-reconciliation` |
| **Collaborator** | `adaptive-feedback-cycle` | dual-gate · `find-skills` |
| **Oversight / external contrib** | `help-wanted-lane` | evidence-led + adaptive-wait · living status board |
| **Issue/PR graph** | `github-issue-pr-graph` | `context-relationship-graph` · `review-loop` |
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
| github-issue-pr-graph | `.agents/skills/github-issue-pr-graph/SKILL.md` |
| help-wanted-lane | `.agents/skills/help-wanted-lane/SKILL.md` |
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
| [`HELP-WANTED-EVIDENCE-FEED.md`](HELP-WANTED-EVIDENCE-FEED.md) | Receipts → evaluation |
| generated board | `docs/ops/generated/help-wanted-status.md` |

## Routing / orchestration pointers

| Need | Path |
|------|------|
| Three-plane map | [`ROUTING-ORCHESTRATION-MAP.md`](ROUTING-ORCHESTRATION-MAP.md) |
| Model rotation | [`docs/schemas/model-rotation.yaml`](../schemas/model-rotation.yaml) |
| Provider caps | [`docs/schemas/provider-capabilities.md`](../schemas/provider-capabilities.md) |
| Approxination ops | [`APPROXINATION-LANE.md`](APPROXINATION-LANE.md) |
| DeepSeek invoke | [`DEEPSEEK-CI.md`](DEEPSEEK-CI.md) |
| Agent monikers | [`AGENT-MONIKERS.md`](AGENT-MONIKERS.md) |

## Cycle snapshot (2026-09-19)

- **#638 MERGED:** LIVE help-wanted contribute (fork-ready, FALLBACK notice).
- **#640 MERGED:** neighbor-safe — idempotent claims, skip closed, living status board.
- Proven PRIMARY: DioNanos/codex-termux PR #27 (do **not** re-claim closed #14); Haven PR #657.
- Maintainer routing (codex-termux): parity only; logic → upstream; features → [codex-vl](https://github.com/DioNanos/codex-vl).
- Dual-gate still required for monorepo merges. External PRs follow target norms.
- **This cycle:** add `github-issue-pr-graph`; fold and delete root `AGENTS.md`.

BIUDL. Agent-Identity: Grok (Administrator)
