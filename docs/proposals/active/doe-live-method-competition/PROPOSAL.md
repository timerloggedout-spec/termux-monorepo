# Proposal: DOE / MVT live method-competition framework (repo-wide)

Status: proposed (docs-only; no runtime changes)
Filed: 2026-10-27
Refs: #1573 (cadence program parent), #1595 (derived quota census — prerequisite), #1596 (cadence reconciliation fan — prerequisite)
Provenance: adapted from external DOE/multivariate-testing research; re-grounded on this repository's live surfaces by the operator's directive that method comparisons run LIVE across all lanes (no/minimal sandboxes).

## 1. Purpose

Establish a repository-wide system for comparing competing methods — every concept, lane, and cross-lane dependency gets a traceable evaluation question, eligible alternatives, controlled conditions, outcome measures, and promotion criteria. Classical design-of-experiments (DOE) presumes isolated sandbox execution; this repository runs live. This proposal therefore replaces the sandbox stage of the DOE control loop with existing repo surfaces, and keeps every existing authority (workflow-surface-policy, drift guard, repo_gate, human merge) binding.

## 2. Live-mode substitution map (binding)

| DOE stage (classical) | Live repo surface (this proposal) |
| :-- | :-- |
| Pinned snapshot | Commit SHA recorded in every experiment contract |
| Isolated sandbox execution | Ephemeral feature branch (dispatch-only, self-deleting — pattern proven by the `supabase-url-provision` / `supabase-anon-key-provision` runs) plus per-run state via `workflow_dispatch` inputs. Never assume environment isolation on shared runners. |
| Randomized assignment | Dispatcher verdicts (`quota-dispatch-tree` nodes A–H) and lane `workflow_dispatch` inputs as factor-level switches |
| Factor levels | Shipped dormant-until-config (vantage-cost-report pattern: exit-0 dormant, `strict` flag) so live traffic flows only when a level is explicitly woken |
| Run records | Supabase `dispatch_verdicts` (live end-to-end since 2026-10-25) + `action-effectiveness-ledger` telemetry. OWNER RETENTION rule applies: experiment rows are never deleted. |
| Sample-ratio-mismatch / assignment-integrity gate | #1596 cadence reconciliation fan (actual vs planned 24h run counts), once #1595 census fields land |
| Run-budget / cost ledger | #1595 derived `runs_per_day` census; quota is the DOE run budget |
| Confirmation set | Held-out tasks / later time windows; predeclared stopping rules, no repeated fixed-horizon peeking |
| Promotion authority | UNCHANGED: gates, drift guard, human merge. A favorable live comparison never becomes a merge permission. |

## 3. Unit-of-observation discipline

- One dispatched workflow run = one observation of that lane at that factor setting.
- Repeated wakes of the same lane are repeated measures, not independent tasks.
- Block by lane and hour-of-day: GitHub cron throttling (observed ~6/day vs 144/day planned for the dispatcher) makes planned vs observed cadence diverge; power/sample-size calculations MUST use observed dispatch rate, not cron math.
- Record trigger source (scheduled dispatch vs operator-wake comment vs manual `workflow_dispatch`) in every run record, or operator intervention confounds method effect.
- Post-merge superseded/canceled builds are excluded; count only settled final builds (the build-21280 precedent).

## 4. Fair-competition rules

1. Compare equivalent work: shared capability contract defined before any comparison; two similarly named lanes are not automatically substitutes.
2. Separate method effects from resource effects: equal-quota and equal-quality-target comparisons are separate experiments. A lane woken 4x/hour must be quota-normalized before comparison against one woken once.
3. Respect dependence: matched task instances where appropriate; shared sessions, caches, reviewers, and state link observations — blocking and replication must reflect that.
4. Preserve mandatory safety: credentials, secret-name wiring, approval gates, and source authority are controlled conditions, never factors.
5. Separate exploration from confirmation: screening first, held-out confirmation for finalists, predeclared stopping procedures.

## 5. Coverage ledger

Every discovered artifact receives a disposition before it can enter a comparison: active implementation / maintained specification / concept or proposal / reference-only / generated output / historical or recovered / duplicate or alias / blocked / unknown. Three governance ratios (classification, evaluation, evidence coverage) are computed against separate denominators; "100% coverage" claims are invalid while unknown or blocked areas are silently excluded.

## 6. Experiment contract (record shape)

```yaml
experiment:
  id: REQUIRED            # e.g. context-routing-x-compression-001
  status: proposed
  provenance:
    repository: timerloggedout-spec/termux-monorepo
    base_sha: REQUIRED
    owning_source: REQUIRED
  scope:
    capability: REQUIRED  # shared behavior contract
    lane_ids: [REQUIRED]
    execution_environment: live-dispatch  # ephemeral-branch if isolation needed
  hypothesis: { statement: REQUIRED, predeclared_threshold: REQUIRED }
  factors: { }             # factor: [levels]; levels dormant-until-config
  design:
    type: REQUIRED         # blocked factorial / fractional / paired
    blocks: [lane, hour-of-day]
    assignment: dispatcher-verdict | workflow_dispatch-input
    trigger_source_recorded: true
    replication_plan: REQUIRED
  outcomes:
    primary: REQUIRED
    secondary: [ ]
    constraints: [no-unauthorized-actions, retention-rule]
  analysis:
    target_effects: [ ]
    observed_vs_planned_cadence: REQUIRED   # power uses observed rate
  decision:
    allowed_results: [reject, inconclusive, confirm, candidate-for-review]
    promotion_authority: existing-repository-policy
```

## 7. Implementation sequence

| Phase | Deliverable | Exit condition |
| :-- | :-- | :-- |
| 0 | Pin commit; read canonical entry points | Owners, constraints, gates identified |
| 1 | Artifact + lane inventory with dispositions | Unknowns/blocked visible |
| 2 | Capability normalization to shared contracts | Real competitors separated from complements |
| 3 | Common run-record + outcome definitions | Reference runs reconcile |
| 4 | Pilot 1 (lane-local) + Pilot 2 (cross-lane) | Assignment, scoring, analysis verified |
| 5 | Screening across eligible lanes | Promising factors recorded with limits |
| 6 | Held-out confirmation of finalists | Gains + uncertainty documented |
| 7 | Reviewable evidence-backed proposal | Existing review/gates satisfied |
| 8 | Version-triggered reevaluation | Results marked current/stale/superseded |

## 8. First two pilots (proposals, filed as sub-issues of #1573)

1. Context routing x CedrLang compression — factor levels from the open Linguist PRs (#1607, #1642, #1679); outcomes: semantic fidelity, token density, decode failures.
2. Dispatch topology x quota policy — dispatcher node verdict timing x `max-parallel` / `max-busy` admission; outcomes: queue delay, admission pauses, settled-build rate.

## 9. Quota delta, risks, validation

- Quota delta: 0 (docs-only). Pilots and future experiments must state their runs/day cost against the #1595 census and fit the post-consolidation budget.
- Risks: live confounding from cron throttling and operator wakes (mitigated by §3), experiment rows consuming `dispatch_verdicts` write budget (300 rows/hour anon trigger cap — record, do not spam), over-claiming from unreplicated live runs (mitigated by §4.5).
- Validation: pilot contracts must reconcile reference runs against recorded metrics before any lane-wide rollout (Phase 3 exit condition).
