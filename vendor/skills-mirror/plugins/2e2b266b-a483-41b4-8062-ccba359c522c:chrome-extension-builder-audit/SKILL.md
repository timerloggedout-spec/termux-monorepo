---
name: chrome-extension-builder-audit
description: Route a Chrome extension audit to architecture, security, testing, and performance reviews using scoped sanitized source or an explicitly available local build. Use for chrome-extension-builder-audit, review, readiness, or permission-risk requests.
---

# Chrome Extension Builder: Audit

Before starting, read [policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Use sanitized selected files/fixtures; do not ingest credentials, profiles, transcripts, or restricted records.

Select [architecture](../chrome-extension-builder-architecture/SKILL.md), [security](../chrome-extension-builder-security/SKILL.md), [testing](../chrome-extension-builder-testing/SKILL.md), and [performance](../chrome-extension-builder-performance/SKILL.md) according to the requested scope. Main routing follows [chrome-extension-builder](../chrome-extension-builder/SKILL.md). Do not duplicate those workflows here.

Review the supplied artifact/source and document severity, reproduction, owner, fix, and residual gate. Run local checks only with explicit supported environment access; browser/runtime cases remain unrun otherwise. Exit with actionable findings and evidence-separated readiness, never a blanket compliance certificate or inferred authorization to publish.

## Context and outcome handoff

Scope the audit from confirmed project context and exact artifact. Distinguish stale, absent, failed, and not-applicable evidence. Use [report](../chrome-extension-builder-report/SKILL.md) to give actionable findings without inventing runtime or host execution. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
