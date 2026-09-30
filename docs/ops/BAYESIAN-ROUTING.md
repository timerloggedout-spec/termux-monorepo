# Bayesian + Uncertainty Layer for Optimized Routing

## Why this layer exists

The existing 3L0/Moneyball system measures outcomes, but routing also needs to represent **what the system does not know**.

A useful architecture is:

`evidence → likelihood → posterior state → decision/value-of-information → route → execution → evidence`

This is not a replacement for the evidence ledger. It is a probabilistic decision layer over that ledger.

## Bayesian primitives

### 1. Beta-Bernoulli outcome belief

For a binary task outcome:

`p ~ Beta(α, β)`

with observations updating:

`α' = α + successes`

`β' = β + failures`

Store the prior, observation counts, posterior mean, and credible interval. Never store only a naked score.

Use this for acceptance/correctness-like events, not latency.

### 2. Hierarchical / partial-pooling beliefs

A sparse provider/model/task lane should not be treated as either:

- completely unknown, or
- identical to every other lane.

Use a hierarchy such as:

`global → task_family → role → provider → model → provider×model×task_family`

This lets new candidates borrow limited statistical strength while remaining distinguishable.

### 3. Operational distributions

Latency, token consumption, retries, intervention time, and other continuous measures require a separate likelihood rather than pretending they are Bernoulli success.

The implementation should preserve raw observations and derive the distributional summary later.

### 4. Bayesian model averaging

There may be multiple plausible hypotheses:

- single-node route is sufficient;
- parallel scouting reduces integration time;
- a volley improves review quality;
- waiting is cheaper than another invocation;
- a specialist adds enough marginal value to justify its cost.

Keep competing hypotheses alive until evidence changes their posterior support.

## Exploration / exploitation

**Thompson sampling** is a natural routing supplement:

1. hard-gate candidates;
2. sample each candidate's uncertain utility;
3. select according to the active topology;
4. execute;
5. record the actual outcome;
6. update posterior state.

This is particularly useful for new models with little data.

It must never override:

- security policy;
- capability requirements;
- credentials;
- current-SHA rules;
- availability;
- quota;
- task ownership.

## Expected Value of Information

The manager should sometimes ask:

> Is another experiment worth doing before I commit to this route?

Approximate:

`EVI = expected decision improvement - experiment cost`

Experiment cost includes:

- provider requests/tokens;
- wall-clock delay;
- context consumption;
- duplicate work;
- conflict probability;
- human attention;
- quota opportunity cost.

If EVI is low, exploit the current route. If EVI is high, deliberately explore.

This prevents both premature certainty and endless benchmarking.

## Change-point awareness

Provider catalogs, pricing, models, quotas, prompts, repository architecture, and task distributions drift.

A posterior from six months ago should not silently have the same weight as a fresh controlled observation.

Record:

- observation time;
- catalog hash;
- environment fingerprint;
- policy version;
- task cohort;
- model/provider version where available.

When regime change is detected or strongly suspected, start a new epoch or apply an explicit decay policy.

## Alternatives to Bayesian inference

Bayesian inference is powerful, but it is not the only useful uncertainty/decision formalism.

| Method | Useful for | Important distinction |
|---|---|---|
| Bayesian | updating beliefs under uncertainty | requires explicit priors/likelihood assumptions |
| Thompson sampling | adaptive exploration | a policy, not a quality metric |
| Bayesian optimization | expensive black-box tuning | best for continuous/structured parameter search |
| Contextual bandits | route choice conditioned on task/context | less commitment than full sequential planning |
| MDP/POMDP | multi-step routes under uncertainty | useful when actions change future state |
| Dempster-Shafer / belief functions | conflicting/incomplete evidence | useful when probabilities are hard to justify |
| Conformal prediction | calibrated uncertainty sets | useful where distribution-free coverage matters |
| Causal inference | intervention effects | answers “what changed because of treatment?” rather than “what is likely?” |
| Survival / hazard models | time-to-event and failure | useful for cooldowns, completion, and reliability |
| Pareto optimization | competing objectives | avoids hiding tradeoffs inside one scalar |
| MCDA | explicit stakeholder criteria | transparent but weight-sensitive |
| Robust optimization | worst-case constraints | useful for safety and quota uncertainty |
| Scenario planning | foresight / discontinuities | useful where probabilities are inappropriate |
| Delphi / structured expert elicitation | expert uncertainty | useful for weak-data futures |
| Knowledge graphs / provenance graphs | relational evidence | complementary, not probabilistic by itself |

## Foresight integration

For the repository's existing foresight/cadence process, Bayesian inference should sit **beside**, not replace, scenario reasoning.

Use:

`foresight signal → hypothesis → scenario → MVT/DoE → observation → posterior update`

Do not assign artificial probabilities to futures merely because a number is convenient.

A scenario can remain qualitative until enough evidence exists to justify a probabilistic treatment.

## DAG / branch integration

The Git DAG is not the causal DAG.

Maintain two linked but distinct graphs:

**Engineering DAG**

`commit → parent → PR → check → artifact → integration`

**Decision/evidence DAG**

`hypothesis → treatment → observation → outcome → posterior → decision`

Join them with immutable identities:

`head_sha + run_id + run_attempt + artifact_digest + experiment_id`

A branch merge changes engineering state; it does not retroactively change historical evidence.

## 13-phase / cadence integration

Whatever the repository's established 13-phase foresight/implementation cadence calls each phase, attach probabilistic state to the phase transition rather than replacing the phase model.

A generic mapping is:

`signal → frame → hypotheses → alternatives → experiment → execute → observe → evaluate → update → integrate → verify → learn → next epoch`

The canonical project phase names remain authoritative; this mapping is an integration pattern only.

## Decision ledger

Every consequential routing decision should be explainable as:

`objective + constraints + eligible set + evidence snapshot + uncertainty state + selected topology + action + outcome + posterior delta`

This creates a durable debate/proposal history without turning debate volume into evidence.

## Debate handling

Treat proposals as hypotheses, not observations.

A debate can produce:

- hypothesis;
- assumptions;
- predicted observable;
- counter-hypothesis;
- disconfirming condition;
- proposed MVT;
- expected information gain.

Only execution/evidence updates the empirical posterior.

This cleanly separates **argument quality** from **empirical support**.

## Recommended control stack

`OPERATOR`
→ objective / constraints
→ **foresight**
→ classifier
→ Scout
→ manager
→ hard admission
→ **uncertainty engine**
→ topology selection
→ execution
→ evidence ledger
→ **causal/evaluation layer**
→ posterior update
→ decision ledger
→ DAG integration
→ next cadence

The important property is composability: no single mathematical formalism becomes the architecture's source of truth.
