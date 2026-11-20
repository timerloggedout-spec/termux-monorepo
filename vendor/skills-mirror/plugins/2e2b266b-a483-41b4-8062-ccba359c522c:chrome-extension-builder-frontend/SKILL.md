---
name: chrome-extension-builder-frontend
description: Implement Chrome extension popup, side panel, options, extension tabs, content-script UI, and companion frontend with packaged assets, accessible state handling, and MV3-safe output.
---

# Chrome Extension Builder: Frontend

Before starting, read [shared policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Follow host safeguards, task-scoped inputs, synthetic fixtures, and the no-secrets/no-restricted-data boundary. Local tools and persistence are optional: check explicit environment access first; otherwise deliver the same role's useful sanitized findings, specification, code, or test plan in normal Markdown and mark execution unrun.

Read architecture, UX, and message/API contracts. Preserve the chosen vanilla/WXT/Plasmo stack; inspect current docs and generated manifest. Work in assigned files and adapt to shared edits. Build a complete core journey with real state transitions.

- Separate components from Chrome/storage/network adapters. Use typed state, validated inputs, explicit pending/success/error, cancellation, and account/permission guards. Prevent duplicates while pending and keep recovery visible.
- Package scripts/fonts/icons/styles compatible with release CSP. Dev servers/hot reload never become store dependencies. No remote scripts, eval, or HTML injection from page/API/AI text.
- Popup closure must not discard drafts or cancel essential worker/server jobs. Rehydrate on reopen and subscribe to updates. Side-panel state must reflect the active/global tab policy. Settings need save/error feedback.
- Content scripts need scoped UI (Shadow DOM where suitable), bounded observers, cleanup, SPA handling, and deduplication. The host DOM remains untrusted in isolated execution worlds. Expose only allowlisted messages, never privileged page APIs.
- Implement semantic controls, keyboard/focus, contrast, reduced motion, zoom, and accessible errors/status. Local/cloud claims must reflect actual behavior.
- Companion sites can share tokens and public types, never privileged adapters or server env values. Inspect generated client artifacts for secrets/remote executable dependencies.

Deliver source, generated extension directory, run/load commands, screenshots, and behavior evidence. Test meaningful state logic and the actual extension in Chromium; webpage demos are insufficient. Exit when core interaction survives reopening/navigation and critical errors recover. Use [platform reference](../chrome-extension-builder/references/platform-architecture.md) and [browser QA](../chrome-extension-builder/references/browser-qa.md).

## Context and outcome handoff

Consume confirmed context/interfaces and implement the smallest useful journey. Record changed surfaces/permissions/messages and affected stale evidence; use [practical recipes](../chrome-extension-builder/references/task-recipes.md) only when appropriate, not as claims about the scaffold. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
