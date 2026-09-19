# BIFROST-006 — Benchmark smoke runbook

**Status:** runbook ready · results not yet collected  
**Repos:** bifrost-benchmarking_fork + bifrost_fork  
**Goal:** Cost-free, reproducible evidence of gateway overhead vs current chat plane.

## Why

Catalog status is `evaluation`. Promote toward any production path only with measured latency / success / memory — not README claims.

Compare:
1. **Bifrost** (self-hosted) → mocker provider
2. **llm_api_hub** (local :8787) if running
3. Optional: OpenRouter free model (real network; not free of rate limits)

Prefer mocker so provider latency does not dominate.

## Prerequisites

```bash
# Benchmarking fork
git clone --depth 1 https://github.com/timerloggedout-spec/bifrost-benchmarking_fork.git
cd bifrost-benchmarking_fork
go mod tidy
go build -o benchmark ./benchmark.go   # or: go build benchmark.go

# Mocker (separate terminal)
cd mocker && go run main.go -port 8000
```

Bifrost gateway (NPX or Docker) pointed at mocker as OpenAI-compatible upstream:

```bash
npx -y @maximhq/bifrost
# configure provider base URL http://host.docker.internal:8000 or localhost:8000
# UI: http://localhost:8080
```

`.env` in benchmarking root (example):

```env
BIFROST_PORT=8080
# LITELLM_PORT=4000
# PORTKEY_PORT=8787
```

## Smoke commands (start small)

```bash
# 30s @ 100 RPS — Bifrost only
./benchmark -provider bifrost -rate 100 -duration 30 -output results-bifrost-smoke.json

# Concurrent-users mode
./benchmark -provider bifrost -users 50 -duration 30 -output results-bifrost-users.json

# Larger payload fixture
./benchmark -provider bifrost -rate 50 -duration 30 -prompt-file 10kbprompt.txt \
  -output results-bifrost-10k.json
```

## Evidence package (append-only)

After a successful run, store under monorepo (future PR):

```text
docs/proposals/active/bifrost-gateway-integration/evidence/
  YYYY-MM-DD/
    results.json          # or renamed per provider
    NOTES.md              # machine, Go version, Bifrost SHA, mocker flags
    env-redacted.txt      # ports only — no keys
```

`NOTES.md` minimum fields:

- date UTC
- bifrost_fork SHA / image tag
- benchmarking_fork SHA
- host (Codespace / local / Termux — if any)
- rate or users, duration, success_rate, p50/p99, throughput_rps
- comparison target if any (llm_api_hub / none)

## Non-goals

- Do not add paid OpenRouter spend for this smoke
- Do not make GHA depend on live Bifrost binary yet
- Do not change model-router primary away from Gemini without dual-gate + this evidence

## Acceptance for BIFROST-006 close

- [ ] At least one mocker-backed Bifrost run with success_rate ≥ 99% @ modest load
- [ ] results.json + NOTES.md committed under evidence/
- [ ] Short compare paragraph in RECON or ITEMS (Bifrost vs baseline or “baseline N/A”)
- [ ] Dual-gate green on the evidence PR

BIUDL. Agent-Identity: Grok (Administrator)
