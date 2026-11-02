# Telemetry Ingest — HindSight + Provenance (separate)

Status: wired 2026-10-28. Before this, neither system ingested the repo's
telemetry providers: HindSight existed only as the deepcli client scaffold
(`deepcli/_v1_hindsight.py`, env-gated, nothing feeding it), and Provenance
was an attribution layer being initialized (evidence-envelope / foresight
spine), with no ingest over the telemetry surfaces.

## The two sinks are separate

`{|separate|}` is load-bearing: HindSight and Provenance are independent
sinks with independent files, records, and failure modes. Neither is a
copy, mirror, or downstream of the other. The ingest script writes both
from the same source read, in one pass, so their coverage cannot drift —
but a HindSight outage never blocks the Provenance ledger, and vice versa.

| Sink | Output | Shape |
|---|---|---|
| Provenance | `ops/telemetry/provenance-ledger.jsonl` | `telemetry-provenance/v1` envelopes: foresight-spine `resource_id`/`item_id`/`lane_id`, source path + SHA-256, `evidence_hash` over canonical JSON |
| HindSight | `ops/telemetry/hindsight-payloads.jsonl` | `telemetry-hindsight/v1` retain payloads in the repo client contract (`POST /retain`, `{bank_id, content, metadata}`); content = ids/counts/hashes only |
| Receipt | `ops/telemetry/ingest-receipt.json` | per-source emitted/partial/skipped, sink counts, provider coverage, excluded list |

## Sources (all of them)

Manifest: `scripts/telemetry_ingest/sources.json`. A source not in the
manifest is not ingested — add it there, never by hand-editing outputs.

- `ops/quota/registry.json` — every quota service + provider
- `ops/cadence/provider-onboarding.json` — every cadence provider (LLM + review)
- `config/agent_stack_integrations.json` — every agent-stack integration
- `data/g4f-working/providers.json` — every g4f tester-harvest provider
- `docs/ops/generated/reviewer-metrics.json` — reviewer telemetry
- `ops/github-telemetry/config/sources.yaml` — every GitHub telemetry source
- `agent_telemetry_stream.json` — the agent telemetry stream, per provider
- `ops/delphi/ledgers.json`, `ops/challenge/coordinator.json`,
  `ops/moneyball/plane.json` — ops record surfaces
- `apps/help-wanted-dashboard/data/*` — every dashboard feed file (glob)

Coverage rule: the expected provider set is the union of provider names
in the quota registry, cadence onboarding, and the g4f harvest. Every
expected provider must produce one Provenance envelope AND one HindSight
payload, or appear in the receipt's `excluded` list with a reason.
`scripts/telemetry_ingest/ingest.py --check` (and the test suite) fail on
any missing provider.

## Honesty rules

- Excluded ≠ dropped: agent-stack integrations with status `HOLD`/`REJECT`
  (e.g. `copilot-usage-metrics-api` — no Copilot seats on this account,
  NOT APPLICABLE 2026-10-26) are recorded as excluded with the reason, in
  both sinks. They are never counted as ingested.
- Missing/unparseable source = `partial` receipt entry, never zero,
  never success (docs/ops/AUTOMATED-TELEMETRY-AUDIT.md).
- No secrets, prompts, or payload values in either sink: outputs carry
  ids, counts, statuses, and hashes only, and the generator refuses
  secret-shaped content.
- Counts are derived from the source files at run time, never copied
  forward.

## Running

```
python3 scripts/telemetry_ingest/ingest.py --now <ISO8601>            # regenerate outputs
python3 scripts/telemetry_ingest/ingest.py --now <ISO8601> --retain-live
    # + POST every payload to $HINDSIGHT_BASE_URL/retain
    #   (bank $HINDSIGHT_BANK_ID, Bearer $HINDSIGHT_API_KEY; both secret
    #    names are provisioned in the repo Actions store, names-only)
python3 scripts/telemetry_ingest/ingest.py --check                    # committed outputs current?
python3 -m pytest tests/test_telemetry_ingest.py -q
```

Automation: `.github/workflows/telemetry-ingest.yml` (weekly Wed 07:23Z,
push on any source path, dispatch) — runs the tests, regenerates, does
the live HindSight retain as a separate step, and proposes the outputs
as a refresh PR. It never commits directly to master.

## Token/App history x attribution correlation (2026-11-01)

`ops/telemetry/token-attribution-correlation.json` correlates the
fleet's token/App action history with the attribution records over the
599-PR backfill window: the PAT-era GitHub view (every owner-login PR
attributed to the owner) vs the attributed population. Owner-login PRs
redistribute across lane actors by stamp/trailer evidence; the
remainder stays null. App-era actions (per-App `[bot]` logins, own
rate buckets) self-attribute via the app_bot leg. This correlation is
the provenance population delta consumed by the DoE competing-backfill
trigger whenever the attribution method version changes.

## HindSight live retain contract (corrected 2026-11-01)

Live retain uses the deployed server's real contract, verified from
timerloggedout-spec/hindsight source (hindsight_api/api/http.py):
`POST /v1/default/banks/{bank_id}/memories` with
`{"items":[{content, document_id, context, metadata, tags}], "async": true}`
and Bearer auth; document_id = the telemetry/density unit id, so
re-retains upsert (document upsert semantics) and refresh runs are
idempotent. The earlier scaffold shape (POST /retain) is not a server
route and failed 316/316; receipts now record endpoint, batch counts,
and first_error {status, body_excerpt} as exact gate evidence.
