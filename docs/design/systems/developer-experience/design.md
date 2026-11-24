# Developer Experience — Design

> **Evidence status:** candidate surface / source inventory  
> **Design owner:** integration and developer-documentation maintainers  
> **Canonical implementation:** linked integration and skill sources  
> **Last source review:** 2026-11-23

## 1. Purpose and users

Developer Experience spans repository contributors integrating tools, discovering capabilities, reading technical guidance, and operating supported workflows. The current evidence is distributed across integration and skill documentation; a single end-to-end experience specification remains to be established.

## 2. Experience surfaces

| Surface | Audience | Evidence status | Owning source |
|---|---|---|---|
| Integration catalog and adapter contracts | Contributors / integrators | Existing docs | [Integration catalog](../../../integrations/README.md) |
| Skill discovery and usage | Contributors / agents | Existing inventory | [Skills inventory](../../../ops/SKILLS-INVENTORY.md) |
| Repository entry and navigation | Contributors | Existing docs | [CLAUDE.md](../../../../CLAUDE.md), [architecture](../../../../architecture.md) |

## 3. Information architecture

The integration catalog and skills inventory remain independently owned. A consolidated contributor journey should link them while preserving their distinct discovery and governance roles.

## 4. Journeys and interactions

Current source inventory supports discovery, documentation lookup, and integration selection as areas to map. Exact contributor onboarding, install, configuration, verification, and troubleshooting journeys require further source-backed synthesis.

## 5. Visual language

Developer-facing documentation should follow the shared visual and information conventions where applicable. The present source set does not establish one cross-product documentation design system.

## 6. Accessibility

Verify accessibility on rendered documentation and any developer tools separately. The source inventory does not establish a consolidated accessibility audit.

## 7. Evidence and system states

Document connection, capability, entitlement, availability, and execution states according to each integration's contract. Keep documentation claims distinct from live provider/account observations.

## 8. Decisions and open gaps

- Map contributor onboarding from repository entry to first verified contribution.
- Map integration discovery, configuration, validation, and failure recovery.
- Inventory documentation hosting and navigation ownership.
- Verify which Context7, Context.dev, Mintlify, and Cloudinary integrations are repository-native versus session-connected before assigning them product responsibilities.

## 9. Canonical sources

- [Integration catalog](../../../integrations/README.md)
- [Adapter contract](../../../integrations/ADAPTER-CONTRACT.md)
- [Skills inventory](../../../ops/SKILLS-INVENTORY.md)
- [Repository entry](../../../../CLAUDE.md)
- [Repository architecture](../../../../architecture.md)
