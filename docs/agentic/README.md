# Dependency-Phase Automation

This directory contains a **repository-native lifecycle system** for dependency-ordered work. It integrates the canonical phase plan with GitHub Project #1, pull-request/check evidence, explicit approvals, idempotent claims, and GitHub Actions workflows.

> **Authority rule:** `dependency-phases.json`, current pull-request/check evidence, explicit approval evidence, and GitHub Project items jointly determine lifecycle state. Mermaid, Markdown, DeepWiki, dashboards, issue prose, and collaborator-generated summaries are derived views only.

## Navigation SSOT (start here)

| Need | Path |
|---|---|
| **This README** | Operator / Collaborator entry for the phase system |
| Canonical plan | [`dependency-phases.json`](dependency-phases.json) |
| Generated status (do not edit) | [`DEPENDENCY_PHASES.md`](DEPENDENCY_PHASES.md) · [`dependency-phases.mmd`](dependency-phases.mmd) |
| Proposal + ITEMS | [`../proposals/active/gantt-dependency-phases/`](../proposals/active/gantt-dependency-phases/) |
| Historical design | [`../GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md`](../GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md) |
| Template / PM catalog (inspiration) | [`PROJECT-MANAGEMENT-TEMPLATE-CATALOG.md`](PROJECT-MANAGEMENT-TEMPLATE-CATALOG.md) |
| Primary repo entry | [`../../CLAUDE.md`](../../CLAUDE.md) — **not** root `AGENTS.md` (deprecated) |

## Components

| Path | Purpose |
|---|---|
| `dependency-phases.json` | Canonical phase IDs, dependencies, required checks, policy, and live Project metadata. |
| `phase-approvals.json` | Explicit human approval evidence for phases that require it. An empty object means no approval. |
| `scripts/agentic/dependency_phase_engine.py` | Pure offline validator, evaluator, and Mermaid/Markdown renderer. |
| `scripts/agentic/github_phase_adapter.py` | Live GitHub CLI adapter for Project evidence, reconciliation, and claim records. |
| `scripts/agentic/dependency_phases.py` | Command-line interface for all lifecycle operations. |
| `DEPENDENCY_PHASES.md` / `dependency-phases.mmd` | Generated inspection views. Never edit as canonical state. |
| `.github/workflows/dependency-phase-*.yml` | Validation, read-only evaluation, manual Project sync, and controlled dispatch workflows. |

## Automations (live)

| Workflow | Role |
|---|---|
| `dependency-phase-validate.yml` | Schema / DAG / fixture validation (read-only; PR + dispatch) |
| `dependency-phase-evaluate.yml` | Read-only evaluation + artifact upload (schedule + dispatch) |
| `dependency-phase-project-sync.yml` | Dry-run default Project reconciliation; `--apply` only with Operator token |
| `dependency-phase-dispatch.yml` | Controlled claim + optional Jules handoff (`repository_dispatch` / manual) |

## Lifecycle rules

| State | Definition | Permitted behavior |
|---|---|---|
| `waiting` | A dependency is not complete. | Report only. |
| `blocked` | Approval evidence is missing or Project/PR evidence is contradictory. | Report only. |
| `ready` | Dependencies complete, approvals present, no active claim, and no contradictory evidence. | A controlled workflow may create one claim. |
| `running` | Linked PR or idempotency claim is active. | Observe; never launch duplicate work. |
| `awaiting_review` | Linked PR has current required checks but is not merged. | Existing review process owns the next action. |
| `complete` | A matching merged PR, required checks, and Project `Done` status agree. | Unlock dependent evaluation only. |

A phase cannot become `complete` based solely on a GitHub Project card, a collaborator comment, or a Mermaid node. A project item marked `Done` without a matching merged PR is intentionally reported as `blocked`.

## Local commands

All commands run from the repository root. The core engine uses only the Python standard library; live GitHub operations require the authenticated `gh` CLI.

```bash
# Validate canonical phase structure and dependency graph.
python3 scripts/agentic/dependency_phases.py validate

# Run the full unit test suite for lifecycle rules.
python3 -m unittest tests/test_dependency_phase_engine.py

# Evaluate a reproducible fixture and write the graph/report views.
python3 scripts/agentic/dependency_phases.py \
  --snapshot tests/fixtures/dependency_phases/ready.json \
  render

# Read current GitHub Project and PR evidence; no write occurs.
python3 scripts/agentic/dependency_phases.py \
  --live --repo timerloggedout-spec/termux-monorepo evaluate

# Show the exact Project issue/status operations that would be performed.
python3 scripts/agentic/dependency_phases.py \
  --live --repo timerloggedout-spec/termux-monorepo sync-project

# Apply Project reconciliation only after reviewing the dry-run output.
python3 scripts/agentic/dependency_phases.py \
  --live --apply --repo timerloggedout-spec/termux-monorepo sync-project
```

