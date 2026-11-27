# Gate Admission Optimization — Design

**Status:** Operator-authorized; implementation in progress  
**Date:** 2026-11-27  
**Repository head inspected:** `341ee481f3d829652e816789c0f9dbfc661897fd`  
**Proposal:** `gate-admission-optimization`

## Objective

Select validation and provider work from the changed execution surface, reference impact, quota state, and expected incremental evidence. Keep the universal repository floor small and deterministic.

## Evidence observed

- `.github/workflows/termux-smoke.yml` currently starts on every pull request and configured integration push. Its job installs PyYAML and pytest to run bucket-headroom tests alongside Termux smoke.
- `scripts/ci/termux_smoke.py` checks the Termux runtime contract, repository gate files, SIM-memory contract, connector smoke, and optional deepcli/archwiz surfaces.
- `.github/workflows/archwiz-dangle.yml` currently triggers on dangle implementation files, `.github/workflows/**`, and `apps/**`. Its census scope is `.github/` and `apps/`; its baseline ratchet and rename mode remain read-only.
- Vercel has project-scoped ignore helpers and a quota-aware batch lane. Live inspection found the linked `historical-corpus-explorer` project building from repository entrypoint `.`; its latest 24-hour window contained 96 deployments, including 42 from `master` and multiple unrelated refresh branches. The docs/test-only PR received a `build-rate-limit` status. The project was updated to root `apps/historical-corpus-explorer`, enable affected-project deployment filtering, and compare changes against that app path. A checked-in `vercel.json` and helper mapping now keep this policy in source control. The post-update docs-only head has no matching deployment record; its Vercel status still reports `build-rate-limit`, so provider-effect verification remains pending.
- The current gate register records Devin API access as paid-organization-only and card-blocked for the Free organization. The referral programme index names other providers and does not establish a Devin credit route. The operator's 2026-11-27 report of free-tier availability and referral replenishment is retained as a fresh evidence lead pending a current account/entitlement receipt.

## Chosen design

### 1. Universal repository floor

- Run `repo-gate` on every pull request and integration push.
- Run the Siglary mandate validator against the exact candidate SHA before promotion.
- Keep the repo gate stdlib-only and deterministic.

### 2. Surface-aware Termux execution

Keep the `agentic termux smoke` workflow check present for every pull request and configured integration push. Add a fast, stdlib-only admission step that compares changed paths with one canonical Termux surface registry.

- Matching paths execute smoke regression tests, core smoke, and optional agent-surface probes.
- Unmatched paths emit an explicit `SKIPPED` reason and finish the workflow check successfully for branch-protection continuity.
- Missing base/head evidence or diff errors fail closed to executing smoke.
- Manual `workflow_dispatch` executes smoke.
- The downstream PR classifier reads changed paths and a separate `termux_smoke_required` field. A successful admission skip is treated as not applicable, rather than as smoke execution evidence.

The initial Termux surface registry covers the smoke script and its required files, SIM-memory contract files, connector smoke, deepcli/multi-ai launchers, ArchWiz, and the Termux multi-agent/dashboard surfaces.

### 3. Separate bucket-headroom contracts

Move the PyYAML/pytest bucket-headroom tests into a dedicated path-scoped workflow. Keep those tests close to `scripts/ops/bucket_headroom.py` and `.github/workflows/bucket-headroom-watch.yml`. Keep package installation out of the Termux smoke workflow.

### 4. Reference-aware dangle admission

Expand dangle workflow triggers to include the target roots used by workflow scripts, application links, docs, ops data, configs, tests, and context/agent surfaces. Preserve the current `.github/` and `apps/` census scopes, existing baseline ratchet, read-only rename verifier, and report artifact.

### 5. Provider lanes

**Vercel:** preserve the existing project-scoped path selector, quota-aware batch dispatcher, reserve, and cooldown. Scope `historical-corpus-explorer` to `apps/historical-corpus-explorer`, enable affected-project deployment filtering, and use the project-specific ignore command. Keep preview deployments available for relevant app changes. Track provider-side skip/build confirmation as a separate evidence state; configuration and local tests establish setup while deployment receipts establish provider effect.

**Devin:** treat Devin as an optional bounded worker, never a required merge gate. Admission requires current evidence for API eligibility, free quota remaining, task fit, billing boundary, and referral-credit provenance. Keep subscription eligibility, API quota, and marketing referral rewards as separate fields. The operator-reported availability remains a lead until a current provider/account receipt supports it.

## Gate result vocabulary

| State | Meaning |
|---|---|
| `PASS` | Required gate completed successfully on the exact candidate SHA |
| `FAIL` | Required gate completed with a failing result |
| `SKIPPED` | Surface classifier marked the gate inapplicable; include the matched/absent surface reason |
| `BLOCKED` | Admission requires evidence or authorization that is currently unavailable |
| `PENDING` | Gate admitted and awaiting execution/result |

A skipped conditional gate records applicability; execution evidence is represented by PASS or FAIL. A provider quota deferral records capacity; code correctness remains separate.

## Alternatives considered

1. **Path-filter the entire Termux workflow.** Rejected because skipped workflows can leave a required status check absent and downstream classifiers would lose the distinction between inapplicable and missing evidence.
2. **Always execute every gate.** Rejected because unrelated changes pay the full smoke and provider cost.
3. **Introduce a central dynamic workflow orchestrator.** Rejected because native workflow triggers and one small stdlib classifier cover the current need with fewer moving parts.

## Acceptance criteria

- The Termux workflow check remains visible on every PR; the smoke command runs only when the shared path classifier admits it or when manually dispatched.
- Unknown diff state admits smoke, preserving fail-closed behavior.
- Bucket-headroom tests execute in a dedicated path-scoped workflow.
- The PR classifier treats a non-Termux slice as eligible without Termux smoke while preserving required evidence for Termux slices.
- Dangle triggers cover both source and target path changes while retaining its baseline and report contract.
- Vercel `historical-corpus-explorer` uses its app root and affected-project filtering; an unrelated post-update commit produces no deployment record and a relevant app change produces an app-root deployment.
- Devin remains optional until fresh account and referral evidence supports no-cost admission.
- Repository policy, proposal records, tests, and workflow behavior agree.
