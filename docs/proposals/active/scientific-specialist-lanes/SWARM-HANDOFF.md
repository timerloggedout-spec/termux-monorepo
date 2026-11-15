# Swarm handoff — scientific specialist lanes and QDesk

**Status:** prepared; not dispatched  
**PR:** [#5190](https://github.com/timerloggedout-spec/termux-monorepo/pull/5190)  
**Branch:** `feat/que-scientific-psychology-lanes`

The Agent Swarm connector currently reports zero linked swarms. These task contracts are therefore committed as a handoff package, not represented as dispatched or assigned. Once a writable swarm is linked, send each task independently and require evidence artifacts.

## Task A — event/admission integration audit

**Type:** review · **Priority:** P0  
**Scope:** `.github/workflows/project-task-dispatch.yml`, `scripts/dispatch/admission_receipt.py`, `scripts/ops/swarm_admission.py`, tests.

Validate the event-driven dependency contract:
- `issues.opened` and `issues.reopened` remain first-class project-task route triggers.
- Admission evaluator remains authoritative and stamps the issue before intake.
- Fresh receipt timestamp and exact template identity are enforced.
- Deferred, stale, unmatched, and unrelated-template receipts never queue.
- Reopened issues re-evaluate and do not reuse stale admission decisions.
- Verify GitHub Actions expression semantics, API pagination, runner timeout, and retry behavior.
- Verify the event-keyed intake receipt marker prevents duplicate comments on retries while allowing a later reopen event to receive a new receipt.

**Acceptance:** automated contract tests plus a documented event trace for opened, reopened, deferred, malformed, and retry cases. No trigger replacement.

## Task B — scientific specialist role registry review

**Type:** review · **Priority:** P1  
**Scope:** `ops/roles/scientific-specialists.json`, `scripts/dispatch/project_task.py`, `scripts/dispatch/test_project_task.py`.

Review all 33 role contract seeds for:
- role scope, competence boundary, methods, inputs, outputs, evidence and abstention;
- independent reviewer separation for high-impact/confirmatory work;
- no conflation of provider identity with capability role;
- no new canonical DoE seat IDs;
- candidate role hints are not treated as assignments or qualifications;
- DO Statements and Performance Psychology remain separate measurable lanes.

**Acceptance:** schema validation, coverage matrix, negative tests, and an independent review report. Any additions must be justified by a missing capability, not role proliferation.

## Task C — QDesk proposal type/feed/UI review

**Type:** review · **Priority:** P1  
**Scope:** `docs/proposals/PROPOSAL-TYPES.md`, `docs/proposals/registry.yaml`, `scripts/proposals/proposals_feed.py`, `tests/test_proposals_feed.py`, `apps/tribute-dashboard/proposals.html`.

Verify:
- registry remains the single source of truth;
- `proposal_type` is optional for legacy records and carried verbatim;
- unknown values remain visible and are reported as feed gaps;
- `counts.by_type` excludes null values without inferring types;
- the UI Type filter derives only from feed values;
- `desk.html` remains the operational queue/traversal projection, not a second proposal registry.

**Acceptance:** feed collector tests, browser/UI smoke evidence, and a concise migration note. Do not rewrite legacy proposal classifications without owner-approved evidence.

## Shared execution rules

- Use the existing repo gate and Termux smoke; do not invent a parallel CI gate.
- Report commit SHA, exact commands, test results, artifacts, and remaining gaps.
- Do not merge PR #5190 or promote experiments.
- Failures are observations; do not rerun merely to obtain green status.