## GitHub Project integration

The canonical plan records the verified target metadata for the user-owned Project #1. Phase issues are mapped by their stable title marker such as `[DPH-100]`. Project statuses are a derived synchronization target:

| Lifecycle state | Project status |
|---|---|
| `waiting`, `blocked`, `ready` | `Todo` |
| `running`, `awaiting_review` | `In progress` |
| `complete` | `Done` |

The adapter defaults to dry run. `sync-project --apply` is the only command that creates phase issues, adds them to the Project, or updates Project status. It must use a token with repository **Issues read/write** and **Projects read/write** access.

### Credential routing (#184 names-only)

Issue **#184** is the credential inventory SSOT (names and last-used only — never secret values). Classic Operator PATs in that inventory have long included the `project` scope. Live Project writes therefore use the existing Operator-token precedence (not a missing capability):

`ARCHWIZ_GITHUB_TOKEN` → `OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `GITHUB_TOKEN`

Wire the intended Operator credential as a **repository secret** when Project apply is required. Do not paste values into issues or PRs.

## Approval evidence

For an approval-required phase, make the smallest reviewed edit to `phase-approvals.json`:

```json
{
  "approvals": {
    "DPH-100": {
      "approved": true,
      "by": "timerloggedout-spec",
      "evidence": "<PR, issue, or decision link>"
    }
  }
}
```

The lifecycle engine reads only the boolean `approved` as a gate. The `by` and `evidence` fields are audit context, not inferred approval.

## Controlled dispatch

The `dispatch` command and corresponding workflow **re-evaluate live evidence immediately before creating a claim**. The claim key is `PHASE_ID:PLAN_SHA256`, stored in a GitHub issue comment marker. A duplicate event for the same plan revision becomes a no-op. A revised canonical plan intentionally creates a new key and requires current evidence to remain valid.

```bash
# Dry-run claim decision: no GitHub write.
python3 scripts/agentic/dependency_phases.py \
  --live --repo timerloggedout-spec/termux-monorepo \
  dispatch --phase-id DPH-100 --issue 123

# Record one claim only after the dry-run has been reviewed.
python3 scripts/agentic/dependency_phases.py \
  --live --apply --repo timerloggedout-spec/termux-monorepo \
  dispatch --phase-id DPH-100 --issue 123
```

The GitHub Actions dispatcher may invoke Jules only after a successful applied claim and only when `JULES_API_KEY` is configured. It does not merge PRs, close proposals, update submodules, or grant approvals.

## Workflow setup

| Secret (name only — #184) | Required by | Purpose |
|---|---|---|
| `ARCHWIZ_GITHUB_TOKEN`, `OPERATOR_GITHUB_TOKEN`, or `OPERATOR_TOKEN` | Live evaluation, Project synchronization, and dispatch revalidation | First configured Operator credential wins; `GITHUB_TOKEN` is final fallback. Selected credential needs Issues + Projects access on the user-owned Project. |
| `JULES_API_KEY` | Optional final step of applied dispatch | Existing Jules integration secret; no value means the claim is recorded but no collaborator is invoked. |

The validation workflow has no secrets and remains read-only. The evaluator is scheduled daily and can be manually run; it uploads derived artifacts rather than committing them. Project sync is manual and dry-run by default. Dispatch is manual or a controlled repository event, never a pull-request event from untrusted code.

## Required checks before merge

```bash
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
python3 scripts/agentic/dependency_phases.py validate
python3 -m unittest tests/test_dependency_phase_engine.py
```

## Naming

Collaborators are addressed by **Role**, **Name**, and **Moniker**. Root `AGENTS.md` is a deprecated redirect (Linguist / CedrLang / Jules compression only). Primary entry is always [`CLAUDE.md`](../../CLAUDE.md).

## Upgrade note (2026-09-25)

Docs consolidated for navigation, status accuracy, Collaborator naming, and #184 Projects-access clarity. Runtime behavior unchanged. See proposal MANIFEST review log for evidence trail.
