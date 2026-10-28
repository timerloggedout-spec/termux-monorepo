# DoE Component Registry — Markov / Bayesian / Kahn / Gantt as integrated surfaces

**Registry:** `ops/doe/component-registry.json` (schema
`doe.component-registry.v1`). Owner order 2026-10-27 (Delphi lane).

The fleet's algorithmic components are registered as **separate
integrated surfaces**. Each component:

- is **individually evaluated** through the Delphi gate — one
  `delphi:rfp` per component surface id, scored per cycle like any
  surface (gate score = admission signal; the evaluation record is
  the outcome of record);
- **contributes to decisions** in its own role (beliefs to routing,
  Kahn plans to orchestration, waves to phase scheduling, Markov
  dynamics as a lab candidate);
- **improves itself under the DoE family** — evaluation findings
  convert to component revision PRs or explicit no-change records
  on the component's RFP, the loop discipline already running for
  `doe.criteria-loop` (#1959) and
  `delphi.method-self-application` (#1963). Components are never
  merged into one aggregate; comparison is per component, per
  cycle, inside the proposed `doe-components` segment.

## The components

| Surface id | Kind | Status | What it is |
|---|---|---|---|
| `markov.trellis-lab` | Markov | lab | ArchWiz Markov trellis experiment + proposal pack — state-transition modeling candidate |
| `bayesian.routing` | Bayesian | live | Beta-Bernoulli beliefs over the outcome ledger → posterior → value-of-information → route (`scripts/bayesian_routing.py`) |
| `kahn.dag` | DAG planning | live | Canonical Kahn primitives, `kahn-reference-v2` (`she/orchestration/dag.py`) — topo order, ready frontiers, cycle residuals |
| `gantt.dependency-phases` | Gantt | live | Dependency-phase engine (`validate → topological order → compute_waves`) over the canonical plan; Gantt views are derived, never authority |

## Wiring landed with this registry

- **Kahn deduplication:** the Temporal N4 compiler
  (`scripts/temporal/gantt_compile.py`) no longer re-implements
  topological ordering — it delegates to `kahn.dag`
  (`plan_dag`), emitting the algorithm version and graph sha256
  with every compiled plan. It keeps only filing-format parsing
  and aggregated violation reporting.
- **Gantt history as evidence:** the `gantt.dependency-phases`
  component's evidence feeds are the canonical plan
  (`docs/agentic/dependency-phases.json`), the generated
  status/history view (`docs/agentic/DEPENDENCY_PHASES.md`), the
  plan's git history, and the N4 compile evidence — including the
  dangling-dependency defect the compiler found in the fleet's
  filed Gantt template (dep `consensus implementation` vs the
  phase named `feature extraction + consensus implementation`;
  fix belongs to the filing template).
- **DoE separation visibility:** this registry is the separated
  component view; the DoE lane adds the four RFPs to
  `ops/delphi/rfp-segments.json` as the `doe-components` segment
  so the flood page renders them as their own group.

## Provenance notes

- Markov/Bayesian/Kahn/Gantt census verified firsthand 2026-10-27
  (code search + file reads on master).
- The Gantt system's multi-repo provenance: design by Manus;
  gantt-cli fork, GanTTY fork and Camshaft/GanttML were evaluated
  as inspiration/exporters only and are not control-plane
  authority (`docs/GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md`).
- Surfaces here are internal components, not vendor quota
  surfaces — they are deliberately NOT added to
  `ops/delphi/surfaces.json` (that registry is vendor limits with
  fetched sources only).
