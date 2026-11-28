---
name: chrome-extension-builder-ux-design
description: Design polished Chrome extension journeys, popup and side-panel layouts, onboarding, permission and account states, accessible interaction, design tokens, and companion-app UX.
---

# Chrome Extension Builder: UX Design

Before starting, read [shared policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Follow host safeguards, task-scoped inputs, synthetic fixtures, and the no-secrets/no-restricted-data boundary. Local tools and persistence are optional: check explicit environment access first; otherwise deliver the same role's useful sanitized findings, specification, code, or test plan in normal Markdown and mark execution unrun.

Design for the user's job and browser surface. Inspect current UI and preserve approved direction. Show a useful first-run journey before decorative detail.

Create `docs/ux-spec.md` with journey/state maps, surface dimensions, typography/spacing/color tokens, component behavior, interaction copy, and accessibility acceptance criteria. Produce an interactive local prototype or implemented journey where tools permit; mark mocked account/API behavior in review evidence.

1. Choose one primary action per surface. Popup suits short actions; side panel or extension tab suits sustained editing. Persist drafts/progress outside ephemeral popup state.
2. Design first use → access/account choice → core task → result → repeat use. Ask for access when its benefit is apparent. Explain exact site/data and give recoverable decline.
3. Cover empty/loading/offline, denied/revoked permission, signed out/expired session, quota/paid limits, success/partial success, retryable/fatal errors. Status must be truthful. Include cancellation/disconnect/delete/export where applicable.
4. Use semantic controls, visible focus, logical keyboard order, labels, status announcements, contrast, reduced motion, scalable text, and accessible errors. Avoid color/hover-only information and tiny targets. Target applicable WCAG 2.2 AA criteria; test actual keyboard/screen-reader behavior.
5. Injected page UI needs scoped CSS, dismissal, and host-page focus/scroll preservation. Verify host themes and zoom. Never impersonate browser or website authentication dialogs.
6. Compare at most three meaningful alternatives if direction is uncertain. Judge completion, hierarchy, trust, accessibility, and implementation cost; select one and retain rationale.

Exit when the core journey is interactive and critical states have defined behavior. Handoff tokens, components, screenshot targets, and QA scenarios. Use [browser QA](../chrome-extension-builder/references/browser-qa.md) and [WCAG](https://www.w3.org/TR/WCAG22/).

## Context and outcome handoff

Retain accepted visual direction from authorized project context. Deliver representative empty/loading/error/offline/permission/account states. Label concept, prototype, and actual capture using [visual evidence](../chrome-extension-builder/references/reporting-and-visual-evidence.md); screenshots alone do not prove accessibility or extension runtime. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
