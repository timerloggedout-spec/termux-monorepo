# Engineering Work Intake — QUE / QDesk Contract

**Status:** proposal
**Owner/lane:** QUE / QDesk + Engineering Toolchain Integration
**Canonical for:** engineering task metadata and reuse of existing queue machinery
**Review record:** PR for `feat/engineering-toolchain-activation` (review pending)

## Admission payload

An engineering task carries these typed fields in its normal QUE filing:

- `engineering_domain`: mechanical | electronics | electrical | simulation | manufacturing | semiconductor | visualization
- `toolchain_id`: stable ID from `ops/engineering/taxonomy.json`
- `stage`: current stage from the taxonomy workflow vocabulary
- `source_artifacts`: repository-relative paths or immutable artifact references
- `expected_artifacts`: required output paths/formats
- `environment_fingerprint`: OS/architecture/runner image/tool versions
- `verification_plan`: deterministic checks, solver checks and reviewer evidence
- `access_class`: local-free | cloud-free-tier | commercial-paid
- `physical_world_effect`: none | fabrication-submission | device-programming | physical-actuation
- `risk_tier`: informational | engineering-review | safety-critical

## Routing

1. File the work through the existing QUE intake contract and issue identity.
2. Reuse existing rank, admission, auto-claim, lease/reclaim, escalation and Desk/QDesk review.
3. Use existing `dispatch-queued` / project dispatch route where its current policy admits the task.
4. Route the work to a named capability and pinned execution environment. Keep arbitrary shell text out of issue-to-device routing.
5. Return a run receipt with source/input/output hashes, exact tool versions, environment fingerprint, exit state and validator results.
6. Send independent review and owner-gated decisions through existing QDesk/Desk authority.
7. Keep fabrication purchases, external submissions, device programming and physical actions approval-gated.


## Active intake surface

The repository issue form `.github/ISSUE_TEMPLATE/engineering-toolchain.yml` declares `issue-dispatch/v1`, lane `engineering-toolchain`, tier 3 and route `project-task-dispatch.yml`. Its unique `[engineering]` title prefix lets the existing `swarm-admission.yml` match the filing; the rendered `Task / spec`, `Scope` and `Done-evidence` headings feed the existing project-task intake parser. QUE admission stamps `swarm-admitted` or `deferred-by-tier`; the existing project dispatch and QDesk claim/lease flow remain the execution owners.

## Queue ownership

QUE remains the only queue and lifecycle authority. QDesk remains the existing recurring self-repair and oversight cycle. Engineering adds typed task metadata and capability discovery; existing QUE/QDesk machinery retains scheduling, claims, ranking, promotion and task storage.

## Terminal states

success | cleanly-skipped | blocked | approval-required | exhausted | stagnated

A queued/running job is pending. A successful process exit earns process-success status; engineering validity requires its verification plan and evidence. Missing evidence retains the `unknown` state.
