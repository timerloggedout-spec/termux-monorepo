# AMD AI League — Match 4: Intelligent Web Information Retrieval (P1: core agent)

Agent: NL request ⇒ plan (decompose ⇒ sub-queries) ⇒ navigate/fetch (bounded
multi-hop: pagination chains ∘ ranked evidence links) ⇒ extract (prose ∘
lists ∘ tables→records) ⇒ merged answer + per-source citations.
Brief (card only, packet ↦ PR #2543): "Build an AI agent that can navigate
websites, understand a natural-language request and accurately retrieve the
specific information a user needs." 1,800 pts, LIVE; ∅ harness/rubric
published ⇒ build ↦ league contract + generality.

## Run

- Service (container default): `python3 /app/app.py --serve --port 8080`
  → `GET /health`, `POST /ask {"request": "...", "urls": ["https://..."]}`.
- CLI: `python3 app.py "What are the opening hours?" --url https://example.org/`
  → JSON `{question, answer, citations[], pages_fetched[]}`; every answer
  passage carries its `[n]` citation ↦ `citations[n].url`.
- Planner swap: `AMD_M4_PLANNER=heuristic` (default) | `llm` | `auto`.
  `python3 app.py --model-status` prints the local-model detection verdict.

## Planner — local open-source model only (∅ keys, ∅ external calls)

`LLMPlanner` implements the `Planner` interface against a LOCAL model and
activates ONLY when detection (`local_model_status()`) finds one:

1. **Endpoint** — `AMD_M4_LOCAL_MODEL_URL` naming an OpenAI-compatible server
   on a **loopback** host (llama.cpp / vLLM / Ollama serving a local
   open-source model). Non-loopback URLs are refused before any call.
   Detection probes `GET /v1/models`; planning uses `/v1/chat/completions`.
2. **In-process** — weights under `AMD_M4_MODEL_DIR` (default `/models`:
   `*.gguf` / `*.safetensors` / HF `config.json`) ∧ an importable local
   runtime (`llama_cpp` ∨ `transformers`).

∅ detected model ∨ dead endpoint ∨ unparseable reply ⇒ `HeuristicPlanner`
(deterministic decomposition) — the agent never blocks on a model.
**State on the build VM (2026-10-30): ∅ `/models`, ∅ local runtime ⇒ path
inactive here**; transport + detection + fallback are proven against a fake
local endpoint in `tests/test_amd_m4_p1.py` (`TestLLMPlannerLocalModel`),
and the real-model activation remains a P3 (GPU/container) verification item.

## Contract compliance — claim ↦ evidence

| Contract point (packet ↦ PR #2543, C11 §) | State ↦ evidence |
|---|---|
| FINAL stage = `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`; multi-stage ok, ∅ squash | ✓ unchanged at P1 — `Dockerfile` stage 2 `FROM` = mandated image verbatim |
| Code at `/app`: `app.py` + `requirements.txt` (+ `/models` optional) | ✓ `COPY app.py /app/app.py`, `COPY requirements.txt /app/requirements.txt`; `/models` ∅ (runtime-detected if the league mounts weights) |
| Public-registry image, pullable ∅ creds, runs as-is | ✓ `CMD python3 /app/app.py --serve`; ∅ build args, ∅ runtime creds |
| Image ≤ 60 GiB (target ≪) | ✓ app delta ≈ 0 (stdlib only); total ≈ mandated base; ∅ weights baked in |
| VRAM 1–48 GiB envelope | ✓ pipeline is CPU-only with ∅ model; a mounted local model must size ≤ 48 GiB — P3 checklist item, NOT yet verified |
| Startup/process time limits | ✓ stdlib-only imports ⇒ fast start; fetch timeout 15 s × `MAX_PAGES = 8` ∧ `MAX_HOPS = 2` bound a run (test: hop bound) |
| ∅ secrets in image or repo | ✓ ∅ keys/tokens anywhere; model path reads ∅ credentials ∧ refuses non-loopback endpoints (test: refused, ∅ external call) |
| Anti-hardcoding: hidden tests, hardcoded answers = 0 | ✓ answers composed only from fetched pages; unseen-query suites (P0 ×5 + P1 ×12) assert structure + retrieval-derived fragments, ∅ memorized strings ↦ `tests/` |
| Open-source models/frameworks allowed | ✓ P1 model path = local open-source models only (endpoint ∨ in-process), detection-gated, heuristic fallback |
| Multi-hop generality (P1 scope) | ✓ decomposition + pagination chains + ranked evidence links, bounded; tests cite ≥ 2 sources on compound queries across pages ∧ sites; generic heuristics only, ∅ per-site code |
| Extraction strength (P1 scope) | ✓ prose ∘ ul/ol lists (heading context) ∘ tables ⇒ structured records; tests ↦ `TestExtractPlus` |

Docker validation: **docker build still ∅ on this VM** — static verification
only (`FROM` lines + stage graph by read). ⚠ P3 FIRST-BUILD FLAG stays OPEN:
the first real `docker build` + run-as-is check happens in P3
(GPU/container phase) ∧ must re-verify this table before submission.

## Tests

- Default (offline, ∅ network): `python3 -m unittest discover -s tests -v`
  — 23 tests: P0 suite (unchanged, green) + P1 suite (extract+ ∘ multi-hop ∘
  LLM local-model ∘ 12 unseen queries).
- Live (opt-in, network-marked, SKIPPED by default incl. CI):
  `AMD_M4_LIVE=1 python3 -m unittest tests.test_amd_m4_live -v` — real public
  pages (example.com/.org), structural assertions only. Verified live
  2026-10-30 on the build VM: 2/2 ok when opted in.

## Remaining phases

- P2 (Nov 05–07): standing/fit ranking upgrade — passage scoring ⇒ v2
  composite over the scored field, replacing term-overlap.
- P3 (Nov 07–09): GPU/container phase — FIRST docker build (flag above),
  real local-model activation + VRAM sizing ≤ 48 GiB, harness adapter once
  AMD publishes one (∅ published at P1).
