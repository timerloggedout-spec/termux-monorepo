# P3 VALIDATION RUNBOOK — AMD M4 (GPU / container phase, Nov 07–09)

Status of this document: **PREP ONLY.** Every step below is **NOT-RUN**.
Owner of every step: **the AMD seat environment** (notebooks.amd.com GPU
sessions + a docker-capable host) — this build VM has ∅ docker ∧ ∅ GPU ∧
∅ `/models`, so ∅ step can be executed or claimed from here. Execution
fills the Evidence column; a step counts only with its evidence attached.

Contract of record ↦ PR #2543 ⇒ `docs/ops/CHALLENGE-ENTRIES-LOG.md` §C11.
Code state to validate: `apps/amd-m4-retrieval/` on monorepo `master`
(P0 #2615 ∘ P1 #2619 ∘ P2 tests/selfcheck — record the exact master SHA
used in Step 0 ∧ validate THAT state, never a stale checkout).

Legend: `[ ] NOT-RUN` → `[x] RUN — evidence: <link/log>` per step.

---

## Step 0 — Preconditions ∧ state pin

- [ ] NOT-RUN — owner: AMD seat environment
- Checkout `timerloggedout-spec/termux-monorepo` @ master; record
  `git rev-parse HEAD` ⇒ ______ (all later evidence binds to this SHA).
- Confirm `apps/amd-m4-retrieval/{Dockerfile,app.py,requirements.txt}`
  present ∧ offline suite green on the host before any GPU time is spent:
  `python3 -m unittest discover -s apps/amd-m4-retrieval/tests`
  (expected at prep time: 42 run / 40 ok / 2 skipped-live).

## Step 1 — FIRST docker build (the carried P0/P1 flag)

- [ ] NOT-RUN — owner: AMD seat environment
- Exact command (build context = the app dir; multi-stage, ∅ squash):

```bash
cd apps/amd-m4-retrieval
docker build --no-cache -t amd-m4-retrieval:p3 .
docker history amd-m4-retrieval:p3        # stage graph sanity
docker inspect amd-m4-retrieval:p3 \
  --format '{{ .Config.Cmd }} {{ .Config.WorkingDir }}'
```

- Evidence required: full build log (all stages), final stage `FROM`
  line = `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`
  verbatim, `Cmd` = the `--serve` entry, WorkingDir `/app`.
- Failure handling: a build failure here is a CONTRACT defect, not an
  environment note — stop, file the log, route the fix to the desk
  before any later step runs.

## Step 2 — Image size ≤ 60 GiB

- [ ] NOT-RUN — owner: AMD seat environment

```bash
docker images amd-m4-retrieval:p3 --format '{{ .Size }}'
docker inspect amd-m4-retrieval:p3 --format '{{ .Size }}'   # bytes
```

- Pass ⇔ size ≤ 60 GiB (prep expectation: ≈ mandated ROCm base + ≈ 0 app
  delta — stdlib only, ∅ weights baked in; the measured number governs,
  never the expectation).

## Step 3 — Run-as-is smoke, ∅ credentials

- [ ] NOT-RUN — owner: AMD seat environment

```bash
docker run -d --name m4smoke -p 8080:8080 \
  --env-file /dev/null amd-m4-retrieval:p3        # ∅ creds, ∅ env secrets
curl -s localhost:8080/health                     # {"ok": true, ...}
curl -s -X POST localhost:8080/ask -H 'Content-Type: application/json' \
  -d '{"request": "What is this domain intended for?",
       "urls": ["https://example.com/"]}'
docker exec m4smoke python3 /app/app.py --selfcheck
docker exec m4smoke python3 /app/app.py --model-status
```

- Pass ⇔ health ok ∧ /ask returns a cited answer composed from the
  fetched page ∧ `--selfcheck` prints `"ok": true` with its measured
  numbers (startup_s / chain bound / byte cap / timeout) ∧
  `--model-status` honestly reports unavailable (no model mounted yet).

## Step 4 — `/models` placement ∧ LLMPlanner activation ∧ VRAM sizing

