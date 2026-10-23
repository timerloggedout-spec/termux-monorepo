# Delphi collaborative interaction lanes

How other lanes file RFPs into the Delphi gate and consume its awards. Payloads reuse existing schemas only: ForeSight evidence (`foresight/schema.json`), HindSight retain (`docs/ops/sessions/HINDSIGHT.md`), `3l0.moneyball.v1` (`docs/ops/HEX-MONEYBALL-INTEGRATION.md`) and `3l0.quota-weights.v1` (`docs/ops/QUOTA-REGISTRY.md`). No secret values anywhere: names only.

## Lanes

| Lane (Hark project) | Writes | Reads | How |
|---|---|---|---|
| **Delphi gate** (owner) | ledger comments, `delphi:*` labels, ForeSight/HindSight/3L0 records, weights ledger | RFPs, quota readings, feedback | `.github/workflows/delphi-gate.yml` |
| **Planning Queue / Resiliency** | RFP issues (e.g. the ledger backing-store evaluation: one RFP per candidate store) | awards on its RFPs | Issue form `delphi-rfp.yml`, `Filed by: planning-queue` |
| **Deploy Quota & Render Resiliency** | `ops/quota/registry.json` (limits + sources), `quota-readings` artifact from `vercel-quota-probe` | shadow awards for deploy surfaces (to pace them) | push to registry or the probe's `workflow_run` wakes the gate |
| **Termux Monorepo Operations** | `/delphi confirmed` · `/delphi miss` after real shadow runs; `hark:queue` jobs | awards; `delphi:shadow` issues to wire as lanes | `issue_comment`, `hark-enqueue.yml` |
| **Hark GitHub Queue Bridge** | `hark:queue` issues that wake Hark lanes (`project: delphi`) | `hark:queue` | `docs/hark-bridge.md` |
| **AI Agent Access Resilience** | the missing Actions credential for a `delphi:needs-access` award | `delphi:needs-access` issues | adds the secret via its own approved path, then comments or dispatches `delphi-rfp` |

## Labels

| Label | Set by | Meaning |
|---|---|---|
| `delphi:rfp` | filer (template) | In the gate |
| `delphi:converged` | gate | Panel IQR/range inside the bar |
| `delphi:shadow` | gate | Awarded a shadow lane at 5% traffic |
| `delphi:parked` | gate | Parked in ForeSight; `recheck_after` in the ledger |
| `delphi:needs-access` | gate | Shadow award blocked on an Actions credential |
| `delphi:promoted` | gate (flywheel) | Shadow confirmed by real runs |
| `delphi:weights` | gate | The append-only weights ledger issue |
| `hark:queue` | any lane | Wake a Hark lane (bridge contract) |

## Events (repository_dispatch)

| `event_type` | `client_payload` | Sender |
|---|---|---|
| `delphi-rfp` | `{}` (re-scan all open RFPs) | any lane |
| `quota-registry-changed` | `{"registry_sha": "<sha>"}` | Deploy Quota |
| `foresight-radar-hit` | ForeSight record (`resource_id`, `canonical_source`, `horizon`, `evidence_status`) | ForeSight / Scout |
| `hindsight-forecast-miss` | `{"rfp": <issue>, "bank_id": "deepagent::termux-monorepo", "content": "<what happened>"}` | any lane running a shadow |
| `delphi-feedback` | `{"rfp": <issue>, "outcome": "confirmed" \| "miss"}` | Ops |

## Award payload (in every ledger comment)

```json
{"input_hash": "…", "final_votes": [{"role": "cost_auditor", "impact": 4, "importance": 5, "score": 20, "veto": false,
  "reason": "…", "via": "rubric|free-model", "sha256": "…", "signed": "Signed-off-by: Delphi-cost_auditor (OPERATOR) run-… / #N#r1"}],
 "award": {"decision": "shadow|parked", "traffic_share": 0.05, "band": "High", "recheck_after": "…", "blocked_on": "…"},
 "records": {"foresight": {"…": "foresight/schema.json"}, "hindsight": {"bank_id": "deepagent::termux-monorepo", "content": "…"},
             "moneyball": {"contract_version": "3l0.moneyball.v1", "…": "…"}}}
```

Consumers read the newest comment starting with `<!-- delphi-ledger v1 -->`.

Signed-off-by: Hark (OPERATOR) delphi-gate-2026-10-20 / project-bbf883e1

## Emitting events from a workflow (2026-10-21)

`repository_dispatch` needs a PAT. Workflows inside this repo should call the reusable emitter instead. It validates the event name and dispatches `delphi-gate.yml` with `GITHUB_TOKEN`:

```yaml
jobs:
  wake-delphi:
    uses: ./.github/workflows/delphi-signal.yml
    permissions: { actions: write }
    with:
      event: hindsight-forecast-miss   # or quota-registry-changed | foresight-radar-hit | delphi-feedback | delphi-rfp
      rfp: "1423"                      # feedback / forecast miss only
      outcome: ""                      # confirmed | miss for delphi-feedback
```

