# Delphi Oracle RFP gate

Admits new free-tier surfaces as **shadow lanes** through a blind agent panel, sourced oracle facts and weighted consensus. Delphi decides *which surfaces deserve a trial*; it **never picks a model for live routing** (that stays with `.github/actions/model-router` and 3L0).

Owner: Hark project "Delphi Oracle RFP Gate". Collaboration contract: [`DELPHI-LANE-CONTRACT.md`](DELPHI-LANE-CONTRACT.md). Weighting: [`DELPHI-WEIGHTING.md`](DELPHI-WEIGHTING.md).

## Pipeline

```
RFP issue [delphi:rfp] ─▶ oracle ─▶ blind panel r1 ─▶ (median, IQR, anon outlier reasons) ─▶ r2 ─▶ r3 ─▶ award
                                                                                                   ├─ shadow lane (5% traffic) ─▶ HindSight retain
                                                                                                   └─ parked ─▶ ForeSight record + recheck_after
real runs ─▶ "/delphi confirmed|miss" or repository_dispatch ─▶ flywheel re-weights roles ─▶ re-prioritized queue
```

| Stage | What happens | Code |
|---|---|---|
| RFP | Issue form `.github/ISSUE_TEMPLATE/delphi-rfp.yml` in Gantt proposal format: lane, free quota with source URL, reset with zone, auth from Actions (secret **name** only), lock-in, failure modes | template |
| Oracle | Attaches the documented limit + source URL (`ops/delphi/surfaces.json`, cross-referenced to `ops/quota/registry.json`), the live 3L0 quota multiplier from the `quota-readings` artifact when one exists, and ForeSight horizon / failure-mode evidence. `limit: null` = no fetched page states a number; nothing is invented | `gate.oracle` |
| Panel | 5 blind roles: OPERATOR, builder, reviewer, Scout, cost_auditor. Each scores DECISION-MATRIX Impact 1-5 × Importance 1-5. MSM-018 keeps every role on transparent rubric scoring only. Provider keys are not passed to the job; model ballots remain disabled until exact no-cost entitlement and fresh quota admission are implemented and independently validated. The cost auditor's **money veto** (needs a card / auto-bills) caps the score at 4 regardless | `gate.rubric_vote`, `gate.llm_vote` |
| Rounds | Rounds 2-3 show each role only the median, the IQR and anonymous outlier reasons. Stop when IQR ≤ 4 or range ≤ 6, or after round 3 | `gate.delphi` |
| Score | `effective_score = Σ(w×score)/Σw`, `w = base × (0.5 + gate_pass_rate) × (elo/1500)` | `gate.effective` |
| Award | ≥ 15 (High/P0) and no veto → **shadow** at 5% traffic, promote after 3 confirmed runs. 9-14.99 → **parked**, recheck 14 days. < 9 or veto → **parked**, recheck 30 days. A shadow award whose Actions credential is verified absent also gets `delphi:needs-access` (Access lane) | `gate.award` |
| Records | Per result: ForeSight evidence record (`foresight/schema.json`), HindSight `retain(bank_id="deepagent::termux-monorepo", …)` payload, and a `3l0.moneyball.v1` row, inside the signed ledger comment and the `delphi-records-<run>` artifact | `gate.records` |
| Signing | Every vote carries `Signed-off-by: Delphi-<role> (OPERATOR) run-<id> / #<rfp>#r<round>` and a sha256 fingerprint ([`OPERATOR-SIGNING.md`](OPERATOR-SIGNING.md)) | `gate.sign` |

## Adaptive cadence (no fixed daily cron)

`.github/workflows/delphi-gate.yml` wakes on events:

