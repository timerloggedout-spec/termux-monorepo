---
description: Audit an existing Chrome extension across architecture, security, UX, runtime behavior, performance and release readiness.
argument-hint:
- extension project path
---

Audit the user's extension: $ARGUMENTS

Read `chrome-extension-builder`, `chrome-extension-builder-architecture`, `chrome-extension-builder-security`, `chrome-extension-builder-testing`, `chrome-extension-builder-performance` and `chrome-extension-builder-ux-design` as appropriate to the actual project. Preserve source during an audit unless the user also requests fixes.

Identify the exact source/build and distribution state. Run `node "${CLAUDE_PLUGIN_ROOT}/skills/chrome-extension-builder/scripts/extension_builder.mjs" check` with the project path and flags confirmed by `check --help`. A static pass alone is insufficient to clear runtime or Store gates.

Use skills/chrome-extension-builder/references/team.json to assign disjoint investigations and independent review. Examine manifest/host permissions, executable code/CSP, page-message trust, worker lifetime/storage, UI states/accessibility/localization, SPA/Shadow DOM behavior, backend auth/tenancy/privacy/cost, provider contracts, dependency provenance, package/listing and maintenance. Mark absent optional capabilities not-applicable with a reason.

Try the acceptance journeys on the current build when extension-capable browser tooling is available. Otherwise provide exact reproduction steps and mark those checks unverified. Return ranked actionable findings with file/line, impact, evidence and smallest remedy; never convert an unavailable check to pass. If fixes are authorized, route them to owners, verify the changed build and produce a fresh report.
