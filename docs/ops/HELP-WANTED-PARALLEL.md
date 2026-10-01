# Help-Wanted Parallel Capacity (SSOT)

**Status:** adaptive cadence live (scout 2h / execute 4h budgeted).
**Companion:** `HELP-WANTED-LANE.md` · `AGENT-MONIKERS.md` · skill `help-wanted-lane`.

## Delivery hierarchy — DO NOT FLATTEN

| Priority | Mode | What |
|----------|------|------|
| **PRIMARY** | **upstream-pr** | Claim → branch → **PR into the author's repo** |
| **FALLBACK** | **fork-offer** | Only if upstream PR blocked / not allowed / failed |
| **PARALLEL NOTICE** | issue comment + commit URL | Optional **alongside** primary (or with fallback) |

## Adaptive cadence (workbench benchmarks)

| Workflow | Cadence | Notes |
|----------|---------|--------|
| Scout | **every 2 hours** (`17 */2 * * *`) | Was 6h; raise until rate-limit pain, then back off |
| Execute | **every 4 hours** + dispatch | Budget gate; no spray when `remaining=0` |
| Daily upstream budget | **3 / UTC day** (input `daily_budget`) | Tunable; ledger records used/success/fail |

**Finding the working limit:** increase cadence and budget until secondary rate limits or abuse signals appear; artifact benches (`help-wanted-scout-bench.json`, `help-wanted-daily-budget.json`) feed process tuning. Prefer production of **merged upstream value** over raw comment volume.

### Parallel notice (implementation sketch)

After a successful **upstream-pr** (or on fallback only):

1. Resolve commit SHA on our fork branch.
2. Post issue comment: claim context + `https://github.com/<fork>/commit/<sha>` (+ PR URL if primary succeeded).
3. Never use notice as a substitute for primary when primary works.

### Upstream PR best practices (lane defaults)

- One issue → one focused PR; link `Fixes #n`.
- Claim comment before code.
- Minimal diff; match project style.
- No force-push to upstream default; no secrets in bodies.
- Cap concurrent upstream PRs (token pool 2–3).

### Identity trajectory (UI proposals)

| Path | Status |
|------|--------|
| OPERATOR PAT in Actions | **Live** (proven zero#81) |
| GitHub App installation tokens (OIDC / ephemeral ~1h) | Next — least standing privilege |
| Fine-grained PAT roster slots | Expand parallel write pool |

## Rosters

| Slot | Moniker | Surface |
|------|---------|--------|
| 0 | `archW1z` | OPERATOR / Grok |
| 1 | `l337S33k` | Full-scope PAT (intended) |
| 2 | `opsSweep` | GHA + OPERATOR_GITHUB_TOKEN |
| 3 | `heyVern` | `@jules` |
| 4 | `sparkFlux` | `@gemini-cli` |
| 5–7 | `deepCore` / `codeHound` / `peerGate` | review / contract |

Token order: `OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `ARCHWIZ_GITHUB_TOKEN` → `GITHUB_TOKEN`.

## Limits

| Knob | Default |
|------|--------|
| Scout max | 40 |
| Concurrent execute | 1 group (budget serializes day) |
| Upstream PRs / day | 3 |
| Safe parallel write tokens | 2–3 |

## BIUDL

Agent-Identity: Grok (Administrator) · `archW1z`
