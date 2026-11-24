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
| DoE Decides | Record an eligible candidate pool for DoE selection; leave the decision pending and execution false |
| All | Include all 12 research participants, all four DoE components, linked methodology RFPs/projects, and all four research arms |
| Specific selection | Include only the checked participants, components, methodology RFPs, and projects; baseline is the arm default |
| Prior default | Include the 12 baseline research participants; exclude variants, DoE components, and method RFPs. Independently checked project references remain available for reconciliation |

An empty selection-mode group resolves to Prior default. The 12 research silos remain independent segments; cross-silo aggregation stays disabled and comparisons remain silo-local. Arms are `baseline`, `rnd`, `selected`, and `control`. Absent source issue IDs remain explicit nulls while catalogue identity stays valid.

The checkbox catalogue includes all 12 registered participants, four DoE components, methodology work (#1572, #1959, #1963), and the related Strands / CEEL projects.

## Harmonious Reconciliation

The form captures selected projects and reconciliation dimensions: objectives, duplicate/overlapping proposals, requirements, dependencies, evidence, conflicting assumptions, decisions/dissent, and implementation sequencing. The normalizer records these as requested reconciliation inputs and preserves the distinction between evidence, candidates, and a confirmed decision.

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

## Disposition

- Selection review: emit an idempotent issue comment and apply the `delphi:selection-review` label.
- Registry catalogue: open/update a PR that appends or revises the source-linked record in `ops/delphi/selection-catalogue.json`.
- Both: perform both independent operations.
- Deliberation only: preserve the normalized record without requesting review or catalogue PR.

Catalogue contract: `ops/delphi/selection-catalogue.json`. Each immutable revision lives at `ops/delphi/selection-catalogue/<selection_id>/<record_sha256>.json`. Catalogue writes flow through a per-revision branch and PR against `master`; merged PRs publish catalogue records.

## Canonical record

Each record includes schema/version, stable selection ID, source issue and actor metadata, request category, research selection mode, resolved participant/component/RFP/project IDs, arms, segment-boundary policy, reconciliation dimensions, methodology, round profile, Question Matrix strategy/schedule, panel, WebView oversight, disposition, review flag, catalogue flag, and immutable `execution: false`.

## Acceptance criteria

1. Existing quota RFP form and gate remain unchanged.
2. The new form uses dropdowns for single choice and checkboxes for multi-choice.
3. DoE Decides, All, Specific selection, and Prior default resolve as specified.
4. The prior default is the 12 baseline research participants.
5. All 12 participants and four DoE components are selectable from source-aligned checkbox lists.
6. Method RFPs and Strands/CEEL projects are selectable.
7. Matrix strategy and optional round schedule persist.
8. Reconciliation dimensions, panel, and optional WebView oversight persist.
9. Review comments are idempotent.
10. Catalogue dispositions open a PR to `master`.
11. Cross-silo score aggregation remains disabled.
12. Every normalized record fixes `execution: false`.
13. Focused tests, proposal validation, repo-gate, Termux smoke, and exact-head PR checks pass.
