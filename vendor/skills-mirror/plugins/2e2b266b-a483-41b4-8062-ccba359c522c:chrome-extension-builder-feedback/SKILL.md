---
name: chrome-extension-builder-feedback
description: Capture optional sanitized feedback and turn demonstrated builder or generated-extension problems into scoped reproductions, priorities, and regression candidates. Use for feedback, confusing workflows, repeated context failures, or end-user extension issues without mixing product identities.
---

# Chrome Extension Builder: Feedback

Read [policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Feedback is optional and local by default. No automatic uploads, transcripts, telemetry, raw source/page content, credentials, identifying project names in aggregate builder reports, or inferred satisfaction profiles.

At a meaningful milestone, optionally offer useful / partly useful / blocked and a short missing-piece note. Do not repeat after every message, delay continuation, or interpret skipping/rephrasing as dissatisfaction. Apply a user's correction to the active task immediately; persisting a general preference requires a scoped basis and permission.

1. Select `builder` or `extension` explicitly. Builder concerns routing/explanations/context/generated-artifact usefulness; extension concerns that project's end-user behavior. Separate their records, ownership, evidence, and aggregate metrics. Read [feedback-and-learning.md](../chrome-extension-builder/references/feedback-and-learning.md).
2. Record package version, host, task category, outcome, issue category, and voluntarily supplied sanitized note; generated-product feedback additionally needs a safe project/build context. Preserve observed versus reported status. Classify reproducible defect, confusing experience, context failure, inaccurate claim, or feature request.
3. Deduplicate only demonstrated common causes, retaining distinct affected environments. Prioritize user impact, affected scope, evidence confidence, and effort; frequency alone is insufficient. Redact and preview any report before the user chooses to export/share. External sending or hosted storage requires actual authorization and matching privacy/retention/deletion policy.
4. Validate with a synthetic reproduction or behavioral evaluation. Demonstrate the incumbent failure where possible, assign a focused owner, repair within scope, and rerun the original case and affected boundaries. A spec or source-string test is not proof of semantic model behavior.
5. Keep useful scoped lessons only after demonstrated correction/evaluation, recording conditions, counterexamples, evidence/date, and maintainer review. No autonomous self-training, shared private-project corpus, or unattended plugin rewrites. Changes/publication retain host and release gates.

Use the main skill's `scripts/intelligence.py feedback` after inspecting its live contract; use its distinct `feedback-export` for reviewed minimized builder-only aggregation, never treat ordinary project feedback reports as anonymous exports; otherwise provide a sanitized report in chat. Deliver categorized evidence, priority rationale, reproduction, owner, next action, and honest validation status. Exit with actionable local findings or an explicitly shared report; do not claim global users, retention, or satisfaction from local records. Route defects to [debugging](../chrome-extension-builder-debugging/SKILL.md) and synthesis to [report](../chrome-extension-builder-report/SKILL.md).
