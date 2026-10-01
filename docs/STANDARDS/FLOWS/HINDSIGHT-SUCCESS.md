# Hindsight — Verified Success Flows (2026-10-01)

## Flow 1 · Codespace self-host
gh codespace create -R timerloggedout-spec/termux-monorepo \
  -b feat/gh-actions/deepseek-integrates-itself \
  --devcontainer-path .devcontainer/devcontainer.json \
  --default-permissions --machine standardLinux32gb --idle-timeout 30m

Base: devcontainers/base:bookworm + python feature 3.11
Secrets: containerEnv maps every Codespaces-scope name via ${localEnv:NAME}
postCreate: venv + pip install 'hindsight-api-slim[embedded-db]'
postStart:  hindsight-api on 0.0.0.0:8888
Verified:   health=200, worker=hindsight-termux-monorepo

## Flow 2 · Termux → codespace tunnel
ssh -N -L 18888:localhost:8888 \
  cs.<cs>.feat-gh-actions-deepseek-integrates-itself
Verified: /health -> 200 from localhost:18888

## Flow 3 · Retain + recall
POST http://localhost:18888/v1/default/banks/deepagent::termux-monorepo/memories
     {"items":[{"content":"...","metadata":{...}}]}
POST http://localhost:18888/v1/default/banks/deepagent::termux-monorepo/memories/recall
     {"query":"...","top_k":N}
Verified: 200 items_count=1, recall hits>=1

## Flow 4 · Hindsight env that works (0.10.2 slim + Gemini)
HINDSIGHT_API_WORKER_ID=hindsight-termux-monorepo
HINDSIGHT_API_LLM_PROVIDER=gemini
HINDSIGHT_API_LLM_MODEL=<live-200-model>
HINDSIGHT_API_LLM_GEMINI_SERVICE_TIER=flex
HINDSIGHT_API_LLM_PROMPT_CACHE_ENABLED=false
HINDSIGHT_API_LLM_CACHE_AFFINITY=none
HINDSIGHT_API_EMBEDDINGS_PROVIDER=google
HINDSIGHT_API_EMBEDDINGS_MODEL=gemini-embedding-001
HINDSIGHT_API_EMBEDDINGS_GEMINI_OUTPUT_DIMENSIONALITY=768
HINDSIGHT_API_RERANKER_PROVIDER=rrf
HINDSIGHT_API_RERANKER_REQUIRED=false
HINDSIGHT_API_FILE_PARSER=markitdown
HINDSIGHT_API_PORT=8888
HINDSIGHT_API_HOST=0.0.0.0

## Flow 5 · Live quota-aware model pick (hs-rotator v2)
1. GET /v1beta/models?pageSize=200 -> text-generate list
2. recall("gemini model verdict quota") -> rank by past success
3. For each: 1-token generateContent -> 200/429/404
4. retain("gemini verdict ok=.. code=.. model=.. task=retain_extract")
5. First 200 -> restart Hindsight -> persist ~/.llm-active.json

## Flow 6 · Codespaces secret propagation
- Actions-scope secrets: encrypted, unreadable by API
- Workflow run has ${{ secrets.NAME }} access
- One-shot workflow writes to Codespaces scope:
    printf '%s' "$V" | gh secret set NAME --app codespaces -R <repo>
- Codespaces scope read at container create
- devcontainer.json must map each name via containerEnv:

  "containerEnv": { "NAME": "${localEnv:NAME}" }

## Flow 7 · Lifecycle scripts
hs-up          start codespace + relaunch + tunnel + verify
hs-down        stop tunnel + codespace
hs-status      state, tunnel, health, bank facts, quota, ledgers
hs-cadence     batched harvest/multi/exports runner
hs-watch       one SSH per tick monitor
hs-quota-watch cloud probe + auto export on 402
hs-quota-state JSON + Prometheus telemetry
hs-parity2     bidirectional export/import/sync any env -> any env
hs-llm-launch  manual provider/model switch with logging
hs-rotator     Hindsight-driven quota-aware rotation

## Failed attempts (do not retry)
LLM_PROVIDER=google            -> use gemini
SERVICE_TIER=on_demand         -> only valid is flex
PROMPT_CACHE_ENABLED unset     -> free tier cache quota=0
CACHE_AFFINITY=false           -> use none
EMBEDDINGS_PROVIDER=gemini     -> use google
RERANKER_PROVIDER=none         -> use rrf
gemini-2.0-flash               -> RETIRED
gemini-3.8-flash on 0.10.2     -> needs Interactions API
docker inside codespace        -> unshare blocked by seccomp
watch 'gh codespace ssh'       -> spawns sessions, queues forever
import octet-stream            -> use multipart -F file=@z

## Mev/Jev/Kev/Laya status
Executors now live in deepcli/observatory/ (this commit).
Roles are contracts, not slots. Selection is dynamic from leaderboard.