- [ ] NOT-RUN — owner: AMD seat environment
- Place ONE open-source model (weights only, ∅ keys) where the contract
  expects it; two supported placements (detection order in
  `local_model_status()`):
  1. weights under `/models` (e.g. `*.gguf` for llama.cpp or an HF dir
     with `config.json`/`*.safetensors` for transformers) — start from a
     7–8B-class model; a larger quantized model is admissible only while
     Step 4c stays ≤ 48 GiB;
  2. ∨ a loopback OpenAI-compatible server (llama.cpp / vLLM / Ollama)
     with `AMD_M4_LOCAL_MODEL_URL=http://127.0.0.1:<port>` — non-loopback
     URLs are refused by design ∧ must stay refused (re-test that here:
     set a non-loopback URL ⇒ status detail must say "refused").
- [ ] 4a detection: `python3 /app/app.py --model-status` ⇒
  `available: true`, kind `inprocess` ∨ `endpoint`, detail naming the
  weights path ∨ endpoint.
- [ ] 4b activation: `AMD_M4_PLANNER=auto python3 /app/app.py
  "What are the opening hours?" --url https://example.com/` ⇒ answer
  still fully cited (the model plans; retrieval still grounds) ∧
  `AMD_M4_PLANNER=heuristic` run of the same query still works
  (fallback intact).
- [ ] 4c VRAM: during 4b, watch `rocm-smi --showmeminfo vram` (AMD) —
  peak VRAM must satisfy 1 GiB ≤ peak ≤ 48 GiB; record the peak number.
  Over ⇒ smaller model / tighter quantization, repeat 4a–4c.

## Step 5 — notebooks.amd.com session plan (3 h/day budget, batched)

- [ ] NOT-RUN — owner: AMD seat environment
- One session = 180 min; batches are ordered so the longest pole
  (build) starts first ∧ every batch leaves evidence before the next:

| Batch | Min | Contents | Evidence out |
|---|---|---|---|
| B0 prep | 15 | Step 0 pin + offline suite on the notebook host | head SHA + suite counts |
| B1 build | 45 | Step 1 build (+1 rebuild buffer) + Step 2 size | build log + size number |
| B2 smoke | 20 | Step 3 run-as-is + `--selfcheck` in container | smoke transcript |
| B3 model | 50 | Step 4a–4c: place weights, activate, VRAM sweep | model-status JSON + rocm-smi peak |
| B4 suites | 35 | full offline suite in container + opt-in live suite (`AMD_M4_LIVE=1`) + 3 unseen spot queries by hand | suite counts + transcripts |
| B5 record | 15 | Step 6 table fill + log upload to the PR | completed table |
| **Total** | **180** | — | — |

- If B1 fails: spend the session on the fix loop (B3/B4 slip a day —
  Nov 08/09 remain), never on skipping ahead.
- Queries for B3/B4 spot checks must be UNSEEN (not from `tests/`):
  write them in the session log before running them.

## Step 6 — Compliance table re-verification (claim ↦ evidence)

- [ ] NOT-RUN — owner: AMD seat environment
- Re-verify EVERY row of the README compliance table against P3 evidence
  (the P0–P2 static/test evidence does NOT carry over silently):

| Contract point | P3 evidence required | Result |
|---|---|---|
| FINAL stage = mandated ROCm image, ∅ squash | Step 1 build log `FROM` line | ☐ |
| `/app/app.py` + `/app/requirements.txt` layout | Step 1 inspect output | ☐ |
| Public-registry pullable, runs as-is, ∅ creds | Step 3 smoke with `--env-file /dev/null` | ☐ |
| Image ≤ 60 GiB | Step 2 measured bytes | ☐ |
| VRAM 1–48 GiB with a real model | Step 4c rocm-smi peak | ☐ |
| Startup/process limits | Step 3 `--selfcheck` JSON numbers | ☐ |
| ∅ secrets in image or repo | image env/history scan in B5 (`docker history` + env dump ⇒ ∅ credential material) | ☐ |
| ∅ hardcoded answers | B4 unseen spot queries answered from retrieval | ☐ |
| Local open-source model path real | Step 4a/4b transcripts | ☐ |

## Step 7 — Submission-readiness gate (desk + AMD seat, after Step 6)

- [ ] NOT-RUN — owner: AMD seat environment
- All Step 6 rows ☐→☑ with evidence ∧ image published to a public
  registry (pull test from a clean, credential-free context) ∧ artifact
  built from the Step 0 master SHA ⇒ desk routes the submission package;
  submit target Nov 09, hard deadline Dec 01 11:00 PT (↦ packet #2543).
