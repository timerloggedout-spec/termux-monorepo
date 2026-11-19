---
name: chrome-extension-builder-debugging
description: Reproduce and fix Chrome extension runtime defects in popup, side panel, content scripts, MV3 workers, permissions, messaging, storage, build output, auth, and cloud integrations.
---

# Chrome Extension Builder: Debugging

Before starting, read [shared policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Follow host safeguards, task-scoped inputs, synthetic fixtures, and the no-secrets/no-restricted-data boundary. Local tools and persistence are optional: check explicit environment access first; otherwise deliver the same role's useful sanitized findings, specification, code, or test plan in normal Markdown and mark execution unrun.

Reproduce the reported interaction on the current built extension. Capture source/artifact/browser versions, exact context/action, expected/observed behavior, and redacted error. Ask only for information tools/source cannot provide.

1. Inspect chrome://extensions errors and the right console. Page, popup, worker, and server evidence describe distinct layers. Correlate request IDs/timestamps without exposing tokens.
2. Confirm generated manifest/files, intended build, site match, grant, restricted URLs, and minimum-version support.
3. Check worker listener initialization, hydration, shutdown recovery, duplicates, timeouts/retries, and migrations. Evaluate idle behavior with worker inspection closed.
4. Check messaging contracts, sender/receiver, JSON compatibility, routing, response lifetime, and disconnect. For broad support, use callback/sendResponse plus literal true for asynchronous handling; verify current Chrome rollout/version before Promise listeners.
5. Check frames/worlds, SPA navigation, duplicate injection, stale nodes, style/focus collision, and revocation. Cloud failures need correlated auth/ownership/CORS/callback/limit/provider evidence.
6. Write a failing test or repeatable browser reproduction. Make the smallest coherent root-cause fix; avoid success fallbacks and blanket permission widening. Rerun original and affected negative paths.

Deliver evidence, patch, regression test/reproduction, root cause, and current-artifact outcome in the issue record or `docs/qa-report.md`. Exit after the original interaction passes or name the exact external gate. Use [browser QA](../chrome-extension-builder/references/browser-qa.md).

## Context and outcome handoff

Start from [compact context](../chrome-extension-builder-context/SKILL.md), current artifact, and failing reproduction; use the fix route without restarting full research. Retain accepted choices; mark impacted checks stale, verify the smallest meaningful regression, and record next actionable outcome. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
