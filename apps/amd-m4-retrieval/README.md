# AMD AI League — Match 4: Intelligent Web Information Retrieval (P0 scaffold)

Agent: NL request ⇒ plan ⇒ navigate/fetch ⇒ extract ⇒ answer + source citations.
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
- Planner swap: `AMD_M4_PLANNER=heuristic` (default) | `llm` (P1 stub).

## Contract compliance — claim ↦ evidence

| Contract point (packet ↦ PR #2543, C11 §) | State ↦ evidence |
|---|---|
| FINAL stage = `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`; multi-stage ok, ∅ squash | ✓ `Dockerfile` stage 2 `FROM` = mandated image verbatim; stage 1 (venv) on the same base ⇒ py3.14 match |
| Code at `/app`: `app.py` + `requirements.txt` (+ `/models` optional) | ✓ `COPY app.py /app/app.py`, `COPY requirements.txt /app/requirements.txt`; `/models` ∅ at P0 |
| Public-registry image, pullable ∅ creds, runs as-is | ✓ `CMD python3 /app/app.py --serve`; ∅ build args, ∅ runtime creds |
| Image ≤ 60 GiB (target ≪) | ✓ app delta ≈ 0 (stdlib only); total ≈ mandated base — the base is league-chosen, the app adds no model weights at P0 |
| VRAM 1–48 GiB envelope | ✓ P0 pipeline is CPU-only ⇒ GPU need = 0 GiB at P0; P1 model sizing must stay ≤ 48 GiB (checklist item for P3) |
| Startup/process time limits | ✓ stdlib-only imports ⇒ fast start; fetch timeout 15 s × `MAX_PAGES = 5` bounds a run |
| ∅ secrets in image or repo | ✓ ∅ keys/tokens anywhere; `grep -ri "api_key\|secret\|token" .` ⇒ only this rule text + stub docstring |
| Anti-hardcoding: hidden tests, hardcoded answers = 0 | ✓ answers composed only from fetched pages; unseen-query tests assert structure, not memorized strings ↦ `tests/` |
| Open-source models/frameworks allowed | ✓ P0 = stdlib; P1 model choice is an open-source pick (below) |

Docker validation at P0: static (docker unavailable on the build VM) —
`FROM` lines + stage graph verified by read; first `docker build` runs in P3
(GPU/container phase) ∧ must re-verify this table before submission.

## Tests (offline, ∅ network)

`python3 -m unittest discover -s tests -v` — fixtures = saved HTML
(multi-site library + museum, a catalog table, a next-link pagination chain).
Coverage: extract (blocks/tables/next; script+style excluded) ∘ pagination
following ∘ multi-site citation ∘ unreachable-source honesty ∘ unseen-query
set (wording ∉ fixtures; asserted: ≥1 citation, citations ⊆ fetched pages,
∅ fixture leakage).

## P1 extension (core build, Nov 03–06 per exec plan)

- `LLMPlanner` implementation behind the existing `Planner` interface
  (open-source model, weights in `/models`, chosen for the 48 GiB envelope).
- Standing/fit ranking upgrade: passage scoring ⇒ v2 composite over the
  scored field, replacing P0 term-overlap.
- Fetcher options: JS-rendered pages (headless) ∧ search-API seed discovery —
  behind the same `fetcher` callable; ∅ interface change for the agent.
- Harness adapter once AMD publishes one (∅ published at P0): the service
  surface (`POST /ask`) + CLI JSON are the two stable entry points.
