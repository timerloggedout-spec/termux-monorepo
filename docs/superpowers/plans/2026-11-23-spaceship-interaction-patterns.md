# Spaceship IDE interaction-pattern reference integration

**Proposal:** `spaceship-interaction-patterns`  
**Work items:** `SPACESHIP-001`, `SPACESHIP-002`, `SPACESHIP-003`  
**Branch:** `docs/spaceship-interaction-reference-20261123-v2`  
**Base:** `master` @ `e73307e7685074f8f33f29e35d6f422fd6989730`

## Outcome

Register the source as a Tier-C design-pattern reference and connect it to the existing prompt/context, evaluation-quality, research-integration, ICM, DoE/MVT, and refTemplates validation lanes.

## Scope

1. Add `refTemplates/13_Third_Party_Refs/spaceship-ide/{README.md,SOURCE.txt}`.
2. Add the cross-lane integration record and category/index/source-map links.
3. Extend refTemplates inventory to validate README + SOURCE metadata under `13_Third_Party_Refs/`.
4. Add focused tests for valid and incomplete Tier-C metadata.
5. Register the proposal and preserve exact source provenance.

## Validation

Run in the repository environment or inspect equivalent Actions evidence:

```bash
python3 scripts/ci/refTemplates_inventory.py --strict
python3 -m pytest tests/test_refTemplates_inventory.py -q
python3 scripts/proposals/validate_registry.py
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
git diff --check
```

## Promotion boundaries

- Keep the source in Tier C; the Tier-A research score and Delphi participant registry remain scoped to `15_Research_Repo_Templates/`.
- Keep the source outside `refTemplates/smods/` until a deliberate customization delta, compatibility evidence, immutable reviewed pin, and passing gates exist.
- Treat DoE/MVT as a future experiment candidate. Experiment state: none admitted or executed.
- Preserve upstream attribution and MIT license metadata; source code and media remain upstream.
