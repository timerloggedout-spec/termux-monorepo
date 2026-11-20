---
name: jules-doe-role-adapter
description: Apply the Jules-derived issue-analysis and local-verification patterns through the repository's canonical Design of Experiments roles and active agent router.
---

# Jules-derived DoE Role Adapter

## Source and status

Reference clone: `timerloggedout-spec/jules-skills_fork`

Pinned source revision: `7a76d3bfcf4258ee437d65b5d12e54b51c395de5`

License: Apache-2.0

Source skills, adapted locally:
- `.agents/skills/automate-github-issues/SKILL.md`
- `.agents/skills/local-action-verification/SKILL.md`

This adapter preserves useful workflow patterns as local role guidance. Provider execution and Jules session clients remain separate runtime capabilities.

Google Jules became read-only after 2026-11-11. The source skill's `@google/jules-sdk` calls and `JULES_API_KEY` dependency remain historical reference material. The source's sequential PR merge phase remains outside this adapter; repository merge authority stays with the governed merge process.

## Canonical DoE role bindings

Use the role names from `docs/ops/DOE-ROLES-EPOCH-2026-11-03.md`.

| DoE role | Jules-derived capability | Required output |
|---|---|---|
| observer | Issue census and current-state analysis | Sourced issue inventory and baseline |
| scout | Candidate triage and task decomposition | Candidate list, dependencies, and file-ownership proposal |
| builder | Implementation planning and local verification | Scoped implementation plan, changes, and test evidence |
| operator | Admission and dispatch governance | Approved route and dispatch receipt |
| steward | Claim and execution record custody | Append-only task, claim, and provenance records |
| reviewer | Independent verification | Exact-head verdict and findings |
| participant | Bounded task execution | One task claim, changed-file list, and result |
| gambler | Experiment forecast discipline | Cited prediction and scored outcome |

## Operating sequence

1. **Observer:** inventory the eligible issues and capture their labels, dependencies, timestamps, and current state.
2. **Scout:** group work by root cause and propose exclusive file ownership for independent tasks.
3. **Operator:** validate admission, conflicts, health, policy, and a concrete execution adapter before dispatch.
4. **Builder:** implement one bounded task using the active repository agent runtime and the approved branch contract.
5. **Reviewer:** run the repository gates and, where supported, local GitHub Actions verification with `act`; inspect the exact candidate head independently.
6. **Steward:** preserve the issue-to-task mapping, claims, changed-file inventory, check results, and PR links as append-only evidence.
7. **Participant:** report the task result against its accepted scope. The operator retains the dispatch and completion decision.

## Execution gates

- Provider readiness comes from a live adapter probe owned by the execution workflow.
- Evaluate credential presence and service availability as separate evidence dimensions.
- Evaluate role skill guidance and execution readiness as separate states.
- Multi-provider availability requires an explicit manager selection under the repository routing policy.
- Every implementation produces a reviewable branch or PR and exact-head verification evidence.
- Merge authority remains separate from builder and reviewer roles.

## Local verification

Use the source skill's `local-action-verification` pattern as a reusable builder/reviewer capability:

- identify the relevant workflow and job;
- run the supported local action job with `act` when the Docker/runtime prerequisites are available;
- preserve logs and the exact command/result in the task receipt;
- run the repository's authoritative CI gates as the final acceptance evidence.

## Repository references

- Role register: `docs/ops/DOE-ROLES-EPOCH-2026-11-03.md`
- Agent router: `docs/schemas/agent-roster.yaml`
- Dependency phases: `docs/agentic/dependency-phases.json`
- Route resolver: `scripts/agentic/dependency_phase_route.py`
- Execution boundary: `.github/workflows/dependency-phase-dispatch.yml`
