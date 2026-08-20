# Dependency-Phase Automation Source

## Objective

Build a complete dependency-phase lifecycle system for `termux-monorepo`. The system must coordinate repository work in phases, reflect the current GitHub Project, prevent duplicate agent work, and expose a readable dependency graph without granting a visualization or an agent comment authority over the repository.

## Live integration target

The verified target is the user-owned GitHub Project at `https://github.com/users/timerloggedout-spec/projects/1`. At implementation time it has project ID `PVT_kwHODennMc4BfLt5`, 241 items, and a `Status` single-select field with `Todo`, `In progress`, and `Done` options. The canonical plan records those identifiers so reconciliation does not guess them.

## Authority model

| Source | Authority |
|---|---|
| `docs/agentic/dependency-phases.json` | Canonical phase definitions, dependencies, policy, and GitHub Project metadata. |
| Pull requests/checks plus GitHub Project item state | Objective lifecycle evidence. |
| `docs/agentic/phase-approvals.json` | Explicit human approval evidence for approval-required phases. |
| Issue comments with an idempotency marker | Agent claim record only. |
| Mermaid, Markdown, dashboards, DeepWiki, and project charts | Derived views only. |

## Required safety properties

The implementation must fail closed on invalid or cyclic dependencies; require current live evidence before claims or project writes; default all GitHub mutations to dry run; use a plan-hash idempotency key; and never auto-merge pull requests, close proposals, update submodules, or infer human approvals.

## Full implementation scope

The implementation includes the local engine, tests, GitHub adapter, canonical plan, approvals file, Project reconciliation, claim workflow, validation workflow, scheduled/manual report workflow, generated Mermaid/Markdown artifacts, and user/agent documentation. Actual project writes and agent invocation are enabled only by explicit workflow/manual inputs or an explicit CLI `--apply` command.
