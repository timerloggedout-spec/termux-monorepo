# CLAUDE.md — Primary collaborator route

This human source pairs with the root Claude instruction surface. `scripts/linguist/agent_document_pairs.py` applies the per-lane contract; this root pair uses the registered Siglary conjunction/disjunction operators.

## Agent-specific source routes
| Role | Human source | Programmatic route |
|---|---|---|
| Claude | `CLAUDE.hum.md` | `CLAUDE.md` |
| Gemini | `GEMINI.hum.md` | `GEMINI.md` |
| Codex | `.codex/AGENTS.hum.md` | `.codex/AGENTS.md` |
| ICM Claude | `docs/icm/CLAUDE.hum.md` | `docs/icm/CLAUDE.md` |
| ICM AGENTS | `docs/icm/AGENTS.hum.md` | `docs/icm/AGENTS.md` |
| ICM maintenance Claude | `docs/icm/maintenance/CLAUDE.hum.md` | `docs/icm/maintenance/CLAUDE.md` |
| ICM maintenance AGENTS | `docs/icm/maintenance/AGENTS.hum.md` | `docs/icm/maintenance/AGENTS.md` |

## Siglary name mapping

The notation system's name of record is **Siglary**, per [the Notation Matrice](docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md) ∧ [the Siglary Standard](docs/proposals/active/notation-sets/SIGLARY-STANDARD.md). Retain `CAVEMAN-MICRO-DENSE-V2.md` as the legacy Matrice path. Treat the superseded working title “Caveman Micro Dense 🧬 v2” ∧ the other repositories’ proper names “Caveman” ∧ “CEDRLang” as prior art.

For each nontrivial change, begin with [context-relationship reconnaissance](docs/icm/processes/context-relationship-reconnaissance.md) ∧ the [context-relationship graph skill](.agents/skills/context-relationship-graph/SKILL.md). Build verified evidence, then label scored **candidates** separately. Route ICM work through [`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md), its owning ICM card, and cited sources; each machine alias keeps its own sibling human source ∧ byte-identical local content.

## Governance route

1. Read [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) to identify active work.
2. Follow [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) for proposal lifecycle.
3. Apply [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) at human-authority boundaries.
4. Use [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) for promotion evidence.
5. Read [`docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md`](docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md) ∧ the canonical Siglary/Matrice links it names.
6. Use [`docs/proposals/active/notation-sets/SIGLARY-STANDARD.md`](docs/proposals/active/notation-sets/SIGLARY-STANDARD.md), [`docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md`](docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md), and [`scripts/ci/validate_siglary_mandate.py`](scripts/ci/validate_siglary_mandate.py) for canonical mapping ∧ enforcement.

## Execution contract

- Target `master` for integration work; use `master-staging` when the active lane names it.
- Run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/validate_siglary_mandate.py --base origin/master` before promotion. Run `python3 scripts/ci/termux_smoke.py` when `scripts/ci/gate_admission.py` admits the changed paths or when manually dispatched; unavailable diff evidence admits smoke.
- Register implementation scope in `docs/proposals/active/<id>/ITEMS.md` before execution.
- Cite `Implements: <ITEM-ID>` in commits ∧ pull requests.
- Extract independently reviewable work from mega-PRs #2 ∧ #6 when their status is `GO=FALSE`.
- Route credentials, history rewrites, and Class 3/4 material through the human-only permissions in `docs/proposals/AGENTIC-PERMISSIONS.md`.
- Record credential names in issue #184; retain secret values in approved secret storage.
- Record consensus through a Review log ∨ `DEBATE.md`.
- Apply Fully Automated Agentic Development (FA-ADE): auto-promote when repo-gate and the Siglary validator pass on the exact candidate SHA, plus Termux smoke when the shared path classifier requires it; record `SKIPPED` with reason for other slices.

## Operating motion

Use BIUDL: Broad then Integrate then Validate then Develop then Learn. Execute authorized work to a verified outcome, run non-conflicting work during WAIT, and re-fetch evidence before promotion. Keep each change reviewable ∧ cite its source, test, or run.

The session ∧ lane source of truth is [`docs/ops/LANE-MATRIX.md`](docs/ops/LANE-MATRIX.md). The ICM chart is [`docs/architecture/AGENT-TEAM-CONTROL-PLANE.md`](docs/architecture/AGENT-TEAM-CONTROL-PLANE.md). Reference pins live under `refTemplates/smods/` ∧ remain read-only inputs.
