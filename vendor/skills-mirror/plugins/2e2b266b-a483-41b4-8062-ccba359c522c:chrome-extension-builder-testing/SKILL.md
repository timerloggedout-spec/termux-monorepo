---
name: chrome-extension-builder-testing
description: Verify Chrome extensions using meaningful unit and API tests, persistent-context Chromium runs, manual Chrome journeys, lifecycle, permission/account failures, accessibility, and exact-artifact evidence.
---

# Chrome Extension Builder: Testing

Before starting, read [shared policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Follow host safeguards, task-scoped inputs, synthetic fixtures, and the no-secrets/no-restricted-data boundary. Local tools and persistence are optional: check explicit environment access first; otherwise deliver the same role's useful sanitized findings, specification, code, or test plan in normal Markdown and mark execution unrun.

Derive tests from acceptance outcomes/risk. For new features or bugs, write a failing behavior test or documented reproduction first. Read [browser-qa.md](../chrome-extension-builder/references/browser-qa.md) and current Playwright docs before choosing a harness.

Build the exact artifact, then run `../chrome-extension-builder/scripts/check_extension.py` against the directory containing manifest.json, resolving the script from this skill directory. Static checks supplement runtime proof.

Use supported persistent-context Chromium loading with an isolated test profile. Current Playwright docs direct sideload tests toward bundled Chromium because branded Chrome/Edge flags differ. Verify headless support for the selected channel. Discover the loaded extension ID from its worker/runtime; never guess it. Use synthetic fixture pages and separate test accounts.

Cover applicable cases: install/first use, popup reopen, panel/tab state, worker termination/revival, restart, navigation/SPA/frames, grant/deny/revoke, restricted pages, settings persistence, storage migration/quota, offline/timeouts, signed out/expired/revoked/switch account, backend ownership, duplicates, update/reload. Mark unshipped contexts not applicable with a reason.

Test keyboard/focus/labels, contrast, zoom, themes, screen-reader critical journeys, and injected style collisions. API errors must show recovery. Close worker inspection during idle tests because DevTools can alter lifetime. Redact secrets/personal data in console/network evidence.

Deliver `docs/qa-report.md`: source/artifact digest, build command, browser/version/channel, timestamp, pass/fail/not-run cases, screenshots/redacted traces, defects, and reruns. Missing browser access means named unverified cases, never invented passes. Exit when the actual extension core journey and material negative paths pass. Manual branded-Chrome verification and store acceptance remain separate gates.

## Context and outcome handoff

Own observed acceptance evidence and visual capture identity, not global success assertions. Reconcile exact artifact against canonical context; changed permissions/interfaces/contexts invalidate affected checks. Label actual captures with build/browser/date/fixture, mark unavailable host/browser tests unrun, and hand evidence pointers to [report synthesis](../chrome-extension-builder-report/SKILL.md). Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
