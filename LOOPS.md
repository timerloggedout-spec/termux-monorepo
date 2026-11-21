# Project Loops

Reusable bounded loop prompts for this repository. These prompts describe an operating method; they do not create schedules, invoke providers, or grant repository/production permissions. Read the canonical skills and proposal governance before execution.

## Adaptive Repository Steward Loop

A current-SHA stewardship loop for one authorized repository task. Stop when the requested outcome is verified or a named terminal condition is reached.

**Prompt:**

> Observe fresh repository, proposal, branch, PR, and workflow state bound to an immutable SHA. Choose the highest-value authorized item using priority, risk, dependencies, and measurable outcome. Act once on an isolated feature branch. Verify with deterministic tests and required gates on that SHA. Record evidence IDs, deltas, decisions, outcome, and uncertainty. Repeat only while new evidence can change the next action or progress is measurable. Stop at success, clean-no-op, blocked, approval-required, exhausted, or stagnated. Never merge, alter credentials, or resume suspended production automation without explicit authorization.

**Saved:** 2026-11-06

**Source:** Custom repository adaptation of the user-supplied Loopy Skill Documentation JSON; source version/commit not supplied; not published to the Loop Library.

**Native owners:** .agents/skills/adaptive-wait/SKILL.md, .agents/skills/adaptive-feedback-cycle/SKILL.md, .agents/skills/evidence-led-monorepo-ops/SKILL.md, docs/ops/ORCHESTRATION-RECEIPT.schema.json.

**Terminal semantics:** execution state, task outcome, and promotion remain separate. A completed run or green check is not task success; task success is not automatic promotion.
