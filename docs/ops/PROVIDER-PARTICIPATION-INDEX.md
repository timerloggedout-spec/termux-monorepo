# Provider participation index

**Machine output:** `ops/quota/provider-participation-index.json`  
**Generator:** `scripts/provider_participation_index.py`  
**Dashboard mirror:** `apps/tribute-dashboard/data/provider-participation-index.json`

## Purpose

One exhaustive, evidence-backed projection joins model-lane quota registration, per-record dispatch classification, nested-family participation receipts, role contracts, and the existing provider-rotation DoE. It is not a new provider configuration, quota manager, admission controller, or tournament.

## Evidence dimensions

| Dimension | Source | Meaning |
|---|---|---|
| Provider/model registration | `ops/quota/registry.json` | Canonical model-lane record and quota metadata |
| Dispatch class and route | `ops/challenge/desk-feed.json#dispatch.provider_catalog.inference_availability` | Wiring class and named route |
| Observed model and role | `ops/tracking/nested-family.json` | Exact identity and roles only where task records supply them |
| Invocation proof | Nested-family task records | Passed `inference-invoke` receipts and source/run references |
| Declared role capability | `docs/ops/PROVIDER-COLLABORATOR-CAPABILITY-MAP.md` | Capability declaration, not observed participation |
| Tournament assignment | `experiments/doe/util-1-provider-rotation/DESIGN.json` | Existing live rotation campaign; no duplicate tournament |

Provider names are preserved; case-folding is used only for joins. Unknown model labels become schema `null`. GitHub actors and commit authors are not model identities.

## Dispatch classes

`proven`, `wired-unproven`, `triggerable`, and `inference-only` retain the dispatch-map meanings. `catalog-only` means catalog visibility without an admitted inference route and is never dispatchable. `unmapped` means a model-lane registry record lacks a per-record dispatch row.

## Free eligibility and quota safety

`free_eligibility` is schema `null` unless an exact account + model admission receipt exists. Catalog pricing, public free-plan language, configured credentials, API/catalog reachability, and provider-family status do not establish free eligibility or remaining quota. Quota `null` is not zero.

The generator makes no provider calls and changes no routing weights, allowlists, admission, credentials, or spend ceilings.

## Tournament

The index reads the existing `util-1-provider-rotation` campaign and desk rotation rule. Desk assignment remains authoritative. Records retain provider, selection reason, timestamp, exact model/protocol where present, run correlation, outcome, and provider-reported usage. No synthetic observations or independent ballots are created.

## Refresh

The existing `quota-usage-series-refresh` workflow regenerates the index and byte-identical dashboard mirror when source records change.

```sh
python3 -B scripts/provider_participation_index.py --root .
cmp ops/quota/provider-participation-index.json apps/tribute-dashboard/data/provider-participation-index.json
pytest -q tests/test_provider_participation_index.py
```
