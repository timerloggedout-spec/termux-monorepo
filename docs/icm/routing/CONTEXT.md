# Provider Routing Resource Contract

## Scope

This directory is the repository-native ICM workspace for **routing observations and governance**. It is nested under `docs/icm/` because provider availability, quota posture, and related issue/PR context evolve more frequently than the root ICM catalog.

The resource documents routing governance. Executable routing configuration, workflows, secrets, and provider invocation paths remain in their existing runtime locations.

## Canonical-source hierarchy

| Question | Canonical source | This resource may do | This resource must not do |
|---|---|---|---|
| Which provider records exist? | `.github/connectors/llm-peers.yaml` | Link and summarize source identity. | Duplicate a runtime model catalog as authoritative. |
| Which workflow chooses or invokes a provider? | Current `.github/workflows/` and their reviewed PR history | Link scope and review state. | Change a workflow, secret, trigger, or permission. |
| Which strategy and unresolved tasks apply? | Related GitHub issues and pull requests | Maintain a reviewed evidence index. | Treat an issue as approval to execute. |
| What did an approved observer find? | `providers/observation-log.md` | Record a redacted observation with timestamp and reviewer. | Store tokens, raw secret-bearing payloads, or route-changing instructions. |
| What should the mobile board show? | Canonical card files under `../_tv/screens/` | Mirror the approved routing state. | Become a write path to runtime configuration. |

## Lifecycle

1. A human declares the provider source, allowed query, cadence, credentials model, retention limit, failure behavior, and publication audience.
2. A separately approved poller retrieves an observation and writes only a redacted candidate record.
3. A human reviews the record against the canonical source and marks it `accepted` or `rejected`.
4. The CCTV card mirrors the accepted record for review.
5. A change to provider execution, workflow logic, model choice, or secrets begins a new code/workflow proposal after this ICM work is complete.

## Current state

| Field | Current value |
|---|---|
| Poller | Unconfigured |
| Cadence | Awaiting explicit approval |
| Credentials | Governed by the existing runtime owner and secret-management process |
| Runtime authority | Existing configuration and workflow implementation outside this documentation workspace |
| CCTV mirror | Published static status-card board; source cards remain under `docs/icm/_tv/screens/` |
| GitHub Pages publication | Enabled for the static ICM card board through the existing Tribute publisher |
| Response consumer | Unconfigured; the response cage remains reserved for a future human-approved process |

## Safety and privacy

Provider polling remains a future integration that requires explicit human approval. The static board presents reviewed Markdown state and canonical links. The publication workflow generates HTML from repository files and does not add a provider polling path, runtime service, device operation, or routing mutation.

Any provider observer proposal declares its source, query, cadence, credentials model, redaction rule, retention, failure behavior, and human reviewer before implementation.
