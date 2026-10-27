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

## Status & crossover record

Live operational status (with run/ledger evidence), the crossover record,
and the current entry angle live in
`docs/ops/DELPHI-STATUS-AND-CROSSOVER.md` (verified 2026-10-27).

## Generation (Oracle Method) — owner correction 2026-10-27

Proposals are **generated by the Oracle Method system**; the gate and
the weighting machinery above are the evaluation layer over generated
output, not the product. Any lane may file a *brief* — a structured
request naming the surface (competition | RFP | provider-extension |
research), its deadline, and the artifacts to draw on. The Oracle
Method fetches evidence (`fetch_evidence` sets: provenance- and
freshness-stamped), renders the proposal into `docs/proposals/active/`
in the registry format with `author: oracle-method` and a
`PROVENANCE.json` generation receipt, and registers it in
`docs/proposals/registry.yaml`. Points the evidence cannot carry render
UNVERIFIED — never asserted, never silently dropped. Generated
proposals then enter this contract's normal evaluation flow unchanged:
same RFP issues, same gate, same ledgers.
Generator: `scripts/delphi/generate_proposal.py`; in-Actions path:
`.github/workflows/delphi-generate.yml` (dispatch-only, artifact out,
never commits).

**Passes and the cross-vote (owner parameter, 2026-10-27).** A pass
generates **n** candidate proposals — `generation.proposals_per_pass`
in `ops/delphi/panel.json` (default 3); a brief carries that many
`variants`. The candidates are then **cross-voted**: comparative
ballots scoring every candidate in the set (1–25, DECISION-MATRIX
scale), tallied **per source class and never merged** —
`HUMAN_COLLABORATOR`, `MODEL_PROVIDER`, `LOCAL_BASELINE`
(`DRIVER_SYNTHESIS` is not a ballot; a class with no ballots is
reported as zero). The deterministic rubric comparator casts the
LOCAL_BASELINE ballots, one per panel role; aggregation uses the
panel weighting (ledger weights from #1489, panel formula) — the same
weighting the gate already runs on. The ranked outcome is recorded as
a full receipt (`BALLOT.json` in the pass record) and appended to the
outcome ledger (#1487) as a `delphi-generation-ballot v1` JSON
comment. Tooling: `scripts/delphi/cross_vote.py`; the generate
workflow runs both halves when dispatched in pass mode.

## The Oracle Method cycle (owner spec, 2026-10-27)

A pass is a cycle, not a single vote:

1. **Generate** — the pass emits n proposals.
2. **Cross-vote, round 1** — comparative ballots across the set, and
   each candidate's **input vote expectations** are recorded (expected
   rank + expected weighted score per source class) — priors on record
   *before* any implementation exists.
3. **Implementation parallel-comparisons round** — the candidates are
   implemented in parallel; tests run per individual proposal.
4. **Evidence equalization** — round 2 opens on NEW evidence, and the
   evidence base is **identical for every voter**: the per-proposal
   test results bundle. Its sha256 is stamped on the round-2 receipt,
   and every round-2 ballot must carry that hash — a ballot on
   different evidence is rejected (stage gate).
5. **Re-vote, round 2** — ballots on the common evidence.
6. **Calibration** — round 2 vs the recorded expectations: rank/score
   deltas per candidate, with the evidence that moved them. The
   calibration record is the feed for the weighting / elo ledgers.

Parameters are per-context config (`ops/delphi/panel.json` →
`generation.cycle`: n, rounds, expectation format + tolerance,
convergence) — not hardcoded. Stage gates validate each stage:
generation contract, ballot contract, evidence-set equality before
round 2, calibration record. **A stage that cannot execute yet (e.g.
model ballots while `DELPHI_LLM_MAX=0`, or an implementation round
with no results supplied) is recorded `specified_not_run` in the
cycle record — never silently dropped, never fabricated.**
Tooling: `scripts/delphi/method_cycle.py` (writes CYCLE.json +
BALLOT-round1 / EXPECTATIONS / IMPLEMENTATION / ROUND2-EVIDENCE /
BALLOT-round2 / CALIBRATION records); the generate workflow runs the
cycle in pass mode. The D4 Kiroween first live run follows this cycle.
