# Delphi Oracle Harmonious Intake — Design Specification

**Status:** implementation authorized 2026-11-24  
**Proposal:** `delphi-oracle-harmonious-intake`  
**Work items:** DORI-001, DORI-002  
**Base:** `master`

## Intent

Add a separate general-purpose Delphi Oracle Issue Form for existing-proposal evaluation, new proposals, refinement, research, comparisons, methodology improvement, and Harmonious Reconciliation. The form makes related research selectable with checkboxes and configures methodology, rounds, Question Matrix evolution, panel composition, oversight, and final disposition.

## Approaches

1. Expand the quota-specific `delphi-rfp.yml`: rejected because quota fields and generic research intent are different contracts.
2. Add a separate general-purpose form and intake workflow: selected because it preserves the working quota gate and gives general requests a dedicated parser, review record, and registry handoff.
3. Create one form per research family: deferred because the existing registries already provide a stable catalogue and one intake is easier to maintain.

## Form interaction

- Single-choice fields use dropdown menus.
- Multi-choice fields use checkboxes.
- Research selection mode is a checkbox group; the normalizer accepts exactly one selected mode. An empty group resolves to the documented prior default.
- The new form uses a distinct `[delphi:intake]` title prefix; the `delphi:rfp` label remains exclusive to the legacy quota gate. Intake automation accepts issue authors with OWNER, MEMBER, or COLLABORATOR association.

## Research selection modes

The machine-readable source catalogues remain authoritative:

- `ops/delphi/research-silos.json`
- `ops/delphi/research-participants.json`
- `ops/doe/component-registry.json`
- `ops/delphi/rfp-segments.json`
- proposal registry entries and linked issue IDs

The form exposes four checkbox choices:

| Choice | Resolution |
|---|---|
| DoE Decides | Record an eligible candidate pool; keep reconciliation targets pending until DoE selects them; execution remains false |
| All | Include all 12 research participants, all four DoE components, linked methodology RFPs/projects, and all four research arms |
| Specific selection | Include only the checked participants, components, methodology RFPs, and projects; baseline is the arm default |
| Prior default | Include the 12 baseline research participants; exclude variants, DoE components, and method RFPs. Independently checked project references remain available for reconciliation |

An empty selection-mode group resolves to Prior default. The 12 research silos remain independent segments; cross-silo aggregation stays disabled and comparisons remain silo-local. Arms are `baseline`, `rnd`, `selected`, and `control`. Absent source issue IDs remain explicit nulls while catalogue identity stays valid.

The checkbox catalogue includes all 12 registered participants, four DoE components, five methodology RFPs (#1567, #1571, #1572, #1959, #1963), and the related Strands / CEEL projects.

## Harmonious Reconciliation

The form captures selected projects and reconciliation dimensions: objectives, duplicate/overlapping proposals, requirements, dependencies, evidence, conflicting assumptions, decisions/dissent, and implementation sequencing. Submitter-selected targets must meet the category threshold. DoE Decides records candidate projects and references separately, marks target selection pending, and leaves confirmed reconciliation references empty until the DoE decision.

## Delphi and Question Matrix

- Method dropdown: Classical, Modified, Policy, Decision, Fuzzy, RAND/UCLA appropriateness, one-pass rubric, or Oracle recommends.
- Round profile dropdown: adaptive, fixed 2, fixed 3, fixed 4–5, or custom.
- Matrix strategy dropdown: shared, per-round, alternating, evidence-triggered, or custom.
- An optional per-round schedule captures round-specific matrix changes for custom/alternating strategies.
- Matrix strategy, method, and round settings are recorded as requested configuration. Method-specific execution requires a later engine adapter and its own validation.

## Panel and execution governance

- Panel context is fixed to `Termux-monorepo`.
- Existing five internal roles and optional human expert / stakeholder / model-participant categories are selectable.
- Human WebView oversight is optional.
- `execution: false` is immutable in every normalized record. Selection and catalogue operations remain governance records; separate authorization governs experiments, provider calls, live routing, and implementation.

## Execution and human-oversight boundary

This separate intake version normalizes requests and records method, rounds, Question Matrix, panel, and reconciliation configuration for review and catalogue reference. It does not invoke the existing Delphi gate engine or start a Delphi round. The optional WebView checkbox records a human-oversight request; the actual panel session remains an explicit review handoff. Every normalized record fixes execution to false. Selection review and catalogue publication are the workflow's promotion outputs.

## Disposition

- Selection review: emit an idempotent issue comment and apply the `delphi:selection-review` label; remove the label when the disposition changes away from review.
- Registry catalogue: open/update a PR containing one immutable source-linked JSON record under `ops/delphi/selection-catalogue/<selection_id>/<record_sha256>.json`.
- Both: perform both independent operations.
- Deliberation only: preserve the normalized record without requesting review or catalogue PR.

Catalogue contract: `ops/delphi/selection-catalogue.json`. Each immutable revision lives at `ops/delphi/selection-catalogue/<selection_id>/<record_sha256>.json`. Catalogue writes flow through a per-revision branch and PR against `master`; the workflow dispatches both `repo-gate.yml` and `termux-smoke.yml` on that branch so both promotion checks attach to its head SHA.

## Canonical record

Each record includes schema/version, stable selection ID, source issue and actor metadata, request category, research selection mode, resolved participant/component/RFP/project IDs, arms, segment-boundary policy, reconciliation dimensions, methodology, round profile, Question Matrix strategy/schedule, panel, WebView oversight, disposition, review flag, catalogue flag, and immutable `execution: false`.

## Acceptance criteria

1. Preserve the existing quota RFP form and gate.
2. Use dropdowns for single choice and checkboxes for multi-choice.
3. Resolve DoE Decides, All, Specific selection, and Prior default as specified.
4. Resolve the prior default to the 12 baseline research participants.
5. Expose all 12 participants and four DoE components through source-aligned checkbox lists.
6. Expose all five methodology RFPs and related Strands / CEEL projects.
7. Persist Matrix strategy and the optional per-round schedule.
8. Persist reconciliation dimensions, panel composition, and optional WebView oversight.
9. Keep review comments idempotent and synchronize the review label with disposition.
10. Strip rendered text fences and preserve Markdown headings in free-text answers.
11. Publish actionable issue comments for invalid intake submissions.
12. Open per-revision catalogue PRs and dispatch both promotion gates at the PR head SHA.
13. Preserve silo-local comparisons and disabled cross-silo score aggregation.
14. Fix `execution: false` in every normalized record.
15. Pass focused tests, proposal validation, repo-gate, Termux smoke, and exact-head PR checks.
