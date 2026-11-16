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

## Preferred host: Codespace (agent lane)

Codespace agent lane is **live on master** (`docs/ops/CODESPACE-AGENT-LANE.md`, #530).

### Open (human / Operator — one click)

1. https://github.com/timerloggedout-spec/termux-monorepo → **Code** → **Codespaces** → **Create codespace on `master`**
2. Machine: default (4 CPU / 8 GB) is enough for mocker + Bifrost + Go benchmark
3. Wait for `postCreateCommand` (setup.sh + shallow submodules)
4. Confirm:
   ```bash
   echo "$ARCHWIZ_ENV"   # codespace
   go version || true
   node -v || true
   ```

No prebuilds required for this smoke (#500 prebuild cost decision remains separate Operator call).

### Inside Codespace — full smoke sequence

```bash
# 1) Benchmarking fork
git clone --depth 1 https://github.com/timerloggedout-spec/bifrost-benchmarking_fork.git
cd bifrost-benchmarking_fork
go mod tidy
go build -o benchmark ./benchmark.go || go build -o benchmark benchmark.go

# 2) Mocker (terminal A)
cd mocker && go run main.go -port 8000

# 3) Bifrost (terminal B) — point at mocker
npx -y @maximhq/bifrost
# UI http://localhost:8080 — set OpenAI-compatible base to http://localhost:8000

# 4) Smoke (terminal C, from benchmarking root)
./benchmark -provider bifrost -rate 100 -duration 30 -output results-bifrost-smoke.json
./benchmark -provider bifrost -users 50 -duration 30 -output results-bifrost-users.json
```

Copy results into monorepo evidence path (new branch → PR):

```text
docs/proposals/active/bifrost-gateway-integration/evidence/YYYY-MM-DD/
  results-bifrost-smoke.json
  NOTES.md
  env-redacted.txt
```

## Prerequisites (any host)

```bash
git clone --depth 1 https://github.com/timerloggedout-spec/bifrost-benchmarking_fork.git
cd bifrost-benchmarking_fork
go mod tidy
go build -o benchmark ./benchmark.go

# Mocker
cd mocker && go run main.go -port 8000
```

Bifrost:

```bash
npx -y @maximhq/bifrost
# provider base URL → localhost:8000
```

`.env` example:

```env
BIFROST_PORT=8080
```

## Smoke commands (start small)

```bash
./benchmark -provider bifrost -rate 100 -duration 30 -output results-bifrost-smoke.json
./benchmark -provider bifrost -users 50 -duration 30 -output results-bifrost-users.json
./benchmark -provider bifrost -rate 50 -duration 30 -prompt-file 10kbprompt.txt \
  -output results-bifrost-10k.json
```

## Evidence package (append-only)

```text
docs/proposals/active/bifrost-gateway-integration/evidence/
  YYYY-MM-DD/
    results.json
    NOTES.md              # machine, Go version, Bifrost SHA, host=codespace|local|termux
    env-redacted.txt
```

`NOTES.md` minimum: date UTC, bifrost_fork SHA, benchmarking_fork SHA, host, rate/users, duration, success_rate, p50/p99, throughput_rps.

## Non-goals

- No paid OpenRouter spend for this smoke
- No GHA hard-dep on live Bifrost binary yet
- No model-router primary change without dual-gate + this evidence
- No Codespaces prebuild enablement in this PR (#500 still Operator decision)

## Acceptance for BIFROST-006 close

- [ ] At least one mocker-backed Bifrost run with success_rate ≥ 99% @ modest load
- [ ] results.json + NOTES.md under evidence/
- [ ] Short compare paragraph in RECON or ITEMS
- [ ] Dual-gate green on the evidence PR

BIUDL. Agent-Identity: Grok (Administrator)
