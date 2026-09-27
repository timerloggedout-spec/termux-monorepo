# FOSS AI/Technology Foresight & Procurement Spine

Status: implemented registry contract on a current-master extract branch.

This lane turns the standing digest into an executable, provenance-preserving procurement/evaluation input. It does not make a vendor or model the canonical system of record.

## Architecture

research / first-party sources -> FOSS RESOURCE REGISTRY -> H0-H3 + procurement + provenance -> canonical evidence -> OpenTelemetry / MCP / MoneyBall-3L0 -> management hub

## Horizon semantics
- H0: confirmed/currently usable evidence.
- H1: emerging and sufficiently evidenced to prototype or evaluate.
- H2: weak signal worth structured watching.
- H3: speculative; retain only when material.
- Horizon is not a quality score.

## Evidence semantics
- CONFIRMED: directly supported by a primary repository, specification, official release, standard, or reproducible benchmark.
- ATTRIBUTED: explicitly attributed to a named source; not adopted as established fact.
- EARLY_SIGNAL: credible but incomplete evidence.
- SPECULATIVE: hypothesis or forward-looking research direction.

## Procurement dimensions
license; canonical source; self-host/local viability; egress surface; vendor lock-in; reproducibility; platform portability; agent/MCP interoperability; observability compatibility; unresolved questions; procurement action.

## Canonicality rule
OpenTelemetry is the neutral telemetry boundary. MCP is an interoperability contract. Langfuse/Phoenix are adapters. Docker/Codespaces are environment surfaces with different roles. MASEval is evaluation infrastructure. Complexity providers remain measurement providers rather than truth.

## Research-lane rule
Research-Astute and other organizations may publish evidence records. The management hub consumes normalized records with source, observation date, horizon, evidence status, and provenance; the research lane does not become the operational control plane.

## CI contract
scripts/ci/verify_foss_registry.py validates JSON, required fields, vocabulary, HTTPS primary sources, unique IDs, procurement dimensions, and secret absence. The workflow emits an immutable receipt linked to the source SHA and run ID.

## Research lanes
local/edge inference; ARM/Android measurements; MCP conformance; Docker/Codespaces/Nix parity; Tree-sitter/Lizard/Radon labeled complexity; Langfuse/Phoenix identical-cohort comparison; MASEval manager tournaments; Sigstore/SLSA provenance; Firecracker/gVisor sandbox experiments; NIST traceability implementation tracking.
