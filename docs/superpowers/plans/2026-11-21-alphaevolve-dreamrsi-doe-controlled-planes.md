# AlphaEvolve × Dream-RSI DoE controlled planes

**Proposal:** continuous-capability-evolution-lab

**Work item:** CCEL-005

**Base:** `263a2291fd4e38958758dd0e361f712f69bccc3c`
**Implementation branch:** `feat/doe-controlled-evolutionary-planes-20261121`

## Objective

Make DoE the experimental design and assignment authority around the existing bounded evolutionary replay primitive. AlphaEvolve-style policy generation and Dream-RSI-style replay remain bounded components; the DoE plane freezes factors, levels, control, cohorts, blocks, randomization, replication and analysis lineage.

## Plane boundaries

| Plane | Owner | Responsibility | Evidence |
|---|---|---|---|
| Design/control | DoE family | Pre-register hypothesis, factors, levels, control, seed, blocks, replication and thresholds | Evolution DESIGN artifact |
| Candidate generation | EvolutionEngine | Generate bounded data-only policy candidates; retain incumbent | policy IDs + generation lineage |
| Replay/evaluation | ReplaySimulator | Deterministic read-only evaluation over one immutable history revision | replay rows + history size |
| Online execution | ATES + existing runner | Execute at most the selected candidate in a fresh cohort | canonical EXPERIMENT records |
| Analysis/challenge | existing DoE reducers + Delphi | Estimate main/interaction effects, uncertainty, missingness, costs and alternatives | analysis + review evidence |
| Promotion | proposal lifecycle + dual gates | Review verified task outcome, correctness, integration and same-SHA gates | proposal decision |

## Implementation

1. Add a pure-stdlib DoE adapter for policy-factor full factorials, incumbent control retention, offline replay evidence and a separate randomized confirmation assignment for one selected candidate.
2. Add strict JSON Schemas for the offline design and online confirmation assignment; keep per-run observations in the canonical EXPERIMENT schema.
3. Validate design identity, unique arms and exactly one incumbent control; validate the separate confirmation assignment for control/selected-candidate membership, block consistency, per-unit/per-replicate completeness and contiguous sequence.
4. Add unit tests for deterministic assignment, factor validation, control retention, replay lineage and fail-closed promotion readiness.
5. Update the evolutionary replay operating contract and skill with the DoE plane separation.
6. Keep execution, external providers, production routing and promotion outside this module.

## Acceptance

- Identical frozen inputs produce byte-equivalent design objects and IDs.
- Incumbent appears exactly once as the explicit control in every design.
- Each online confirmation task unit × replicate receives only the incumbent and one selected candidate exactly once in deterministic randomized order.
- Every replay arm uses the same simulator/history object and is labeled `replay_only`.
- Design IDs, campaign IDs, policy IDs, confirmation IDs and assignment IDs are attributable. Online confirmation assignments contain only the incumbent and one selected candidate.
- Promotion readiness remains false until replay threshold, held-out confirmation, verified task outcome, correctness, integration, repo gate and Termux smoke all pass.
- The module performs no network/provider calls, code execution, repository writes or promotion.

## Validation

```bash
python -m unittest discover -s tests/agent_evolution -p 'test_*.py' -v
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

The current session can create and inspect GitHub objects; it does not provide a local checkout or shell runner. These commands require CI execution on the resulting immutable PR head before any pass claim.
