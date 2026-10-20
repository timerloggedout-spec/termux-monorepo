# EPS Implementation Matrix

| Initiative | Current disposition | EPS relationship | Next useful increment |
|---|---|---|---|
| #701 | LANDED | SSOT/session decisions are evidence metadata | ingest lane disposition + source SHA/run refs |
| #682 | EXTRACT / WAIT | ML DAG is a major EPS consumer/producer candidate | emit run/attempt/decision events only after dual-gate evidence |
| #432 / #549 / #601 | EXTRACT | ML wholesale family is historical evidence and reusable component source | extract stable schemas/reducers, not branches wholesale |
| #630 | EXTRACT | Jules provenance + dashboard behavior can become agent-event fixtures | capture agent/task/attempt provenance |
| #684 | HOLD / observe | cadence, concurrency, taint boundaries are telemetry dimensions | emit schedule/concurrency/provider-state events |
| #685 / #695 / #543 / #680 / #702 | OBSERVE | proposals, optimization, skill quality, catalog changes, and research seeds are heterogeneous evidence sources | normalize only metadata needed for reproducible evaluation |
| #48 / #69 / #73 | HOLD | connector/routing/debate history supplies provenance and boundary cases | preserve as historical fixtures; do not revive wrong-base code |

## Gravitee

#702 is relevant to EPS, but as a **research-seed / integration-observatory producer**, not as a telemetry dependency.

Its current proposal registers the Gravitee upstream research seed, preserves the local fork as a comparison surface, and explicitly avoids vendoring/submodules. That makes it useful for:

- API-management capability classification;
- gateway/plugin/policy/MCP capability observations;
- upstream-versus-fork provenance;
- Kubernetes/platform integration evidence;
- future API gateway telemetry experiments.

The useful extraction is the **observation contract**, not the upstream implementation wholesale.

### Gravitee + EPS boundary

`Repository Observatory → EPS research_observation → ML/Hex/Grafana → optional visualization`

Do not let Gravitee become a new execution plane or require its runtime before the observation contract is proven.

## Grafana

Grafana is complementary when EPS is projected into operational time series. Prefer derived metrics such as:

- event ingestion rate;
- validation failures;
- stale-event age;
- run/attempt completion latency;
- provider-state counts;
- action/effect yield;
- attribution-confidence distributions.

Grafana should alert on validated telemetry and link back to evidence identifiers.

## Hex

The existing `3l0.moneyball.v1` contract already has compatible grains: experiment run, agent task attempt, provider call, outcome score, and manager decision. EPS should provide the provenance envelope around those records rather than create a competing Moneyball schema.

Hex remains analytical/evidence presentation, with durable retention outside Hex where required.

## ML

ML should consume frozen EPS snapshots, never mutate the evidence plane. Candidate work includes:

- anomaly detection;
- cohort/regression analysis;
- provider/model routing evaluation;
- attribution-confidence calibration;
- graph/community analysis;
- cost/performance frontiers.

Any learned result is derived evidence and must retain source event IDs, source SHA/ref, model/version, timestamp, and uncertainty.

## Gource / visualization

Gource is a secondary renderer. Its compact custom-log format cannot carry EPS provenance, so EPS must remain canonical and a projection adapter should map EPS events into Gource events.

Future interactive surfaces may reuse the same adapter model without coupling telemetry collection to a particular renderer.
