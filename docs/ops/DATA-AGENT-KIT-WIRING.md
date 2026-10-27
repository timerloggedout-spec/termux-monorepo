# Data Agent Kit — Fleet Wiring (full, pre-signup)

Status: **wired in repo** — full wiring landed before any GCP account exists
(catalog `google-data-agent-kit`, status `wired_full_pending_gcp_project`).
NOT live against data; activation is a runbook, not a design task:
`docs/ops/DATA-AGENT-KIT-ACTIVATION.md`. Owner items: GCP project + billing
and the gcloud sign-in session.

## Why this round rewrote the first-cohort wiring

PR #1684 wired three servers and deliberately left eight out ("no fleet data
on them"). The owner corrected the posture the same day: for freemium
services like GCP, **everything gets wired before signup** — *"We'll have
free credits on sign up; we're getting EVERYTHING ready before."* The trial
clock starts at signup; wiring after signup spends credit on setup. This
document (plus the policy at schema v2, the full client config, and the
activation runbook) is that complete wiring. What did NOT change: the tier
rule. Full wiring ≠ full permission — enforcement remains IAM-tier only.

## What was verified, and how (recon, two rounds)

| Claim | Evidence |
|---|---|
| Kit is real, GA, Apache-2.0, free | Google Cloud blog 2026-09-30 ("Introducing Data Agent Kit…"); `LICENSE` (Apache-2.0) in `GoogleCloudPlatform/data-agent-kit-plugin`; plugin version 1.1.0 from `plugin.json` |
| Server set + endpoints | `mcp_config.json` read from upstream `main`: 11 servers, exact endpoints; client config mirrors it verbatim |
| Skills: 37, all read from upstream tree | `skills/*/SKILL.md` frontmatter (names + descriptions); `accidental-data-loss-prevention` body read in full — consent language, i.e. advisory |
| Read-only pattern is the vendor's own GA shape | GA blog: read-only Data Agents "can inspect schemas and query data, but… cannot alter or drop tables," via dedicated service accounts, IAM deny policy `tool.isReadOnly` check, row/column security inheritance |
| Hooks ship with the plugin — incl. telemetry | `hooks.json` read upstream: `dak-setup-sync` (SessionStart config sync) and `dak-telemetry` (PreToolUse, matcher `*`, runs `.agents/hooks/telemetry_hook.js` on every tool call) — see "Telemetry hook" below |
| Install routes | Plugin README: Claude Code / Codex / Antigravity CLI commands; VS Code-family IDE extension on Marketplace/Open VSX; `dak-setup` skill drives project/region/service configuration |
| GCP freemium terms | Free trial: $300 credit / 90 days, card for identity verification, no auto-charge or auto-upgrade at end (resources stop; 30-day grace). Always Free: BigQuery 1 TiB queries/mo + 10 GiB storage; Cloud Storage 5 GiB — cross-checked 2026-10-26. **No-card route (verified same day): a project with no billing account runs BigQuery in sandbox mode — 1 TiB/mo queries, 10 GiB storage lifetime, 60-day table expiration, no streaming/DML/Data Transfer Service. Cloud Storage requires billing (Firebase Spark lost Storage 2026-02-03); Dataplex requires billing.** |
| Read-only IAM roles per service | Google IAM docs, cross-checked 2026-10-26: `bigquery.dataViewer` + `bigquery.jobUser`; `storage.objectViewer`; `datacatalog.viewer`; `alloydb.viewer`; `cloudsql.viewer`; `spanner.viewer` + `spanner.databaseReader`; `bigtable.reader`; `dataproc.viewer`; `dataform.viewer` |
| Fleet latent GCP surfaces in-repo | Code search over master: BigQuery appears in `ml/pipelines/recon09/connectors.py` (registry entry), the quota-cadence RFP, and the secrets registry; Firebase is referenced in architecture docs. Zero hits for Dataform/Dataplex/AlloyDB/Spanner/Bigtable — honest "no fleet data there yet," which under the new doctrine changes the timing (wire now), not the roles (read-only when instances exist) |
| No fleet GCP presence exists | PR #1511 (merged 2026-10-22) recon: no GCP project/billing on file → activation needs owner signup (card-gated) |

Not verified / not claimed: per-server tool-list behavior against a live
project (needs the project); whether `dak-kc` requires `dataplex.viewer`
instead of `datacatalog.viewer` (substitution noted in the policy, resolved
at provisioning); exact write-permission delta for AlloyDB database-level
access (metadata role wired; data access is per-instance provisioning).

## The wiring (what landed)

| Piece | Path | Content |
|---|---|---|
| Catalog entry | `mcp-hub/catalog.json` → host `google-data-agent-kit` | All 11 servers, endpoints, full client-config pointer, tier summary, exit |
| Client config | `mcp-hub/client-configs/data-agent-kit.json` | Complete `mcpServers` map mirroring upstream `mcp_config.json` verbatim, with readiness classes |
| Fleet skill | `.agents/skills/data-agent-kit/SKILL.md` | Server table, install per surface, tier rule, working rules |
| Guardrail policy | `ops/data_agent_kit/guardrail-policy.yaml` (schema v2) | Freemium block, per-server roles + readiness, enforced vs advisory tiers, telemetry-hook control, provisioning commands, owner items, exit |
| Activation runbook | `docs/ops/DATA-AGENT-KIT-ACTIVATION.md` | Pre-signup checklist, signup-day sequence, 90-day plan, general freemium pattern |

## Readiness classes

