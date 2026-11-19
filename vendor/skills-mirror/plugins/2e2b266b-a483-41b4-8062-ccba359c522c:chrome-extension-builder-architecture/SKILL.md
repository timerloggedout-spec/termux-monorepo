---
name: chrome-extension-builder-architecture
description: Design Manifest V3 extension architecture, browser contexts, framework selection, typed messaging, storage, permissions, compatibility, backend boundaries, and migrations.
---

# Chrome Extension Builder: Architecture

Before starting, read [shared policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Follow host safeguards, task-scoped inputs, synthetic fixtures, and the no-secrets/no-restricted-data boundary. Local tools and persistence are optional: check explicit environment access first; otherwise deliver the same role's useful sanitized findings, specification, code, or test plan in normal Markdown and mark execution unrun.

Read the contract, live code, and research. Choose the smallest architecture supporting the journey. A SaaS companion may combine extension/API/database/web portal; an offline utility need not acquire a backend.

Write `docs/architecture.md` with context/data-flow diagram, module ownership, manifest plan, storage schema, message/API contract, threat boundaries, deployment units, and decision rationale. Use [platform-architecture.md](../chrome-extension-builder/references/platform-architecture.md).

- Popup: quick action; closing must not lose essential work. Side panel: sustained work beside a tab. Options: preferences/account/export/delete. Content script: scoped page interaction. Worker: events/coordination/privileged operations. Offscreen: justified DOM/media with cleanup. DevTools/new-tab/native messaging are purpose-specific choices.
- Compare vanilla for minimal dependencies, WXT for structured entrypoints/builds, and Plasmo for React-oriented tooling. Inspect generated MV3 output, CSP, minimum Chrome, and lockfile. Verify docs rather than mixing framework entrypoint conventions.
- Register worker listeners synchronously during initialization. Separate pure domain logic from Chrome adapters. Design state recovery, idempotency, timeouts, cancellation, and resumable server jobs; no persistent keepalive loops.
- Version JSON-compatible messages with request IDs, operation types, validated payloads, authorization, bounded responses, and stable errors. Page data cannot choose arbitrary privileged operations/fetch URLs.
- Map storage lifetime/quota: small settings in sync; durable data in local/IndexedDB; ephemeral sensitive state in session with trusted-context access. Specify migrations, concurrent updates, export/delete, and account switching. Never sync tokens/provider secrets.
- Justify each permission/host. Prefer activeTab/user gestures and optional grants where compatible. Specify denial/revocation, restricted pages, feature detection, and target browsers.

Exit when frontend/backend can implement independently against agreed interfaces, every crossing has an owner, and security examined the design. Export tasks with dependencies/file ownership; preserve user choices.

## Context and outcome handoff

Use compact authorized [project context](../chrome-extension-builder-context/SKILL.md), reconcile confirmed choices before selecting contexts/stack, and explain matching [engineering defaults](../chrome-extension-builder/references/engineering-instincts.md). Record scoped decisions with provenance; invalidate affected evidence when boundaries/interfaces change. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
