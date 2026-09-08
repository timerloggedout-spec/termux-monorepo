# Linguist Diaspora Recovery

## Canonical relationship

`PR #154 → dc8c08d → #196 → current master → NSE-019`

The PR #154 review contains the historical `to_1337speak()` behavior: sparse randomized character substitution using a **70% probability threshold**, with the stated requirement that the result remain de-compressible to human-readable form.

`dc8c08d` establishes the later CedrLang v2 baseline: O(N) document compilation with strict protection of casing, Markdown structures, numbers, paths, decimals, and emphasis. #196 records the accepted `AGENTS.hum.md` round-trip milestone.

## ICM projection model

```text
semantic source
   ↓
notation / living lexicon
   ↓
INDEX taxonomy + relationship graph
   ↓
canonical CedrLang IR
   ↓
phase codec (initial p=0.70)
   ↓
AGENTS.md / AGENTS.hum.md / README / ICM projections
```

The phase codec is a disposable projection. It is not the semantic source of truth.

## Drift/recovery signals

- historical behavior missing from current runtime;
- `AGENTS.md` / `AGENTS.hum.md` projection mismatch;
- INDEX taxonomy entries without provenance;
- Caveman/Grimoire behavior present only in historical commits;
- ICM relationship edges that point to superseded implementation paths.

## Required evidence

Every recovered behavior records source commit/PR, affected path, invariant, test, and current disposition. The 70% threshold is provenance-backed for the initial phase but remains experimentally tunable.

## Related surfaces

- `docs/proposals/active/notation-sets/ITEMS.md` — NSE-019
- `docs/proposals/active/notation-sets/LINGUIST-LINEAGE.md`
- `docs/linguist/MASTER-ALIGNMENT.md`
- `.jules/Linguist.md`
- `workspace/compression_sandbox/cedrlang/phase_codec.py`
- `tests/test_cedrlang_phase_codec.py`
