# Hindsight Standing Gaps

Generated: 2026-10-02

## Resolved this session

| # | Gap | Fix |
|---|-----|-----|
| G1 | mvt-seed NameError: vendor not defined | inline provider.get() in f-string |
| G2 | memory_units.context empty; text was real column | COALESCE(text, context) everywhere |
| G3 | bank rename PK conflict | DELETE old banks, no UPDATE |
| G4 | OpenRouter llama-3.3-70b:free dead (404) | probe /api/v1/models, pick qwen/qwen3.8-27b:free |
| G5 | hs-db command not found on Termux | Termux wrapper -> codespace runner |
| G6 | /tmp on Termux vs codespace confusion | doctrine: TMPDIR on Termux |
| G7 | heredoc parsing chokes in app UI | prefer .py file writes |

## Open gaps

| # | Gap | Impact | Next |
|---|-----|--------|------|
| G8 | MVT extraction produces zero-length text | Quality of comparison degraded | After G2 confirmed, re-seed historical docs |
| G9 | No automated reviewer/critic role | MVT only compares producers | Build critic via observatory.jev runtime |
| G10 | No calibration ledger active | Confidence scales not tracked | Wire decision-record.schema.json writer |
| G11 | observatory role labels conflated with classifier products | Naming confusion | Separate decide:: namespace, build classifier runtime |
| G12 | S1/S2 DeepAgent hindsight_retain still a stub | No auto-retain from agent loop | Replace `if False` with real call |
| G13 | cs-seed.py still reads hardcoded bank | Legacy path | Deprecate or align to new naming |
| G14 | offload.sh missing | Large-file path incomplete | Materialize from chat, commit |
| G15 | hs-cadence harvest failing | Batched ingestion stalled | Read hs-lib, fix the _cmd invocation |

## Naming evolution

    old: deepagent::mvt::<provider>::<model>::<role>::<comp>
    old: termux-monorepo::mvt::<provider>::<model>::<role>::<comp>
    new: termux-monorepo::mvt::<vendor>::<family>::<model>::<settings>::<role>::<comp>

Vendor = who bills (google, openrouter)
Family = product line (gemini, qwen, llama)
Model = specific checkpoint
Settings = tier/variant (standard, flex, free, thinking)
