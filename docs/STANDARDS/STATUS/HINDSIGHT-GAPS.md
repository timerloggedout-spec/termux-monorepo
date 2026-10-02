# Hindsight Standing Gaps

Generated: 2026-10-02

## Resolved this session

| # | Gap | Fix |
|---|-----|-----|
| G1 | mvt-seed NameError: vendor not defined | inline provider.get() in f-string |
| G2 | CLOSED — memory_units.text, context is wrapper | COALESCE applied |
| G3 | bank rename PK conflict | DELETE old banks, no UPDATE |
| G4 | CLOSED — qwen/qwen3.8-27b:free live, 4 calls, 22141 in / 435 out | — |
| G5 | hs-db command not found on Termux | Termux wrapper -> codespace runner |
| G6 | /tmp on Termux vs codespace confusion | doctrine: TMPDIR on Termux |
| G7 | heredoc parsing chokes in app UI | prefer .py file writes |

## Open gaps

| # | Gap | Impact | Next |
|---|-----|--------|------|
| G8 | CLOSED — real column is text, COALESCE text/context in all readers | — | len=161 avg |
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


## Session close-out 2026-10-02

Verified working:
- primary bank: termux-monorepo::primary (47 facts)
- MVT lane 1: termux-monorepo::mvt::google::gemini::base (56 facts)
- MVT lane 2: termux-monorepo::mvt::google::gemini::gemini-3.5-flash-lite::standard::producer::base (6 facts)
- OpenRouter active: qwen/qwen3.8-27b:free (4 calls, real tokens)
- Divergence query renders
- agent_hindsight module shipped + finish handler wired

Open next:
- G9 critic role runtime
- G10 calibration ledger writer
- G11 classifier namespace
- G12 DeepAgent end-to-end test (retain on finish)
- G14 offload.sh materialization
- G15 hs-cadence fix