Consumers who want every award in one place should read the `delphi:board` issue (generated). Per-RFP ledger comments remain the record.

## Shadow outcomes and new-surface alerts (2026-10-21)

`.github/workflows/delphi-signal-bridge.yml` wires two real signals through `delphi-signal.yml`. It runs on events only, with no schedule and no keys:

| Signal | Source | Emits |
|---|---|---|
| New-surface alert | a push to master that changes `data/foresight/resource-registry.jsonl` | `foresight-radar-hit`. The gate re-scans and lists surfaces with no RFP under **Radar** on the `delphi:board` issue, covering quota-registry services and ForeSight records. A new meter of a provider and lane that are already covered is not listed. |
| Shadow confirmed | a workflow mapped in `ops/delphi/shadow-lanes.json` finishes, and its newest 3 success/failure runs on master are all success | `delphi-feedback` `confirmed`, sent once. The flywheel re-weights and adds `delphi:promoted`. |
| Forecast miss | same mapping, when the newest run is failure right after a success | `hindsight-forecast-miss`, sent once per transition. The flywheel re-weights. |

Current mapping: #1424 `github.native_ledger` → `delphi-gate`. Its signed ledger writes are that surface running for real. #1423 `turso.free` is not wired yet because no Turso lane exists, and adding a `TURSO_AUTH_TOKEN` secret needs user approval. Other lanes add a mapping line by PR.

## tribute-outcome: graded reweighting from Tribute System 1 (2026-10-21)

Tribute System 1 routing (`scripts/ci/tribute_system1.py`) attaches `delphi_signal = {surface: "tribute-lane", repo, outcome, weight}` to each decision. Weights run from −1 to +1: merged +1, approved +0.5, changes_requested +0.1, question_to_us 0, claimed_by_other −0.3, needs_human_skill −0.4, closed_already_assigned −0.6, low_effort_placeholder −0.8, hostile_spam_flag −1. Emit it with:

```yaml
  delphi:
    needs: route                     # the job that exposes the signal as an output
    if: needs.route.outputs.delphi_signal != ''
    uses: ./.github/workflows/delphi-signal.yml
    permissions: { actions: write }
    with:
      event: tribute-outcome
      signal: ${{ needs.route.outputs.delphi_signal }}   # one object, or a JSON array of up to 50 (batch per run)
```

Outside Actions, use `repository_dispatch` with `event_type: tribute-outcome` and `client_payload: {"signal": <object or array>}`.

Validation: `surface` must match `^[a-z0-9][a-z0-9._-]{0,63}$`. `repo` must be `owner/name` or empty. `weight` must be a number from −1 to +1. If `weight` is missing, the canonical table above fills it from `outcome`. Extra keys such as `lesson` are dropped. Invalid items are skipped.

The gate does two things with each signal:
1. **Outcome ledger.** The `Delphi outcome ledger` issue (`delphi:outcomes`) gets an append-only JSON comment per run. It holds per-surface `n`, `sum`, `ewma` (α 0.2) and `by_outcome`, plus a per-repo `ewma`, `n` and `last`, capped at the 200 most recent repos. Tribute can read the newest `<!-- delphi-outcomes v1 -->` comment to re-rank upstream repos.
2. **Graded panel reweighting.** This needs a scored RFP for the surface (`tribute-lane` is in `ops/delphi/surfaces.json`). Each role that predicted pass (score ≥ 15) earns `+weight`, and each role that predicted fail earns `−weight`. The EWMA step is `α·|weight|` and Elo moves `16·reward`. A weight of 0 changes nothing. Weights enter the RFP input hash quantized (gpr to 0.1, Elo to 25), so a stream of small signals re-scores the queue only when a weight moves materially. Rate-limit walls defer; they never fail the gate.

### Tribute ingest and dedupe (2026-10-22)

`.github/workflows/delphi-tribute-ingest.yml` sends Tribute outcomes to the gate without a change in the Tribute lane. It runs when a `tribute-system1` scan (schedule/dispatch) finishes, by reading that run's `tribute-s1-decisions` artifact. On `workflow_dispatch` it reads the `tribute-s1/backfill` branch instead. `scripts/delphi/tribute_ingest.py` keeps each row's `delphi_signal`, keys it by the thread URL, and sends up to 200 per run through `delphi-signal.yml`.

- **Dedupe.** The gate hashes `key` (or `subject_url`) plus the outcome. It remembers the last 2000 digests per surface in the outcome ledger, so re-scans and overlapping backfills apply nothing twice. If a thread's outcome changes (for example claimed → merged), that counts as a new signal.
- **Damping.** Graded panel reweighting is applied once per batch per surface with the batch's mean weight. A large backfill therefore moves the panel like one outcome, not N.
- Ledger reads page from the newest comments, so busy RFP and ledger issues no longer read stale state.
- A direct emitter in `tribute-system1.yml` is still welcome; keyed duplicates are harmless.
