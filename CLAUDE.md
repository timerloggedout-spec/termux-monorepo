# CLAUDE.md — Primary collaborator route

This human source pairs with the root Claude instruction surface. `scripts/cedrlang/render_contact_projections.py` projects the source byte-for-byte until a reversible notation receives approval and round-trip evidence.

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

Load the root collaborator route first. Then follow [`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md) to one owning ICM card and its cited sources. Each ICM machine alias keeps its own sibling human source and byte-identical local content.

## Governance route

1. Read [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) to identify active work.
2. Follow [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) for proposal lifecycle.
3. Apply [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) at human-authority boundaries.
4. Use [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) for promotion evidence.
5. Read [`docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md`](docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md) and the canonical Siglary/Matrice links it names.
6. Use [`docs/proposals/active/notation-sets/SIGLARY-STANDARD.md`](docs/proposals/active/notation-sets/SIGLARY-STANDARD.md), [`docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md`](docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md), and [`scripts/ci/validate_siglary_mandate.py`](scripts/ci/validate_siglary_mandate.py) for canonical mapping and enforcement.

## Execution contract

- Target `master` for integration work; use `master-staging` when the active lane names it.
- Run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py` before promotion.
- Register implementation scope in `docs/proposals/active/<id>/ITEMS.md` before execution.
- Cite `Implements: <ITEM-ID>` in commits and pull requests.
- Extract independently reviewable work from mega-PRs #2 and #6 when their status is `GO=FALSE`.
- Route credentials, history rewrites, and Class 3/4 material through the human-only permissions in `docs/proposals/AGENTIC-PERMISSIONS.md`.
- Record credential names in issue #184; retain secret values in approved secret storage.
- Record consensus through a Review log or `DEBATE.md`.
- Promote when both required gates pass on the exact candidate SHA and the task outcome is verified.

## Operating motion

Use BIUDL: Broad → Integrate → Validate → Develop → Learn. Execute authorized work to a verified outcome, run non-conflicting work during WAIT, and re-fetch evidence before promotion. Keep each change reviewable and cite its source, test, or run.

The session and lane source of truth is [`docs/ops/LANE-MATRIX.md`](docs/ops/LANE-MATRIX.md). The ICM chart is [`docs/architecture/AGENT-TEAM-CONTROL-PLANE.md`](docs/architecture/AGENT-TEAM-CONTROL-PLANE.md). Reference pins live under `refTemplates/smods/` and remain read-only inputs.
