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
