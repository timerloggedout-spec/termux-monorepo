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

Register all seven active Agent machine surfaces against their unique sibling `*.hum.md` sources in `scripts/linguist/agent_document_pairs.py`. Each lane declares a FLY-006 relationship class and mapping mode; ICM Claude/AGENTS machine aliases are preflighted as groups before writes. All seven current lanes use `identity`. The separate 70% codec remains scoped to its canonical-token registry; the `1337_$934k` mention is historical README/PR #1642 provenance. Retain the root `AGENTS.md` projection as historical rename lineage and route active work through the registered per-Agent pairs. Muse initiated the naming migration per owner-supplied attribution; repository verification pending.

Related evidence: the [FLY-006 human-readable parity audit](https://github.com/timerloggedout-spec/termux-monorepo/blob/74e48656cd817e99c6665bc3822f4052fefd1130/docs/linguist/FLY-006-SIDECAR-OVERLAY-ADAPTATION.md#4-human-readable-parity) directly informs [PR #5889](https://github.com/timerloggedout-spec/termux-monorepo/pull/5889): #5889 records the seven Agent-doc source pairs and byte-preserving projection; the audit’s blob-hash provenance ledger and content-addressed overlay loader remain separate follow-on work.

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
