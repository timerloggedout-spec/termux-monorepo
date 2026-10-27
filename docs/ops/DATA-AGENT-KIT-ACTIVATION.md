# Data Agent Kit — Activation Runbook

**Purpose:** turn the already-landed wiring live, in order, with nothing left
to design. **Wiring SSOT:** `docs/ops/DATA-AGENT-KIT-WIRING.md`
· **Policy:** `ops/data_agent_kit/guardrail-policy.yaml` · **Catalog status:**
`mcp-hub/catalog.json` host `google-data-agent-kit`.

## The doctrine (why this runbook is short)

Freemium-prep (owner, 2026-10-26): **wire everything before signup.** The
repo side is complete — catalog, full client config, fleet skill, guardrail
policy — so activation is only the steps that physically require the account
to exist.

## Constraint: the credit card is a BLOCK (owner, 2026-10-26)

The GCP free trial ($300 / 90 days) and every billing-enabled surface require
a card for identity verification. The owner has ruled the card a block, so
**the trial route is closed** and activation takes the no-card routes below.
Recon for any future freemium must surface the card gate in round one and
identify the no-card route before wiring (doctrine update, in the design
doc).

What the block closes: the $300 trial; `dak-gcs` (Cloud Storage requires a
billing-enabled project; Firebase's Spark plan no longer includes Storage —
Blaze-only since 2026-02-03); `dak-kc` (Dataplex/Knowledge Catalog requires
billing); the product trials that presuppose a billing account (AlloyDB,
Spanner).

What stays open — the fleet's primary day-one need:

## Route A (current path): GCP project, no billing → BigQuery sandbox

A Google Cloud project with **no billing account attached** runs BigQuery
in **sandbox mode**: same engine, no card, nothing can be charged.
Verified sandbox terms (Google docs, cross-checked 2026-10-26):

- 1 TiB of query processing per month.
- 10 GiB storage **lifetime** total (not monthly-refreshed; not refunded on
  delete) — fleet telemetry aggregates are megabytes; ample.
- All tables/views/partitions expire after **60 days**. Safe here by
  design: sandbox tables are a *regenerable scratch copy* loaded from repo
  artifacts, never the system of record (the retention red line protects
  the fleet's own stores; nothing of record lives only in the sandbox).
- No streaming inserts, no DML (INSERT/UPDATE/DELETE), no Data Transfer
  Service / scheduled queries. Loads are **batch load jobs**; the fleet's
  read-only posture is unaffected.

### Owner steps (one session)

1. Create the fleet GCP project under the owner Google account **without
   attaching billing** (Cloud Console: create project, skip billing; or
   create it as a Firebase project on the Spark plan — same result, also
   card-free). *Sign-in prompts land on the origin B160V (broken screen) —
   this is the one planned session; 2SV relay applies.*
2. Record the project ID + region in the policy placeholders via a small
   follow-up PR.

### Agent steps (after the project exists)

3. Provision per the policy commands (APIs → `dak-readonly` SA → read
   bindings → MCP deny policy). No billing means no budget alert step —
   nothing can be charged.
4. Create dataset `fleet_telemetry` (dataset-scope `bigquery.dataViewer`
   for `dak-readonly`; note the sandbox's forced 60-day expiration + 10 GiB
   lifetime cap in the dataset description). Batch-load the first telemetry
   snapshot (reviewer metrics + quota observations + provenance receipts)
   from repo artifacts via a load job.
5. Per surface: install the plugin (fleet skill), run `/dak:dak-setup`,
   select the fleet project + region + services.
6. **Disable the plugin telemetry hook** on each surface and verify (policy
   control `plugin-telemetry-hook-disabled`).
7. Smoke evidence as the impersonated read-only identity: one BigQuery
   dry-run + one small SELECT in the sandbox, one Knowledge-Catalog-shaped
   discovery attempt (expected to fail without billing — record the result
   honestly), one GCS listing attempt (same expectation). Record outcomes
   in the PR that flips the catalog status.
8. Flip the catalog `status`: `live_readonly` for the BigQuery sandbox
   scope, with `dak-gcs`/`dak-kc` recorded as pending-billing in the host
   note. Never report a billing-gated server as live.

### Sandbox operating discipline

- Reload/refresh telemetry tables from repo artifacts before the 60-day
  expiry (or let them expire and reload on demand — data is regenerable).
- Watch the 10 GiB lifetime storage cap; prune scratch tables early.
- If the card block ever lifts: attach billing, clear the 60-day expiration
  on the dataset + tables, set the budget alert, set
  `maximum_bytes_billed`, and the same project graduates to the trial /
  Always Free steady state with no re-wiring.

## Route B: trial route — BLOCKED (owner card ruling)

Create project + free-trial billing ($300 / 90 days; no auto-charge at end;
Always Free thereafter covers BigQuery 1 TiB/mo + 10 GiB storage and GCS
5 GiB, graduating `dak-gcs` and `dak-kc` to live). **Not available while
the card block stands.** If it lifts, this route replaces Route A wholesale
— the wiring does not change.

## The general freemium pattern (v2, with the card lesson)

1. Recon the service's real surfaces, guardrail tiers — **and its card
   gate** — from the vendor's own material; name the no-card route
   (sandbox / free plan) before anything is wired.
2. Land the FULL wiring in the repo first: catalog/config, skill, policy,
   provisioning commands, activation runbook.
3. Signup/activate via the best route the constraints allow; credits, when
   usable, fund usage and evaluation, never setup.
4. Activate with evidence; flip the recorded status only on run proof, and
   only for the scope that actually ran.
5. Write the exit before the first credit is spent.
