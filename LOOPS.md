# Loop Library

Version: 1.0
Owner: Repository Stewardship
Canonical wait contract: `.agents/skills/adaptive-wait/SKILL.md`
Canonical feedback contract: `.agents/skills/adaptive-feedback-cycle/SKILL.md`

This library stores bounded, reusable operating loops. Each loop declares its trigger, inputs, steps, stop conditions, outputs, and safety boundary. Repository-native automation remains the execution authority.

---

## CYCLE-001 — Compounding RECON and Delivery

**State:** ACTIVE  
**Version:** 1.0  
**Trigger:** User-directed work, a material repository/runtime delta, a failed gate, a new evidence receipt, or a scheduled stewardship check.

### Inputs

- Repository, base ref, working ref, immutable head SHA, and current PR state.
- Canonical source files, issues, comments, workflow runs, artifacts, and receipts.
- Connected service/device capabilities and their authorization scope.
- User constraints, priority, desired outcome, and approval boundary.
- Existing operational skills, loop definitions, registries, and previous session receipts.

### Steps

1. **Scope** — identify the requested outcome, affected systems, force tier, and in-scope surfaces. Keep the active workset within four to five live items.
2. **Preflight** — read the canonical skill, current repo state, current base/head SHA, available connectors, and relevant source records. Record unavailable capabilities as BLOCKED.
3. **Reconstruct** — classify each finding as VERIFIED, OWNER-REPORTED, IN-REPO, EXECUTED, WIRED, CANDIDATE, STALE, CONFLICTED, or UNKNOWN. Preserve source timestamp and SHA.
4. **Prioritize** — rank work by user value, evidence confidence, downstream reuse, compute cost, risk, and dependency order. Close P0 data-path and runtime gaps before expanding optional surfaces.
5. **Plan** — create a bounded batch with one acceptance receipt per workstream. Reuse existing queues, schedulers, ledgers, scoring planes, and templates.
6. **Implement** — make the smallest coherent change; keep unrelated changes in separate commits/PRs. Use positive DO-form directives and preserve historical evidence.
7. **Validate** — run the smallest relevant local or repository-native checks; inspect the exact commit SHA, workflow revision, run, jobs, steps, logs, artifacts, and review state.
8. **WAIT subcycle** — while authoritative checks progress, perform bounded disjoint RECON. Re-fetch immediately after a commit, dispatch, rerun, review, failure, or state-changing receipt. Back off when the watched state is live and unchanged. Retry when a new attempt has an evidence-backed difference.
9. **Adapt** — classify failures as code, configuration, identity, quota, environment, source drift, or missing evidence. Change the cause before retrying. Reduce fan-out when provider/API limits appear.
10. **Compound** — join each verified artifact to eligible downstream consumers through stable IDs and hashes. Preserve each consumer's own acceptance test and scoring authority.
11. **Publish** — update the dated report, execution plan, source-of-truth docs, skill session log, commit, and draft PR. Record the exact resulting SHA and check receipts.
12. **Close** — state what passed, what changed, what remains blocked, and the next authoritative check. Continue with the next bounded batch when evidence can change the next action.

### WAIT evidence chain

`repository/ref/head SHA → workflow/run → jobs → steps/logs/artifacts → reviews/comments → resulting SHA/status`

Treat older-SHA evidence as historical after the head changes. Use the run's exact event payload and workflow revision when interpreting a result.

### Stop conditions

- All required checks and task outcomes reach authoritative terminal states.
- The next observation cannot change the next action; record the terminal receipt.
- Required authority, input, connector, capacity, or user-selected schedule time is missing; record BLOCKED with the exact dependency.
- Provider/API quota is exhausted; reduce request fan-out and wait for the authoritative reset or a changed execution path.
- A production, device, credential, merge, or schedule change reaches an approval boundary; hold for the required authorization.
- The current batch has a verified output and a bounded next batch is ready.

### Outputs

- Evidence-backed RECON report with dated sources and confidence labels.
- Prioritized execution plan with owner, acceptance criteria, and dependency.
- Small commits and reviewable draft PRs.
- Exact-SHA CI, artifact, runtime, and review receipts.
- Read-only compounding scorecard from canonical source ledgers.
- Session update to the adaptive-wait and adaptive-feedback-cycle skills.
- Explicit BLOCKED/UNKNOWN items with a next authoritative check.

### Safety

- Preserve canonical ledgers, source records, historical snapshots, and native score semantics.
- Keep activity, execution, task outcome, benchmark resolution, and promotion as distinct states.
- Use connected tools only within their documented authorization and user-approved scope.
- Keep secrets, authorization headers, raw private session content, and device-local state out of public repository artifacts.
- Keep production VM, routing, credential, wallet, and scoring changes behind explicit authorization and verified receipts.
- Reuse existing device jobs and schedules; capture current pending-job inventory before installation or replacement.
- Require a user-selected local time before creating a daily stewardship schedule.
- Keep merge, force-push, deployment, and promotion under their established review gates.

---

## Reuse notes

- Use `adaptive-wait` for the wait subcycle and immutable-SHA evidence chain.
- Use `adaptive-feedback-cycle` for regression learning and successor improvements.
- Use `evidence-led-monorepo-ops` for source hierarchy, identity, and promotion.
- Use the project QUE/Temporal/Adaptive Dispatch machinery for recurring work.
- Add a new loop only when it has a distinct trigger, inputs, stop conditions, and output contract.
