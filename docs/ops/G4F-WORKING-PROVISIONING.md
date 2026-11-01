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

Discovery/reference only, mirroring the existing `gpt4free` resource and the `g4f.vendors` quota record (`ops/quota/registry.json`, unmetered/unknown, fallback pool only, experiment label required). Every catalog entry carries `runtime_eligible: false` / `REFERENCE_ONLY`. A harvested entry is not a verified entitlement and never authorizes fetching, execution, or inference; no cookie/HAR harvesting; per-provider GPL/terms review required before any runtime use. Quota resolution landed 2026-10-28 (Quota Specialist lane): per-provider records `g4f.*` in `ops/quota/registry.json` for all 60 — 17 ESTABLISHED from primary vendor sources (documented limit + source + quote on the record), 43 NOT ESTABLISHED (no numeric limit published for the g4f surface; limit stays null and the record carries a usage-log inference from this harvest's tester data — working-model counts — labeled as inference, not an entitlement). `g4f.vendors` remains the aggregate for the unresolved set. Full count + provider reconcile: `docs/ops/QUOTA-RECONCILE-2026-10-28.md`.

Registered as resource `g4f-working-fork` in `data/model-selection-market/resource-registry.json` (27 resources).

## Inference endpoints — universe + verified working set (2026-11-01)

Correction to the headline count: **4242 = raw sum of `model_count`** — distinct (provider, model) pairs in the fork catalog = **4241** (the tester's "4829 tested" = 100 working + 4729 raw non-working entries incl. duplicates, 4146 distinct). The fork is a frozen subset: enumerating the installed g4f library (v8.8.16, 160 provider classes; models via `get_models()`/`models`/`model_aliases`) and unioning gives the true universe in `data/g4f-working/universe.json` (schema `g4f-endpoint-universe/v1`): **9588 pairs** (both 3085 · fork-only 1156 · upstream-only 5347).

Full-universe live probe (sandbox, g4f Client, one synthetic completion per pair, proxy-mediated): **160 / 9588 inference_ok** — Perplexity 43/49 · AnyProvider 46/1050 · Gemini 18/21 · PollinationsImage 17/33 · KiloCode 12/403 · G4FSpace 7 · CohereForAI_C4AI_Command 6 · HuggingSpace 6 · BlackForestLabs_Flux1Dev 2 · AgentTools 1 · Pollinations 1 · Yqcloud 1. Verified set = `data/g4f-working/working-endpoints.json` (schema `g4f-working-endpoints/v1`). Sandbox failure classes (curl_cffi proxy bypass, missing Chromium, Cloudflare verification) are environmental — endpoints scoring 0 here are NOT proven dead in Actions.

Execution path: `scripts/ops/g4f_free_smoke.py` + dispatch-only workflow `g4f-inference-smoke.yml` (sources: `working` = re-verify the 160 · `catalog` = fork tester 100 · `universe` = full 9588; sanitized receipt artifact, no response bodies, no credentials, no retries/paid fallback). This is separate from the scheduled availability probe, which stays catalog-only by invariant. Production admission unchanged (`production_admission_changed: false`); verified endpoints feed the compounding pool as wired g4f-route candidates under the FREE-QUOTA-WINDOWS experiment-label rule.
