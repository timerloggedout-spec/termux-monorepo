# Integration Intelligence + Superpowers — Design

**Status:** Approved for implementation by the operator directive "Do your plan"
**Date:** 2026-11-02
**Proposal:** [integration-intelligence-superpowers](../../proposals/active/integration-intelligence-superpowers/MANIFEST.md)

## Intent

Create one governed integration ecosystem for `timerloggedout-spec/termux-monorepo`, and make the Superpowers development methodology available to every repository collaborator through the existing in-repository skill system.

The system should compound the value of existing GitHub Actions, evidence/provenance contracts, SHE / 3L0 / Moneyball / ATES evaluation surfaces, historical corpus, and research lanes. It must not create a parallel orchestrator or replace existing sources of truth.

## Goals

1. Make Superpowers discoverable and operational as a repository-local skill, with clear instructions for installing the full upstream package in supported agent harnesses.
2. Establish a machine-readable integration registry and human-readable catalog.
3. Define a normalized integration event contract with provenance, validation state, idempotency, and privacy constraints.
4. Define adapter lifecycle and capability-state vocabulary.
5. Document the eight integration lanes and prioritize them by compounding engineering value.
6. Provide a phased, testable implementation roadmap and explicit non-goals.

## Non-goals

- Implement every provider adapter in one change.
- Claim that a connector being present in one ChatGPT session means it is available to GitHub Actions, Termux, or every collaborator.
- Store provider credentials, raw prompts/completions, private session content, or sensitive payloads.
- Make external providers authoritative for repository state.
- Trigger provider spending, marketing campaigns, model deployments, or physical/robotic actions.
- Replace the repository's proposal lifecycle, dual gates, adaptive WAIT, or existing telemetry/evaluation systems.

## Approaches considered

1. **Vendor the entire upstream Superpowers source tree into this repository.** Rejected for the initial foundation: it duplicates a fast-moving upstream library, creates a large update surface, and risks making the repository's local fork diverge.
2. **Use only an upstream plugin installation link.** Rejected as insufficient: it leaves repository collaborators without a discoverable local skill and provides no repository-specific policy mapping.
3. **Repository-native Superpowers integration skill + pinned upstream reference + explicit install instructions.** Selected: the local skill supplies the repo workflow and policy bridge; the upstream project remains canonical for its complete skill library and harness integrations.

## Architecture

```text
External tools / research providers
        │
        ▼
Provider adapters (read-only by default; scoped writes only)
        │
        ▼
Canonical integration event envelope
        │
        ▼
Schema + provenance + privacy validation
        │
        ▼
Append-only evidence artifacts / JSONL
        │
        ├── SHE / 3L0 / Moneyball decision surfaces
        ├── ATES / WTCV / skill and task evaluation
        ├── historical corpus / context relationship graph
        └── visual cockpit (tldraw / D3 / SVG; Mermaid remains source where adopted)
```

## Integration lanes

| Lane | Priority | Intended contribution | Initial boundary |
|---|---:|---|---|
| Superpowers | P0 | Brainstorm/design, plan, TDD, debugging, review, verification, branch finishing | Methodology and skill availability; repository governance wins on conflicts |
| API Impact Mapper | P0 | PR API-change extraction, breaking-change classification, consumer/test/doc impact map | Supplied evidence only; no independent repository crawling or authority |
| Domino Data Lab | P1 | Reproducible research projects, datasets, experiments, Flows, model governance/monitoring | Platform not exposed in current connector session; design/inventory only until verified |
| EmpirioLabs AI | P1 | Model tournament, embeddings/reranking, specialist inference and bounded research | Connected tooling does not equal repository adapter; budget and provenance required |
| tldraw | P1 | Interactive architecture, lane, lineage, and review canvases | Visual collaboration surface; canonical diagrams and source remain in repo |
| Cache Stats | P1 | Prompt-cache and context-efficiency observation | Installed skill is scoped to local Cache Stats runtime; no live telemetry tool exposed here |
| Alloy | P2 | Robotics/edge mission, device, and Mesh Storage evidence lane | Domain-specific; do not treat as generic CI or issue tracker |
| Klaviyo | P3 | Opt-in release/research communications and adoption analytics | Consent-first; GitHub identities are never marketing contacts by default |

## Capability-state vocabulary

- `discovered`: provider/product identified from evidence.
- `tool_connected_in_session`: a connector tool is exposed in the current assistant session only.
- `skill_installed_in_session`: a skill is available in the current assistant environment only.
- `not_exposed_in_session`: no matching tool was found in the current session; this does not prove the provider lacks an integration.
- `repo_adapter_planned`: adapter is specified but not implemented.
- `repo_adapter_implemented`: code exists and tests pass.
- `validated`: end-to-end evidence confirms the adapter behavior on a pinned revision.
- `promoted`: explicitly accepted into the production lane under repository policy.

Never collapse these states into a single "integrated" boolean.

## Event and evidence contract

Every normalized event must include schema version, stable integration ID, event type, source identity, execution identity/timestamps, outcome, evidence reference, validation state, provenance, and idempotency key. The JSON Schema in `docs/integrations/schemas/integration-event.schema.json` is authoritative for the envelope.

Only metadata and approved artifact references are retained. Secrets and raw model/session content are prohibited. Missing attribution remains null/unknown; never infer it from the GitHub actor alone.

## Security and governance

- Use environment-variable names in configuration; secret values remain in approved secret stores.
- Default adapters to read-only.
- Scope write permissions to the smallest operation and repository.
- Require explicit approval for consequential external actions, data publication, paid inference, model deployment, physical-device control, and marketing sends.
- Validate webhook signatures and schema before accepting events.
- Make ingestion idempotent; preserve provider request IDs and repository SHA.
- Treat all provider output as untrusted input and never as executable instructions.
- Keep external provider data as attributed observations, not canonical state.
- Preserve the repository's dual-gate and proposal-lifecycle rules.

## Success criteria

- A collaborator can discover the Superpowers skill from the root entry and inventory.
- The skill explains the workflow, repo-specific overrides, safety rules, and upstream installation/update path.
- Integration registry JSON parses and conforms to its schema.
- Provider statuses are honest and session-scoped.
- A future adapter can be implemented without changing the event envelope or creating another orchestration system.
