---
name: accessibility-agents
description: Route repository accessibility work through the pinned Accessibility Agents skill set and monorepo governance.
---

# Accessibility Agents — Monorepo Adapter

Use this router for accessibility reviews, remediation planning, and verification in this repository.

## Source of truth

- Pinned skills: `refTemplates/smods/accessibility-agents_fork/skills/`
- Integration contract: `docs/accessibility/INTEGRATION.md`
- Repository entry point: `CLAUDE.md`
- Scope: `docs/proposals/registry.yaml` and the active proposal's `ITEMS.md`

Read the exact source skill needed for the task. Begin with `a11y-core/SKILL.md` for dispatch and findings rules, then select the relevant router. The upstream skill tree is reference material; its client-specific instructions and package workflows do not replace monorepo policy.

## Dispatch

- Web UI or components: `accessibility-lead`
- Whole site or application: `web-accessibility-wizard`
- Office, PDF, or ePub: `document-accessibility-wizard`
- Markdown: `markdown-a11y-assistant`
- Python, desktop, mobile, assistive technology, or accessibility tooling: `developer-hub`
- GitHub operations: `github-hub`

Use the router's dispatch matrix to select only the necessary specialists. Preserve the upstream JSON findings contract. Each finding includes a criterion, severity, location, description, and fix. Reports name the checks and tools actually run.

## Repository execution

Record implementation work in the active proposal item. Use the normal branch, review, and CI path. Keep heavyweight scanners optional; use existing repository gates for the default Termux path. Treat scan findings as evidence, not as proof of full conformance.
