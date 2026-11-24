---
id: delphi-oracle-harmonious-intake
title: "Delphi Oracle — Harmonious Reconciliation and Research Selection Intake"
author: ChatGPT
posted_at: 2026-11-24
source: "Operator directive: build a separate version of Delphi Oracle intake, expose related research as checkbox selections, support DoE Decides / All / specific selection / prior default, and continue through merge to master."
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues:
  - 1572
  - 1959
  - 1963
related_prs:
  - 1630
related_branches:
  - feat/delphi-oracle-harmonious-intake-20261124
gates_required:
  - proposal-lifecycle
  - repo-gate
  - termux-smoke
---
# MANIFEST — delphi-oracle-harmonious-intake

## Intent

Build a separate general-purpose Delphi Oracle intake that supports proposal lifecycle requests, Harmonious Reconciliation, methodology and round configuration, versioned Question Matrix strategies, research cohort checkboxes, optional human WebView oversight, and explicit selection-review / registry-catalogue dispositions.

## Authorization

Operator directive received 2026-11-24: "Build whatever you want as a separate version. Notify me when it's on master and available for review. ... Work until Merge master." This authorizes implementation, branch/PR creation, review, required validation, and merge when repository promotion conditions are met.

## Source-of-truth boundaries

- Preserve `.github/ISSUE_TEMPLATE/delphi-rfp.yml` as the quota/provider-specific intake.
- Reuse `ops/delphi/research-silos.json`, `ops/delphi/research-participants.json`, `ops/doe/component-registry.json`, `ops/delphi/rfp-segments.json`, and the proposal registry as catalog authorities.
- Preserve one segment per research silo; never aggregate or leak scores across silo boundaries.
- Preserve the research lane's prior default: all 12 baseline research participants, with no evolutionary variants or DoE component selection.
- Selection creates review/catalogue records only. `execution: false` is immutable in this intake.
- Registry catalogue updates flow through a branch and PR; intake automation does not commit directly to master.
- Human WebView oversight is optional and metadata-only in this slice.

## Scope

- Separate GitHub Issue Form and event-driven intake workflow.
- Deterministic issue-body parser, canonical selection record, catalogue validation, and focused tests.
- Research selection modes: DoE Decides, All, Specific selection, Prior default.
- Checkbox catalogues for the 12 research participants, four DoE components, related method RFPs, and related research projects.
- Matrix schedule, per-round schedule, Delphi method, round profile, reconciliation dimensions, panel, optional oversight, and disposition.
- Idempotent selection-review comment and catalogue PR workflow.
- Documentation, proposal work ledger, and CI coverage.

## Non-goals

- Replace or modify the legacy quota RFP gate or its scoring engine.
- Dispatch research experiments, provider calls, model ballots, implementation jobs, or live routing.
- Aggregate research scores across silos.
- Build a WebView application or grant new external permissions.

## Promotion

Merge to `master` only after independent review, proposal lifecycle validation, repo-gate, Termux smoke, focused Delphi intake tests, and same-head SHA evidence are green. Re-fetch checks and the PR head before promotion.
