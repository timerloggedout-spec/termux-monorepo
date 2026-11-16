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
