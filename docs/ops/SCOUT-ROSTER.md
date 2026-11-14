# Scout roster

`scout_roster.py` is the discovery boundary between live provider/model catalog evidence and the agent-team population.

## Contract

```text
provider catalog → normalized evidence → Scout roster → MVT → telemetry → MoneyBall/3L0 → admission
```

Scout does **not** grant production routing authority. It discovers candidates from observed provider data and preserves provenance. A model is a `candidate` when live evidence identifies it as zero-price, `:free`, or explicitly trial-eligible; paid/unknown models remain `observed` until another policy admits them.

## Anti-hardcoding rule

Provider/model identities should originate from the provider catalog. Current priority experiments such as OpenRouter `stealth/ox-alpha`, Felo OX Alpha, and DeepSeek are experiment selections, not permanent roster constants. Provider-specific documented trial evidence may be retained by the catalog collector, but Scout itself must remain identity-agnostic.

## Evidence fields

Every roster row retains provider, model, pricing/access classification, provenance source, observation timestamp, context/output capability metadata, and raw source. This allows later MoneyBall scoring to distinguish discovery evidence from execution evidence.

## Admission boundary

`candidate` means **eligible to probe**, not **proven capable**. Operational admission requires successful task probes, attributable telemetry, correctness/outcome evidence, regression checks, and the applicable manager/3L0 policy.

## BIUDL

Scout begins the broad population pass. Focused provider/model lanes then produce thin validated slices. Useful findings feed forward into the catalog, skills, telemetry schema, and manager policy before the population is broadened again.


## DoE-governed inference selection (owner clarification, 2026-11-12)

The discovery roster remains evidence-only: it establishes which provider/model endpoints are observed and potentially eligible. **DoE owns production allocation and rotation.** The active DoE design declares the campaign, task strata, eligible endpoint pool, assignment method/proportions, endpoint-level statistical tests, sample plan, stopping rule, multiplicity treatment, culling and promotion gates.

Scout has a scoped execution authority: it selects an eligible endpoint from the existing pool to realize the DoE-assigned treatment, using task-fit plus current capability, credential, catalog, quota and health evidence. Scout does not invent allocation weights, bypass a DoE assignment, or promote/cull an endpoint. A repeated endpoint is valid whenever the active design assigns it; there is no global no-repeat rule.

The selection receipt is the durable join between the DoE assignment and the actual invocation. It records the DoE design/version, Scout identity, manager/request identity, selected endpoint (provider + surface + model@version + protocol), pool snapshot, selection basis, custom-contract reference, exemption state and workflow/request/trace correlation IDs. Missing receipt means the run may be retained as historical/observational evidence but cannot be represented as a fully attributable DoE-assigned observation.

Each inference endpoint is evaluated independently. Provider-family or pooled means do not establish endpoint-level significance. Until that endpoint passes its pre-registered sample, effect-size, uncertainty, stopping and multiplicity gates, its standing is `NOT_ESTABLISHED`.
