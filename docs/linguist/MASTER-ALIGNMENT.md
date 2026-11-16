# Linguist Master Alignment

## Status

`master` is the integration source of truth for the current recovery line.

The recovery anchor is `dc8c08d` (CedrLang v2 compilation). `master` is 511 commits ahead of that anchor, so this is a reconciliation exercise rather than a branch reset. The goal is to recover behavior that was subsequently diluted, superseded, or displaced while preserving later improvements.

## Provenance chain

- `dc8c08d` — O(N) CedrLang v2 compilation, strict casing, Grimoire mapping, formatting/number/path protection, and tests.
- #196 / `ea2a2f8` — accepted O(N) compiler + `AGENTS.hum.md` round-trip milestone.
- `1103d832` / `0360aa2` / `ea2c073` / `06af26e` — cached mappings, precompiled regex, Caveman six-line routine.
- `51023b87` / `ebfaa35` / `7a6e5a7` — single-pass combined regex and recorded performance learning.
- `4eb9f830` / `267fecc` — fast-path term pre-search.
- PR #154 review `discussion_r3754718523` — sparse randomized `to_1337speak()` experiment with the initial **70% probability threshold**.

## Recovery rule

Do not replay historical commits wholesale. Recover behaviors by provenance, isolate them behind explicit contracts, and test them against the current master implementation.

### Phase 1 — 70% diaspora

`workspace/compression_sandbox/cedrlang/phase_codec.py` restores the historical stochastic surface as an explicit codec phase.

- `p=0.70` is the initial rollout value.
- It is intentionally a rollout control so usage can increase incrementally.
- It mutates only known compressed dictionary tokens.
- It is reversible through variant normalization before canonical decompilation.
- Seeded RNG support provides forensic reproducibility.

### Phase 2 — document projections

Reconcile the codec with the `AGENTS.md` ↔ `AGENTS.hum.md` round-trip and the existing strict Markdown protection rules. The canonical source remains human-readable/semantic; compressed variants are projections.

### Phase 3 — taxonomy/index integration

Connect INDEX Taxonomy, Concept/Pointer/Alias indexes, ICM relationship records, and the living lexicon without creating a monolithic replacement index.

### Phase 4 — Caveman / Grimoire

Recover and benchmark Caveman-Micro/fork and Grimoire behaviors individually. Promote only validated behavior into current runtime contracts.

## Guardrails

- Preserve Markdown, URLs, paths, numbers, code fences, and inline code.
- Require round-trip semantic recovery before increasing diaspora probability.
- Measure token/byte density, latency, ambiguity, repair rate, and task quality separately.
- Keep canonical IR upstream of compression.
- No credential/session artifacts are part of this recovery.
- Execution remains subject to the repository gates and the proposal lifecycle.

## Proposal connection

This plan is tracked by `notation-sets-evolution` NSE-019 and the continuous-evolution NSE-003/NSE-004/NSE-008 model. The lineage map in `LINGUIST-LINEAGE.md` records historical vs governed vs experimental artifacts.
