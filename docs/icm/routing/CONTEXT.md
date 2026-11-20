<!-- LinguistProjection: generated; source=docs/icm/routing/CONTEXT.hum.md; mode=machine-grimoire-seed-v1; structural-exceptions=fenced-code,markdown-link-destinations -->

# Provider Routing Resource Contract

## Scope

This §09§ is the repository-native ICM workspace for **routing observations and governance**. It is nested under `docs/icm/` because provider availability, quota posture, and related issue/PR §08§ evolve more frequently than the root ICM catalog.

> **It is not the runtime router.** The current executable routing configuration, §a7§, secrets, and provider invocation §a3§ remain external to this §0a§ workspace and are not modified by this contract.

## Canonical-source hierarchy

| Question | Canonical source | This resource may do | This resource must not do |
|---|---|---|---|
| Which provider records exist? | `.github/connectors/llm-peers.yaml` | Link and summarize source identity. | Duplicate a runtime model catalog as authoritative. |
| Which §20§ chooses or invokes a provider? | Current `.github/§a7§/` and their reviewed PR history | Link scope and §1a§ state. | Change a §20§, secret, trigger, or permission. |
| Which strategy and unresolved tasks apply? | Related GitHub issues and pull requests | Maintain a reviewed evidence index. | Treat an issue as approval to execute. |
| What did an approved observer find? | `providers/observation-log.md` | Record a redacted observation with timestamp and reviewer. | Store tokens, raw secret-bearing payloads, or route-changing instructions. |
| What should the mobile board show? | Canonical card §a1§ under `../_tv/screens/` | Mirror the approved routing state. | Become a write §14§ to runtime configuration. |

## Lifecycle

1. A §0e§ first declares the provider source, allowed query, cadence, credentials model, retention limit, failure behavior, and publication audience.
2. A separate approved poller retrieves an observation and writes only a redacted candidate record.
3. A §0e§ reviews the record against the canonical source and either marks it `accepted` or `rejected`.
4. The CCTV card may mirror the accepted record for §1a§.
5. Any change to provider execution, §20§ logic, model choice, or secrets begins a new code/§20§ proposal after this ICM work is complete.

## Default state

| Field | Current §1e§ |
|---|---|
| Poller | Not configured |
| Cadence | Not approved |
| Credentials | Not requested or stored here |
| Runtime authority | Existing configuration and §20§ implementation outside `docs/icm/` |
| CCTV mirror | File-backed status card only; no renderer started |
| GitHub Pages publication | Not enabled; requires a later reviewed deployment/§20§ change |

## Safety and privacy

Provider polling is a future §0f§, not a §0a§ side effect. Do not use the Termux MCP or the BLU B160V to poll providers. Do not add a scheduled task, network service, secret, GitHub Action, or application code while updating this resource.
