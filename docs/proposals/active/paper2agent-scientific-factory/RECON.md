# Paper2Agent Scientific Factory — RECON

## Evidence basis

Issue #621 identifies twelve gaps. The integration graph preserves the sequence: Paper → Manifest → Claim/Method Graph → Environment → Capability Extraction → MCP (tools + resources + prompts) → Reference Reproduction → Certificate → Scientific Agent Registry → Hierarchical Router → MoneyBall/3L0.

The repository already contains a Paper2Agent pattern document and merged evolutionary-replay work. Those provide orchestration/evaluation patterns but do not establish a first-class scientific artifact contract.

## Existing substrate

| Surface | Reuse boundary |
|---|---|
| Agent Evidence Substrate | SHA/run/artifact/environment provenance |
| Context Relationship Graph | relationship traversal and evidence separation |
| Capability/provider registry | destination for extracted capabilities |
| MCP catalog/hosts | runtime integration boundary |
| Docker/Codespaces | reproducible environment surfaces |
| ATES / MoneyBall / 3L0 | system execution/economic observations |
| Paper2Agent + evolutionary replay | research extraction/replay patterns |

## Scientific evidence classes

SCIENTIFIC_REFERENCE = immutable expected/reference result.
SCIENTIFIC_EXECUTION = execution bound to manifest/environment.
SCIENTIFIC_COMPARISON = normalized reference/candidate comparison.
SCIENTIFIC_VALIDATION = evaluator decision with method/version/tolerance.
SCIENTIFIC_CERTIFICATE = aggregate acceptance artifact.

ATES/3L0 may be operational metadata but cannot upgrade a scientific result between classes.

## Security boundary

Paper repositories and dependencies are untrusted inputs. Before future execution: pin source commit; record dependency lock; isolate filesystem and credentials; default network to disabled or explicit allowlist; bound CPU, memory, wall time, process count, and artifact size; capture environment/image digest; retain artifact provenance; separate dependency/runtime failures from scientific failures.

No secret is copied into manifests, MCP payloads, telemetry, or certificates.

## Lifecycle

DISCOVER → INGEST → EXTRACT → ENVIRONMENT → GENERATE → TEST → REPRODUCE → VALIDATE → PACKAGE → REGISTER → DEPLOY → OBSERVE → RE-VALIDATE → RETIRE.

Each transition requires evidence. Failed or incomplete transitions remain explicitly failed/incomplete.

## Open questions

Which reference-result normalizers should be first-party versus adapters? Which scientific domains should receive initial fixtures? What minimum claim graph is useful without a heavyweight ontology? Which MCP resource identifiers remain stable across paper revisions? Which certificate states are routable versus discoverable only?
