---
name: chrome-extension-builder-context
description: Load and maintain concise Chrome extension project context, decision provenance, acceptance journeys, scoped memory, conflict handling, and adaptive next-step routing. Use when starting consequential work, resuming a project, changing a requirement, or preserving a useful handoff.
---

# Chrome Extension Builder: Project Context

Read [policy boundaries](../chrome-extension-builder/references/policy-boundaries.md) first. Use only the task-authorized project and sanitized records. Do not query/extract host memory, chat history/summaries, uploaded user files, or ambient personal context. No transcript harvesting, credential intake, hidden profiling, or automatic cross-project reuse.

1. Identify the project from the user's explicit context or accessible authorized workspace. Load the compact record first; read only decision-relevant artifacts afterward. Reuse `.extension-builder/project.json` through available local helpers, not a competing status file. In chat, accept/provide a portable summary instead. Check [project-context.md](../chrome-extension-builder/references/project-context.md).
2. Recap the last useful outcome, accepted choices, blocker, relevant change, and recommended next action. Verify consequential historical facts against accessible current source/service evidence. If inaccessible, mark them historical/unverified and preserve the limitation. Do not restart completed work merely because a new chat began.
3. Distinguish user-confirmed decisions, observed facts, and provisional inference with source, scope, checked date, and artifact identity where relevant. A guessed cloud requirement or old popup choice cannot override current user direction. Resolve contradictory inputs; the current request governs intent, while live evidence establishes actual implementation. Preserve superseded decisions without treating them as active.
4. Route build, improve, fix, audit, prepare release, or continue using [adaptive-routing.md](../chrome-extension-builder/references/adaptive-routing.md). Use [engineering-instincts.md](../chrome-extension-builder/references/engineering-instincts.md) only when a pattern matches; explain the recommendation and exceptions. Material uncertainty prompts the question that changes the next decision. Prefer reversible defaults where sufficient.
5. Record scoped decisions, acceptance, constraints, unresolved assumptions, current task, evidence pointers, and next action. A changed permission/data/context/interface marks affected evidence stale with a reason; unchanged evidence is not automatically failed. Persist only when user/host authorizes local or host-backed project state. Allow review, correction, export, and removal; do not silently generalize preferences to other projects.

Optional local tools: check availability and live help for `../chrome-extension-builder/scripts/intelligence.py` from this skill directory. `show PROJECT` produces a compact record-derived recap; recorded facts are not automatically true. Source integrity, actual browser execution, and release state remain separate.

Deliver a verified/provisional recap, active decisions, selected route, smallest useful next action, and concise handoff. Exit when the next role can act without forgetting choices or relying on unresolved material contradictions. For full work use [main builder](../chrome-extension-builder/SKILL.md); for synthesis use [report](../chrome-extension-builder-report/SKILL.md).
