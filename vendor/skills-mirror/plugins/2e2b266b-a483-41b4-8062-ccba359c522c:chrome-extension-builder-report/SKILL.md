---
name: chrome-extension-builder-report
description: Synthesize concise Chrome extension session outcomes, project readiness, quality, feedback, scheduled digests, and labelled visual evidence from the canonical project record and specialist reports. Use for status, recap, handoff, before/after comparison, or readiness reporting.
---

# Chrome Extension Builder: Outcome Reports

Read [policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Reports aggregate actual evidence and selected specialist outputs; they do not create another authoritative state file or turn a checklist into verification. Read [reporting-and-visual-evidence.md](../chrome-extension-builder/references/reporting-and-visual-evidence.md).

Choose session recap, project overview, quality/release report, design comparison, feedback triage, or scheduled digest. Lead with what the user can do now, changed work, observed verification, unrun/blocked/stale cases, and one concrete next action. Keep routine reporting brief and details linked. Include relevant accepted decisions without repeating the full history.

- Use the canonical project/evidence record plus authoritative paths from team.json. Every finding has category, impact/severity, source/date, artifact/environment, evidence, owner, remedy, and status.
- Separate `planned`, `implemented`, `verified`, `blocked`, and reasoned `not applicable` workflow state from quality cases `pass`, `fail`, `stale`, `not run`, `not applicable`. Separate backend/store states. Do not display a generic completion percentage or estimate a reassuring score.
- Label visual assets `concept`, `interactive prototype`, or `actual extension capture`, naming surface, state, build/browser, date, and relevant case. Show useful before/after states only with comparable conditions. A screenshot does not establish account integration, accessibility, or lifecycle correctness.
- Use accessible Markdown tables, concise timelines, and small architecture diagrams by default. Host-supported expandable/interactive views are optional. JSON/HTML/PDF exports require safe supported tools. Validate imports and safely render untrusted text; never fabricate clickable controls or executed actions.
- Charts require observed values, source, date range, sample size, and collection authority. Human sessions, scheduled runs, and retries remain separate. Hide absent analytics and explain how evidence can be obtained; no illustrative product metrics.
- Redact before sharing. Builder aggregate feedback excludes identifying project details, source/page content, transcripts and secrets. Internal project reports remain task-scoped and exportable/removable through user-controlled storage.

Optional local `scripts/intelligence.py report PROJECT --kind session|project|feedback|scheduled --output RELATIVE_BASENAME` produces record-derived JSON/Markdown; resolve the helper from the main skill and read help. It does not run tests, inspect images, deploy, or prove claims. In chat use [outcome template](../chrome-extension-builder/references/templates/outcome-report.md).

Exit with a comprehensible outcome/evidence/next-action report, exact unrun gates, and portable continuation. Never claim 10x improvement, reliable monitoring, native host success, or release readiness without matching observed evidence.
