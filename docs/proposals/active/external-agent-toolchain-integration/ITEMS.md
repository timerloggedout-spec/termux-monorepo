# ITEMS — external-agent-toolchain-integration

| ID | Work | Priority | Owner | Status | Evidence / acceptance criteria |
|---|---|---:|---|---|---|
| EATI-001 | Establish a names-only capability and evidence matrix for the requested tools and their current ChatGPT/repository surfaces. | P1 | ChatGPT | proposed | Each row separates tool availability, repo wiring, authorization, runtime reachability, successful outcome, and publication state; unknown is preserved. |
| EATI-002 | Reconcile each capability against CMDB/IDRR, Integration Mesh, ICM, skills inventory, provider routing, MCP catalog, and existing documentation authorities. | P1 | ChatGPT | proposed | Every field has an authority or is explicitly proposed; no duplicate registry, poller, router, scheduler, or telemetry ledger is introduced. |
| EATI-003 | Define a versioned read-only metadata/provenance contract for tool identity, aliases, version/ref, capability, scope, freshness, source evidence, and unknown/stale/conflicting states. | P1 | ChatGPT | proposed | Fixture-backed schema validation covers duplicate IDs, unresolved references, stale evidence, conflicting sources, and unsupported state inference. |
| EATI-004 | Specify the HAPI MCP Registry discovery lane and its separation from capability review, permission review, and runtime admission. | P1 | ChatGPT | proposed | Discovery records are provenance-pinned; no discovered server/tool is trusted, installed, or exposed solely because it appears in a registry. |
| EATI-005 | Specify the Context.dev → Context7 → Mintlify research/documentation lane. | P1 | ChatGPT | proposed | Research evidence is source-attributed; library guidance is version-pinned; only reviewed documentation is published; Mintlify access/runtime remains explicitly verified or unknown. |
| EATI-006 | Specify task-routing and isolated-execution boundaries for Smart Model Router, Superpowers, and Sprites. | P1 | ChatGPT | proposed | Router recommendations do not mutate the active model; workflow skills do not bypass repo governance; Sprite environments do not gain deployment authority by default. |
| EATI-007 | Specify API Impact Mapper usage for API-change classification and consumer/test/documentation impact analysis. | P1 | ChatGPT | proposed | Analysis is grounded only in supplied or retrieved change evidence; repository tests/review decide acceptance. |
| EATI-008 | Produce a phased implementation backlog that splits each independent runtime, credential, workflow, or deployment integration into separately reviewed items/proposals. | P1 | ChatGPT | proposed | Each follow-on has a bounded owner, authority, permission boundary, validation contract, rollback/disable path, and explicit non-goals. |

## Scope boundary

This proposal is an inventory and architecture slice. It does not implement adapters, add MCP servers, install binaries, provision credentials, enable external services, invoke paid APIs, change routing/admission, dispatch jobs, or publish documentation automatically.
