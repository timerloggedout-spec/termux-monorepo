# AMD AI League — Match 4: Intelligent Web Information Retrieval (P2: hardened)

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
| Startup/process time limits | ✓ declared budgets, functionally enforced: `python3 app.py --selfcheck` measures cold start (0.11 s on the build VM vs 5 s budget), exercises the page bound on an endless next-chain (stops at `MAX_PAGES = 8`), the fetch byte cap (`MAX_RESPONSE_BYTES = 2_000_000`) ∧ the 15 s fetch timeout against a loopback probe (P2; tests ↦ `TestSelfcheck` + `TestRobustnessLoopback`) |
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

- Default (offline, ∅ network beyond loopback probes):
  `python3 -m unittest discover -s tests -v` — 42 run / 40 ok / 2 skipped:
  P0 suite (7) + P1 suite (18: extract+ ∘ multi-hop ∘ LLM local-model ∘
  12 unseen queries) + P2 suite (17, below). All P0/P1 tests unchanged
  ∧ green.
- P2 suite (`tests/test_amd_m4_p2.py`): 21 NEW unseen queries (factual ∘
  table ∘ list ∘ multi-hop ×6) + 4 negative/honesty queries (zero-overlap
  ∧ unreachable ⇒ explicit no-answer, never invention) ∘ property checks
  (cited sources ⊆ fetched pages; ∅ content from unfetched fixtures;
  repeat runs byte-identical) ∘ robustness (malformed HTML — extractor
  now auto-closes unterminated blocks/rows/lists instead of dropping
  them ∘ huge pages under the byte cap ∘ redirect chains + loops ∘
  non-HTML bodies ∘ fetch timeouts) ∘ `--selfcheck` budget verification.
- Selfcheck: `python3 app.py --selfcheck` → JSON with the measured
  numbers; exit 0 ⇔ every budget check passes.
- Live (opt-in, network-marked, SKIPPED by default incl. CI):
  `AMD_M4_LIVE=1 python3 -m unittest tests.test_amd_m4_live -v` — real public
  pages (example.com/.org), structural assertions only. Verified live
  2026-10-30 on the build VM: 2/2 ok when opted in; re-verified at P2
  after the extractor robustness change: 2/2 ok.

## Remaining phases

- P2 (Nov 05–07, delivered early): test hardening + robustness +
  `--selfcheck` (this section) ∧ P3 prep = `P3-VALIDATION.md` runbook —
  every step there is NOT-RUN, owner = AMD seat environment.
- P3 (Nov 07–09): GPU/container phase — FIRST docker build (flag above),
  real local-model activation + VRAM sizing ≤ 48 GiB, compliance table
  re-verification claim ↦ evidence, per `P3-VALIDATION.md`; harness
  adapter once AMD publishes one (∅ published at P2).
