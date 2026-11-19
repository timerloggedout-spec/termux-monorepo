---
name: chrome-extension-builder-studio
description: Guide interactive Chrome extension planning in conversation or manually start the optional local Extension Studio when the user requests it and the host supports local execution. Use for studio or visual planning requests.
---

# Chrome Extension Builder: Studio

Before starting, read [policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Accept only a sanitized brief and explicit choices, never secrets/restricted records.

In chat, guide purpose → audience → local/cloud/hybrid → surfaces → sites/data/permissions → acceptance. Present editable choices and a reviewable normal Markdown plan. Use [chrome-extension-builder](../chrome-extension-builder/SKILL.md) for substantive work. A useful planning result requires no local server or persistent settings.

If the user specifically requests local Studio, first verify shell/Node/Python and bundled assets are available in their explicit environment. Resolve `../chrome-extension-builder/scripts/extension_builder.mjs` from this skill directory, read its help, and manually run its studio command only in that authorized environment. No automatic service startup, external exposure, MCP UI, or cloud connection. If unsupported, continue the chat planning flow and name the limitation.

Explain optional browser-memory/export controls before entering a plan. Studio checkboxes/scores are declarations, not executed tests or independent agents. Exit with a usable brief, chosen tradeoffs, next workflow, and actual startup status when attempted.

## Context and outcome handoff

Planning outputs are provisional declarations until supported by actual artifact evidence. Use [project context](../chrome-extension-builder-context/SKILL.md) to retain confirmed choices and [report](../chrome-extension-builder-report/SKILL.md) to label prototypes versus real captures. Candidate weights stay frozen across rounds; exported plans do not execute agents or activate jobs. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
