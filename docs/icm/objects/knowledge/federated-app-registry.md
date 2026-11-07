---
type: object
cluster: knowledge
universe: live
status: verified
entity: docs/ops/FEDERATED-APP-AND-RELEASE-LANE-MAP.md
verified_at: 2026-11-03
---

# Federated Application Registry

The federated application registry maps product applications that may be maintained outside the Termux monorepo while remaining part of the Termux system architecture.

## Owns

- Product AppID registry navigation and identity-domain boundaries.
- Cross-repository application references and release-lane relationships.
- The distinction between product AppIDs and GitHub App automation identities.

## Does not own

- External application source code or its release implementation.
- Runtime deployment state or production readiness.
- GitHub App credential custody, installation permissions, or token minting.
- UI modality/renderer capabilities, which belong to the UI surface registry.

## Canonical sources

- [Federated application and release-lane map](../../../ops/FEDERATED-APP-AND-RELEASE-LANE-MAP.md)
- [Machine-readable registry](../../../ops/federated-app-registry.json)
- [Registry schema](../../../ops/federated-app-registry.schema.json)
- [Repository discovery census](../../../ops/FEDERATED-APP-REPOSITORY-CENSUS.md)
- [Machine-readable repository census](../../../ops/federated-app-repository-census.json)
- [Repository census schema](../../../ops/federated-app-repository-census.schema.json)
- [GitHub App fleet](../platform/github-app-fleet.md)

## If you change this

Update the machine-readable registry and its schema/tests together. Verify external repository identity and default ref from live GitHub metadata. Keep unknown values null/unknown; do not infer an owning repository from a similarly named fork. Each release lane keeps its own version authority, artifact, signing status, and evidence.

## Relationships

- **indexes:** product application identities, UI surfaces, and release lanes.
- **separates:** product applications from platform automation identities.
- **joins:** external repositories and release receipts to the Termux system map.
- **does not replace:** application-owned release procedures or canonical source code.