- **Day-one** (answers as soon as the project exists): `dak-bigquery`,
  `dak-gcs`, `dak-kc` — the telemetry/MVT-DoE data class (HindSight
  telemetry exports, provenance receipts, quota observations; first dataset
  `fleet_telemetry`, first bucket `<project>-evidence`).
- **Instance-required** (wired; answers when a fleet instance exists):
  `dak-alloydb`, `dak-cloudsql`, `dak-spanner`, `dak-bigtable-data`,
  `dak-spark`. Fleet databases today are Neon/Supabase; these are ready the
  day any workload lands on GCP, with read-only roles already assigned.
- **Local**: `dak-notebook`, `dak-viz` — plugin-local servers on the agent's
  machine.
- **IAM-denied**: `dak-bigtable` (Bigtable **admin** plane) — wired for
  completeness; the fleet identity holds no role for it and the deny policy
  blocks its non-read-only tools. Wiring is not permission.
- **Skills-only surfaces**: Dataform/dbt pipelines and Managed Airflow have
  no MCP servers in the kit; their skills are wired through the plugin, and
  the policy records the read posture (no `composer.user` grant — it can
  trigger DAGs).

## Guardrail tier map (the rule that doesn't change)

> A destructive-action rule that lives only in agent instructions is NOT a
> guardrail.

**ENFORCED (IAM / install layer)** — full detail in the policy:
impersonated `dak-readonly` service account (ADC, no keys, never owner
credentials) holding only the per-server read-only roles; IAM deny policy on
MCP tools where `tool.isReadOnly == false`; `maximum_bytes_billed` on the
telemetry dataset; row/column policies inherited automatically because the
agent connects as the SA; **plugin telemetry hook disabled** at install.

**ADVISORY (guidance only)**: all 37 kit skills + the fleet skill. Consent
wording like "Confirm Deletion: yes" is phrasing an LLM — it is not an
approval card, a permission, or a check run, and is never cited as
enforcement in fleet documentation or admission evidence.

## The telemetry hook (recon round-2 finding)

The plugin ships a PreToolUse hook that reports tool use
(`.agents/hooks/telemetry_hook.js`, matcher `*`). Nothing in the fleet's
telemetry posture (HindSight/Provenance, retention red lines) was written
for a vendor plugin phoning tool-call data out of every session, so the
fleet default is **disabled at install**, recorded as an enforced-tier
(install-layer) control in the policy, with an owner item to review what it
sends and where before any surface enables it. The SessionStart
`dak-setup-sync` hook is config sync and may stay.

## The freemium-prep doctrine (generalized)

This wiring is the template for future freemium services:

1. Recon real surfaces + guardrail tiers from the vendor's own material.
2. Land the FULL wiring in the repo first — catalog/config, skill, policy,
   provisioning commands, activation runbook.
3. Recon the card gate in round one and name the no-card route (sandbox /
   free plan) before wiring; signup only when the wiring is complete, and
   let trial credits — when a card route exists at all — fund usage and
   evaluation, never setup.
4. Activate with run evidence; flip the recorded status only on proof.
5. Write the exit before the first credit is spent.

## Live vs. pending

- **Live now:** the complete wiring in this repo; the kit's public
  endpoints; per-surface plugin availability.
- **Pending (owner items, reshaped by the card ruling):** the credit card
  is a BLOCK (owner, 2026-10-26) — the trial/billing route is closed.
  (1) Create the GCP project WITHOUT billing — activates the BigQuery
  sandbox (Route A in the runbook); GCS and Knowledge Catalog stay
  pending-billing. (2) The gcloud sign-in session — prompts land on the
  broken-screen B160V; plan it as its own session. (3) Telemetry-hook
  review, whenever convenient (installs stay disabled until then).
- The catalog entry flips to `live_readonly` only with activation evidence
  (runbook step 8), in a follow-up PR.

## Exit

No critical lane may single-home on this path (mortality rule, PR #1511).
HindSight/Provenance and the evidence lanes run unchanged without it; the
kit is an additional read path, never the only copy. Data exits BigQuery
via GCS export (JSONL/Parquet) back into repo artifacts. Exit steps: remove
the catalog entry + client config, uninstall the plugin per surface, delete
the `dak-readonly` service account (revokes all agent data access at once).
One session.

## Appendix — the 37 kit skills (grouped; advisory tier)

- **BigQuery & modeling (10):** bigquery-sql, bigquery-ai-ml,
  bigquery-bigframes, bigquery-data-transfer-service, bigquery-graph-author,
  bigquery-graph-query, dataform-bigquery, dbt-bigquery, data-autocleaning,
  schema-mapping
- **Bigtable (1):** bigtable-basics
- **Storage (4):** google-cloud-storage-basics,
  google-cloud-storage-bucket-architect, google-cloud-storage-fuse,
  gcs-security-assessment
- **Pipelines & orchestration (8):** gcp-data-pipelines,
  gcp-pipeline-orchestration, gcp-pipeline-resource-provisioning,
  gcp-managed-airflow-dag-authoring, gcp-managed-airflow-migrations,
  gcp-managed-airflow-recommendations, gcp-composer-troubleshooting,
  gcp-dataflow
- **Spark (3):** gcp-spark, gcp-spark-troubleshooting,
  gcp-managed-spark-upgrades
- **Lakehouse & catalog (2):** federate-lakehouse-catalog,
  discovering-gcp-data-assets
- **ML, notebooks & data apps (4):** ml-best-practices, notebook-guidance,
  building-data-apps, managing-python-dependencies
- **Safety, auth & setup (5):** accidental-data-loss-prevention, dak-setup,
  google-cloud-auth-verification, enforcing-resource-attribution,
  resolving-mcp-region-configs
