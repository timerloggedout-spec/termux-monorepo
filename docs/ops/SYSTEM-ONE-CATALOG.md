# System One Catalog — Tier-1 classifier map

The fleet's map of the **System One** ecosystem: typed decision models
that take application state plus caller-defined questions and return
choices, scores, or probabilities (Choice / Score / Noul) instead of
open-ended text. This is the external landscape the Tier 1 classifier
lane operates in; the fleet's own quartet (deepcli `observatory/`:
Mev/Jev/Kev/Laya roles) is the local implementation surface.

- Machine-readable catalog: `config/system_one_catalog.json`
  (schema `system-one-catalog/1`) — 88 entries, each with layer,
  developer, note, source URL, and fleet state.
- Proposal of record: `docs/proposals/active/system-one-classifier-census/`
  (registered PR #1806) — CENSUS.md preserves the source inventory
  (Perplexity research, as of 2026-10-21); ITEMS.md tracks every row.

## Layer discipline

Entries are counted once, in exactly one layer:

| Layer | Count | Meaning |
|---|---|---|
| model | 61 | Trained model families (hosted, open-weight, or both) |
| adapter | 16 | Inference techniques / serving adapters over existing models |
| runtime | 7 | Ports, servers, and studios that run other entries |
| directory | 4 | Indexes and rankings; never counted as models |

## Fleet state vocabulary

`referenced` (in the census only) → `catalogued` (in the JSON catalog)
→ `trial_candidate` (a free or self-hosted route is identified) →
`evaluated` (an observatory trial record exists). Promotion requires
firsthand verification at each step; directory-level evidence never
promotes an entry by itself.

## Namesakes

The observatory role names are ecosystem projects: **Jev** — TypeSafe
AI (hosted, paid; owner-gated); **Kev** — Jared Palmer's open Qwen
family (self-hosted, TypeSafe-compatible); **Laya** — ConvAI
Innovations' encoder family (open weights); **Mev** — two projects
(a Laya fine-tune for recruiting; Mellow AI's Qwen3.5-4B LoRA).
deepcli's classes implement the roles locally; they are not
deployments of these projects.

## Evaluation route

Counterpart evaluation runs through the observatory dispatch
(`docs/ops/CLASSIFIER-TRIAL-DISPATCH.md`): the `deepcli.llm` System One
adapter speaks the TypeSafe-compatible decision API, so any
compatible server (Kev, simple-jev, Ollaya, LocalJev, jev-style, …)
can be evaluated as a producer or judge endpoint. Hosted/paid models
stay out of trials until the owner allows a paid route.

## Infrastructure options (W3)

Runtimes and adapters tracked as options, not model counts: Ollaya
(local server for Laya/Kev/Von/Decider/Nimble), simple-jev (endpoints
from open models, incl. a Laya backend), laya.cpp / Laya-MLX /
Laya-CoreML (Laya ports), sys1 (Rust/Candle server), classifier.dev
(shared Jev/Laya/Kev interface).
