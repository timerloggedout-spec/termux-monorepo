# g4f-working provisioning (2026-10-28)

Source: https://github.com/timerloggedout-spec/g4f-working_fork @ `49599e769ff12ba1ac57ad96bd5e6deefc927d2b` (2026-10-27T12:51:20Z) — owner's fork of the g4f-working list of working no-auth AI providers/models from xtekky/gpt4free.

## Harvested programmatically (no manual transcription)

`scripts/g4f_working_harvest.py` fetches the source lists and regenerates `data/g4f-working/providers.json` (schema `g4f-working-catalog-v1`):

| Source list | Harvest |
|---|---|
| `provider/providers_models.json` (+ `.txt`, `models_for_testing.txt`) | 60 providers, 4242 catalogued models |
| `working/working_results.txt` | 100 tester-working entries across 15 providers |
| `working/test_results.json` | tester summary: 4829 tested, 100 working, 4729 non-working |

Refresh: `python3 scripts/g4f_working_harvest.py --ref <sha> --source-sha <sha>`

## Boundary

Discovery/reference only, mirroring the existing `gpt4free` resource and the `g4f.vendors` quota record (`ops/quota/registry.json`, unmetered/unknown, fallback pool only, experiment label required). Every catalog entry carries `runtime_eligible: false` / `REFERENCE_ONLY`. A harvested entry is not a verified entitlement and never authorizes fetching, execution, or inference; no cookie/HAR harvesting; per-provider GPL/terms review required before any runtime use. No quota limits are invented for these providers — limits stay unknown/unmetered under `g4f.vendors`.

Registered as resource `g4f-working-fork` in `data/model-selection-market/resource-registry.json` (27 resources).
