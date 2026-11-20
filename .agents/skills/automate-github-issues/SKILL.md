---
name: automate-github-issues
description: Analyze, decompose, admit, and coordinate GitHub issue work through the repository's canonical DoE roles and active provider router.
---

# Automate GitHub Issues — Local DoE Adaptation

## Source lineage

- Upstream fork: timerloggedout-spec/jules-skills_fork
- Source revision: 7a76d3bfcf4258ee437d65b5d12e54b51c395de5
- Upstream skill: automate-github-issues
- License: Apache-2.0

The upstream scripts use @google/jules-sdk and JULES_API_KEY. This local adaptation uses the repository's active agent router and DoE role register. The upstream sequential merge stage remains outside this workflow; merge authority stays with repository governance.

## Five-stage workflow

1. **Analyze — observer**
   - Inventory eligible open issues and capture labels, milestones, timestamps, dependencies, and current status.
   - Produce a structured issue census with source links and a baseline timestamp.
2. **Plan — scout**
   - Group issues by root cause and dependency.
   - Produce bounded task prompts with acceptance criteria, test requirements, expected outputs, and file ownership.
3. **Validate — operator + steward**
   - Check file ownership for exclusive task boundaries.
   - Validate dependencies, admission policy, repository health, and candidate readiness.
   - Preserve the issue-to-task ledger and ownership map.
4. **Dispatch — operator + builder + participant**
   - Resolve the capability through docs/schemas/agent-roster.yaml.
   - Require a concrete adapter readiness signal from the owning execution workflow.
   - Use explicit manager selection when multiple adapters are available.
   - Record the claim, selected provider, branch, and task receipt.
5. **Review and handoff — reviewer + steward**
   - Verify the exact candidate head with repository checks.
   - Capture changed files, test evidence, review findings, and PR links.
   - Route merge decisions through the repository's established authority.

## DoE role bindings

- **observer:** issue census and baseline evidence.
- **scout:** candidate triage, decomposition, dependencies, and file ownership proposals.
- **operator:** admission, ordering, provider selection, and dispatch.
- **builder:** scoped implementation under the active provider runtime.
- **participant:** one admitted task execution with a bounded claim and result.
- **reviewer:** independent exact-head verification.
- **steward:** append-only issue, task, claim, and provenance records.
- **gambler:** cited experiment forecast and scored outcome, separate from implementation execution.

## Repository control points

- Role register: docs/ops/DOE-ROLES-EPOCH-2026-11-03.md
- Agent roster: docs/schemas/agent-roster.yaml
- Dependency plan: docs/agentic/dependency-phases.json
- Route resolver: scripts/agentic/dependency_phase_route.py
- Dispatch workflow: .github/workflows/dependency-phase-dispatch.yml

## Execution contract

- Treat credential presence and service availability as separate evidence dimensions.
- Treat role guidance and provider execution as separate states.
- Require an observed adapter readiness signal before applied dispatch.
- Require exclusive file ownership for parallel tasks.
- Preserve independent review and exact-head validation.
- Keep merge, force-push, and promotion decisions under repository governance.
