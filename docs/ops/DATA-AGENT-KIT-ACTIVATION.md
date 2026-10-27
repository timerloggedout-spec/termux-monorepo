# Data Agent Kit — Activation Runbook

**Purpose:** turn the already-landed wiring live on signup day, in order,
with nothing left to design. **Wiring SSOT:** `docs/ops/DATA-AGENT-KIT-WIRING.md`
· **Policy:** `ops/data_agent_kit/guardrail-policy.yaml` · **Catalog status:**
`mcp-hub/catalog.json` host `google-data-agent-kit`.

## The doctrine (why this runbook is short)

Freemium-prep (owner, 2026-10-26): **wire everything before signup.** GCP's
free trial is a $300 credit on a 90-day clock that starts at signup (card
required for identity verification; no automatic charge or upgrade when it
ends — resources stop, with a 30-day grace before deletion). Every hour of
wiring done after signup burns trial. So the repo side is complete first —
catalog, full client config, fleet skill, guardrail policy — and this
runbook is only the steps that physically require the account to exist.

After the trial, the steady state is Always Free: BigQuery 1 TiB of query
processing + 10 GiB storage per month and 5 GiB of Cloud Storage cover the
read-only telemetry workload at fleet scale. Nothing here needs a paid SKU
to keep operating.

## Pre-signup readiness (all repo-side — verify, don't rebuild)

- [ ] `mcp-hub/catalog.json` carries host `google-data-agent-kit` (all 11 servers).
- [ ] `mcp-hub/client-configs/data-agent-kit.json` carries the full server map.
- [ ] `.agents/skills/data-agent-kit/SKILL.md` present on master.
- [ ] `ops/data_agent_kit/guardrail-policy.yaml` present (schema v2) with the
      provisioning command list and per-server role bindings.
- [ ] Plugin install commands recorded for Claude Code, Codex, Antigravity
      CLI, and the VS Code-family extension.

## Signup day — owner steps

1. Create the fleet GCP project under the owner Google account and start the
   free trial (attach the billing account / card for identity verification).
   *Note: sign-in prompts land on the origin B160V (broken screen) — plan
   this as its own session, with the 2SV relay expectation set.*
2. Record the project ID and chosen region in the policy placeholders
   (`<GCP_PROJECT_ID>`, `<GCP_REGION>`) via a small follow-up PR.
3. Set a billing **budget alert** on the project (alerts notify; they do not
   cap — the enforced cost control is `maximum_bytes_billed` below plus the
   read-only identity).

## Signup day — agent steps (any session with project access)

4. Run the provisioning commands from the policy, in order: enable all APIs
   → create the `dak-readonly` service account → grant the project-level
   read bindings → apply the MCP deny policy for non-read-only tools.
5. Create the starter resources: BigQuery dataset `fleet_telemetry` (grant
   `bigquery.dataViewer` to `dak-readonly` at dataset scope; set
   `maximum_bytes_billed`), Cloud Storage bucket `<project>-evidence`
   (grant `storage.objectViewer` at bucket scope).
6. Per surface: install the plugin (commands in the fleet skill), run
   `/dak:dak-setup`, select the fleet project + region + all services.
7. **Disable the plugin telemetry hook** on each surface and verify it is
   off in the surface's hooks config (install-layer control; owner review
   pending). The SessionStart setup-sync hook may stay.
8. Smoke evidence, as the impersonated read-only identity: one BigQuery
   dry-run + one small SELECT against `fleet_telemetry`, one GCS object
   listing on the evidence bucket, one Knowledge Catalog search. Record run
   IDs/timestamps in the PR that flips the catalog status.
9. Flip the catalog `status` to `live_readonly` in a follow-up PR carrying
   the step-8 evidence. Until that PR merges, the wiring is reported as
   pending — never as live.

## The 90 days — what the credits are FOR

- Backfill the telemetry dataset from the repo's existing evidence planes
  (reviewer metrics, quota observations, provenance receipts) and run the
  first real MVT/DoE queries through `dak-bigquery`.
- Evaluate the instance-required servers only against real candidate
  workloads; creating an AlloyDB/Spanner/Bigtable instance just to try the
  server burns credit against the mortality rule (no lane single-homes on a
  free tier; every dependency keeps a named exit — see the design doc).
- Day ~80 checkpoint: confirm Always Free covers the steady workload, export
  anything trial-only worth keeping to GCS → repo artifacts, and let the
  trial lapse without upgrading unless a measured need says otherwise.

## The general freemium pattern (reuse for the next one)

1. Recon the service's real surfaces and guardrail tiers from its own docs.
2. Land the FULL wiring in the repo first: catalog/config, skill, policy,
   provisioning commands, activation runbook.
3. Only then signup — credits fund usage and evaluation, never setup.
4. Activate with evidence; flip the recorded status only on run proof.
5. Keep the exit written down before the first credit is spent.
