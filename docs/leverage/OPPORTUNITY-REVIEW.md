# L3VERAGE opportunity review and compounding protocol

**Purpose:** choose the next intervention to investigate or experiment on without inventing a single opaque leverage score.  
**Authority:** CEEL owns capability discovery; DoE owns experiment admission/design; existing execution, evaluation, evidence, and promotion authorities retain their boundaries.

## Inputs

An opportunity enters review from a cited source, such as a CEEL capability opportunity, an observed workflow failure, a repeated handoff, a measured cost pattern, or a verified quality gap. The review points to existing records; it does not copy their payloads into a new L3VERAGE ledger.

Every candidate must name:
- source opportunity and evidence references, including source SHA/ref where available;
- the recurring task/workflow and affected cohort;
- the hypothesized mechanism and primary leverage class;
- the expected outcome and the basis for that expectation;
- known unknowns and the evidence confidence.

An unmeasured claim remains a hypothesis. A catalog entry is not evidence that the opportunity exists at scale.

## Opportunity vector

Review each candidate as a visible vector, not a weighted scalar:

| Dimension | Review question | Required representation |
|---|---|---|
| Expected impact | What verified outcome could change, and how broadly? | Range or ordinal band plus evidence/assumption |
| Implementation effort | What engineering, integration, and operator work is needed? | Estimate with basis and uncertainty |
| Confidence | How strong, current, and attributable is the evidence? | High / medium / low with source refs |
| Reversibility | Can the intervention be removed without lasting state change? | Easy / bounded / difficult, with rollback path |
| Risk | What correctness, privacy, security, fairness, or operational harm is plausible? | Explicit risks and hard stops |

Do not collapse these dimensions into an unregistered weighted score. Remove Pareto-dominated candidates from the shortlist only when another candidate is no worse on every declared dimension and strictly better on at least one. Preserve incomparable candidates and explain the trade-off.

The Leverage Opportunity Index is this inspectable vector and its evidence, not a prediction of realized value.

## Review dispositions

| Disposition | Meaning | Required next action |
|---|---|---|
| Investigate | Evidence is too weak to design an intervention | Identify the missing evidence and owner |
| Design | A falsifiable intervention can be specified | Draft baseline, treatment, cohort, metrics, guardrails, and stopping rule |
| Defer | Potential value exists, but timing/dependency is unfavorable | Record the dependency and re-review trigger |
| Reject | Evidence or risk makes the opportunity unsuitable | Preserve rationale and source references |
| Admit to DoE | Design is complete and the DoE owner accepts it | Commit the canonical campaign design record |
| Retain / adapt / combine | A completed experiment supplies relevant evidence | Create or update a mechanism proposal with traceable evidence |
| Retire / supersede | Mechanism no longer meets quality, cost, risk, or maintenance criteria | Preserve history and link the replacement or retirement reason |

Only the DoE owner admits an experiment. Only existing proposal and promotion authorities approve a production change. L3VERAGE cannot self-admit, self-promote, or change runtime routing.

## Compounding loop

1. Discover an opportunity from CEEL or verified operational evidence.
2. Register or link the mechanism hypothesis; keep its lifecycle state honest.
3. Compare the opportunity vector and identify the dominant uncertainty.
4. Design the smallest reversible experiment that can reduce that uncertainty.
5. Obtain DoE admission and record the canonical design.
6. Execute through existing workflows; preserve one canonical EXPERIMENT record per dispatched arm run.
7. Compare quality, correctness, integration, regression, attribution, and resource cost.
8. Retain, adapt, combine, defer, reject, or retire based on evidence.
9. Carry forward only verified learning, with source refs and versioned treatment identity.

A material treatment, cohort, evaluator, or scoring change is a new version or cohort under the DoE rules; it never silently rewrites prior observations. Multi-objective results retain Pareto trade-offs. Missing measurements remain missing.

## Review record template

Use an issue, proposal update, or campaign design record in its existing home. The following fields are a checklist, not a second canonical schema:

- mechanism ID and current lifecycle state;
- source opportunity IDs and immutable evidence references;
- target workflow/task class and affected cohort;
- expected impact and its basis;
- implementation effort and uncertainty;
- evidence confidence and freshness;
- reversibility and rollback path;
- risks, hard guardrails, and permission boundary;
- disposition, rationale, owner, and re-review trigger;
- if designing: baseline/treatment, assignment, outcome metric, resource vector, sample/stopping rule, and independent evaluator.

## Cadence

Review on new verified opportunity evidence, experiment completion, material risk change, or an explicit owner request. A periodic summary may help operators inspect the portfolio, but a calendar cadence is not the sensing mechanism and does not justify stale or fabricated status.