| Trigger | Event |
|---|---|
| New or edited RFP, label added | `issues` (only when labeled `delphi:rfp`) |
| Human comment / `/delphi confirmed` · `/delphi miss` | `issue_comment` (bots ignored, so the gate never wakes itself) |
| Quota registry changed | `push` to `ops/quota/registry.json`, or `repository_dispatch: quota-registry-changed` |
| Fresh live quota readings | `workflow_run` of `vercel-quota-probe` (Deploy Quota lane) |
| ForeSight radar hit | `repository_dispatch: foresight-radar-hit` |
| HindSight forecast miss | `repository_dispatch: hindsight-forecast-miss` (`client_payload.rfp`) → flywheel `miss` |
| Real-run outcome | `repository_dispatch: delphi-feedback` (`rfp`, `outcome`) |
| Liveness | `schedule` every 3 days; also re-checks parked RFPs whose `recheck_after` passed |

**Quota-aware scheduler** (`gate.cadence`): reads the 3L0 multipliers (`3l0.quota-weights.v1`, remaining-budget fraction ÷ remaining-time fraction). Mean ≥ 1.2 (free quota going unused before its reset) with RFPs still pending → **accelerate**: chain a `delphi-tick` dispatch, depth ≤ 3. Mean < 0.5 (near caps) → **defer** non-explicit triggers until reset. Otherwise **steady** (events + heartbeat). Each run spends at most a quarter of the registry's `github.api.github_token` budget (1000/h × 0.8 safety ÷ 6 calls per RFP ÷ 4).

**Flywheel**: every confirmed or missed forecast moves each role's `gate_pass_rate` (EWMA α 0.2) and Elo (±16) on the append-only `Delphi panel weights ledger` issue (`delphi:weights`). Changed weights change every RFP's input hash, so the next wake re-scores the queue with the sharper panel. Throughput grows as confidence grows; registry caps bound it.

## Idempotency and storage

- One concurrency group; each run processes all open RFPs and skips any whose input hash (surface facts + role weights + registry entry + live readings) matches its last ledger comment.
- Ledger = signed issue comments + 7-day artifacts. No commits per round, so polling never triggers Vercel/Render builds.

## Run locally

```bash
python3 -m scripts.delphi.gate score                      # all catalog surfaces, offline, JSON
python3 -m scripts.delphi.gate score --surface turso.free
python3 -m pytest -q tests/test_delphi_gate.py
```

Signed-off-by: Hark (OPERATOR) delphi-gate-2026-10-20 / project-bbf883e1

## Quota and attribution reconciliation (MSM-018)

Generated rubric scores (including role-labeled signatures) are not independent human or provider-model ballots. The existing OpenRouter [RFP ledger](https://github.com/timerloggedout-spec/termux-monorepo/issues/1426#issuecomment-6310432412) explicitly records `via: rubric`; its result establishes rubric processing, not OpenRouter inference. A shadow award is advisory and never opens runtime admission. Key presence, `:free` names and neutral unknown-quota multipliers cannot authorize model voting. This slice preserves event/cadence behavior while removing the implicit key-to-inference path; it does not cast or alter historical votes.

## Live shared-token budget and results board (2026-10-21)

- **Live GitHub budget.** Each run reads `GET /rate_limit` first. That read is free, and it covers the repo-wide `GITHUB_TOKEN` budget every workflow shares. The run keeps a reserve of `max(100, cap/10)` calls for the repo's other workflows. If remaining calls are inside the reserve, the mode is `defer_api`: nothing is scored and the next event or heartbeat resumes. Otherwise, RFPs per run are capped at `(remaining − reserve) / 6`. Acceleration chaining is off while the token is below half its budget. This closes the 2026-10-20 incident: run 39552711019 got a 403 after about 2,500 runs/day had drained the shared token.
- **Labels.** One `GET /labels` per run, and only missing labels are created. This replaces the 7 POSTs per run.
- **Results board.** The `Delphi results board` issue (`delphi:board`) is regenerated each run, and only when its contents change. It has one row per open RFP: effective score, award, band and recheck date. Shadow awards come first. It is a read-only view; the ledger of record stays the signed comment on each RFP.
- **Signal emitter.** Sibling workflows wake the gate through the reusable `.github/workflows/delphi-signal.yml` (`workflow_call`, `actions: write`). See the lane contract.
