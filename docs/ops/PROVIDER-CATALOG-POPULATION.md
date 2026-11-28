# Full Provider/Model Pool Population

**Population contract:** `provider-model-population/v1`  
**Population version:** `1.0.0`  
**DoE:** `DOE-VULTR-CATALOG-001 v3.0.0`  
**Mode:** deterministic offline reconciliation and tournament seeding

## Scope

The adapter map in `scripts/provider_model_catalog.py` is one observation surface, not the provider universe. The population compiler reconciles the quota/service registry, dispatch model-lane bench, g4f working catalog, g4f endpoint universe and optional incumbent v5 observation snapshot.

| Layer | Repository evidence | Interpretation |
|---|---:|---|
| Quota/service registry | 172 service records | All lanes; records are not unique model providers |
| Dispatch model bench | 91 model records / 89 distinct providers | Registry-backed model-lane identities |
| g4f working catalog | 60 providers / 4,242 raw rows / 4,241 distinct pairs | Reference catalog; 100 reported working entries across 15 providers, not runtime admission |
| g4f endpoint universe | 160 providers / 9,588 pairs | 5,347 upstream-only + 1,156 fork-only + 3,085 overlapping pairs; enumeration, not live availability |
| Actions endpoint census | 7,341 provider×model endpoints | Historical verified floor dated 2026-11-01; retain its Actions-only evidence rule |
| Incumbent v5 | Snapshot-dependent | Live catalog observations from configured adapters |

The 7,341 historical verified floor and 9,588 enumerated universe are separate populations. The compiler preserves both; it never sums them or relabels enumeration as live verification.

## Build

```bash
python3 scripts/provider_catalog_population.py --output-dir /tmp/provider-population
python3 -m scripts.provider_catalog_competition --population-input /tmp/provider-population/population-v1.json --output-dir /tmp/provider-tournament
```

The first command emits a source-hash-bound `population-v1.json` and `manifest.json`. The second emits the Incumbent full-pool representation, VultrInspired full-pool projection and paired manifest. Add `--incumbent-v5 /path/to/catalog.json` to include a current v5 observation snapshot.

## Tournament population

All 9,588 enumerated provider/model pairs enter the candidate pool with source provenance. Candidate presence, reported working entries, catalog observations, runtime eligibility, provider admission, entitlement, quota and successful inference remain separate states. Candidate seeding grants no execution authority.

Stratify by source, evidence class, provider and observed modality. Preserve failed, unavailable, unsupported, censored and untested candidates. Use task-specific cohorts for chat, reasoning, tools, structured output, embeddings, reranking, image, audio, video, search and other supported modalities. Chat evidence does not establish media/search capability.

## Variants

Incumbent remains the source-preserving baseline over the complete population. VultrInspired is the native loss-aware projection over the same population manifest. The v5 collector remains one observation layer inside that population. Future catalogue variants join as separately versioned competitors against identical source hashes and cohort identity.

## Evidence and promotion

- Population compilation performs zero network requests, credential reads and inference calls.
- Source-scoped provider identity prevents fuzzy alias collisions.
- The 7,341 figure retains its historical date and Actions-only counting rule.
- Tournament trials require task receipts from the existing manager/router/admission/evaluator path.
- Preserve raw outcomes, failures and censoring; report source coverage and per-stratum results.
- Promotion requires fresh holdout evidence, existing safety/correctness gates, independent review and explicit operator approval.
