# Provider Routing Resource Contract

## Scope

This directory is the repository-native ICM workspace for **routing observations and governance**. It is nested under `docs/icm/` because provider availability, quota posture, and related issue/PR context evolve more frequently than the root ICM catalog.

> **It is not the runtime router.** The current executable routing configuration, workflows, secrets, and provider invocation paths remain external to this documentation workspace and are not modified by this contract.

## Canonical-source hierarchy

| Question | Canonical source | This resource may do | This resource must not do |
|---|---|---|---|
| Which provider records exist? | `.github/connectors/llm-peers.yaml` | Link and summarize source identity. | Duplicate a runtime model catalog as authoritative. |
| Which workflow chooses or invokes a provider? | Current `.github/workflows/` and their reviewed PR history | Link scope and review state. | Change a workflow, secret, trigger, or permission. |
| Which strategy and unresolved tasks apply? | Related GitHub issues and pull requests | Maintain a reviewed evidence index. | Treat an issue as approval to execute. |
| What did an approved observer find? | `providers/observation-log.md` | Record a redacted observation with timestamp and reviewer. | Store tokens, raw secret-bearing payloads, or route-changing instructions. |
| What should the mobile board show? | Canonical card files under `../_tv/screens/` | Mirror the approved routing state. | Become a write path to runtime configuration. |

## Lifecycle

1. A human first declares the provider source, allowed query, cadence, credentials model, retention limit, failure behavior, and publication audience.
2. A separate approved poller retrieves an observation and writes only a redacted candidate record.
3. A human reviews the record against the canonical source and either marks it `accepted` or `rejected`.
4. The CCTV card may mirror the accepted record for review.
5. Any change to provider execution, workflow logic, model choice, or secrets begins a new code/workflow proposal after this ICM work is complete.

## Default state

| Field | Current value |
|---|---|
| Poller | Not configured |
| Cadence | Not approved |
| Credentials | Not requested or stored here |
| Runtime authority | Existing configuration and workflow implementation outside `docs/icm/` |
| CCTV mirror | File-backed status card only; no renderer started |
| GitHub Pages publication | Not enabled; requires a later reviewed deployment/workflow change |

## Safety and privacy

Provider polling is a future integration, not a documentation side effect. Do not use the Termux MCP or the BLU B160V to poll providers. Do not add a scheduled task, network service, secret, GitHub Action, or application code while updating this resource.
