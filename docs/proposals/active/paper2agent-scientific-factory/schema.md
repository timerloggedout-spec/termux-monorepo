# Scientific Factory Schema Contract v0

This is the initial field-level contract. A machine-readable JSON Schema is SAF-001; this document is not a validator.

## Paper manifest

Required identity: schema_version, paper_id, paper_version, source canonical_url/source_commit/source_digest, artifact collections, claims, methods, environment lock_digest/image_digest/os_arch, and provenance.

A manifest MUST bind the paper version to immutable source identity. Mutable URLs alone are insufficient.

## Claim / method graph

Nodes: paper, claim, method, dataset, experiment, result, figure, table, code_artifact.

Edges: ASSERTS, IMPLEMENTS, USES, EVALUATES, PRODUCES, VISUALIZES, DERIVED_FROM, SUPPORTS, CONTRADICTS.

Every edge SHOULD carry a source locator and evidence status: verified, candidate, or unknown. Unknown must not be promoted to verified.

## Capability descriptor

A capability record contains capability_id, kind, inputs, outputs, preconditions, implementation_refs, validation_refs, and MCP tool/resource/prompt descriptors. Capabilities remain candidates until linked to validation evidence.

## Reference reproduction

A comparison binds reference artifact digest, candidate artifact digest, normalization method/version, evaluator kind/version, outcome (REPRODUCED, PARTIAL, FAILED, INCONCLUSIVE), run ID, source SHA, and environment digest.

The evaluator and normalization versions are part of evidence identity.

## Acceptance certificate

A certificate binds paper manifest, agent manifest, environment digest, capabilities, reproduction cases, security controls, provenance, issue time, and status. Status values are GENERATED, TESTED, REPRODUCED, VALIDATED, DEPLOYABLE, RETIRED.

VALIDATED requires scientific validation evidence. DEPLOYABLE additionally requires security/environment acceptance. Neither may be inferred from ATES/3L0.

## Registry admission

A scientific-agent registry record MUST reference immutable paper and agent manifests, environment digest, certificate, capability set, validation protocol/version, current status, and provenance locators. Router admission defaults to deny when the certificate is absent, superseded, expired, or incompatible with the requested capability.

## Revision rule

A paper source revision, code commit, environment-lock change, evaluator change, or capability implementation change creates a new evidence epoch. Historical certificates remain immutable records.
