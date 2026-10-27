---
name: data-agent-kit
description: Use Google's Data Agent Kit (GA, Apache-2.0) to give coding agents governed access to fleet Google Data Cloud data — all 11 kit MCP servers are fleet-wired (BigQuery, Cloud Storage, Knowledge Catalog day-one; AlloyDB, Cloud SQL, Spanner, Bigtable, Spark instance-ready; notebook/viz local). Use when a task touches Google Cloud data with an agent, or when wiring/evaluating MCP data servers. Enforcement is IAM-tier only (impersonated read-only service account + deny policy); skills and prompts are advisory and never counted as guardrails. The plugin's telemetry hook stays disabled in fleet installs.
---

# Data Agent Kit (fleet wiring)

**Design SSOT:** `docs/ops/DATA-AGENT-KIT-WIRING.md`
**Activation runbook:** `docs/ops/DATA-AGENT-KIT-ACTIVATION.md`
**Guardrail policy (machine-readable):** `ops/data_agent_kit/guardrail-policy.yaml`
**Catalog entry:** `mcp-hub/catalog.json` host `google-data-agent-kit`
**Client config:** `mcp-hub/client-configs/data-agent-kit.json`
**Upstream:** https://github.com/GoogleCloudPlatform/data-agent-kit-plugin (plugin v1.1.0)

## Full wiring — every server, pre-signup

All 11 of the kit's MCP servers are configured in the fleet client config
(freemium-prep doctrine: wire everything BEFORE the GCP account exists, so
the signup trial clock funds usage, not setup). Readiness classes:

| Server | Endpoint | Readiness |
|---|---|---|
| `dak-bigquery` | `https://bigquery.googleapis.com/mcp` | day-one |
| `dak-gcs` | `https://storage.googleapis.com/storage/mcp` | day-one |
| `dak-kc` | `https://dataplex.googleapis.com/mcp` | day-one |
| `dak-alloydb` | `https://alloydb.googleapis.com/mcp` | instance-required |
| `dak-cloudsql` | `https://sqladmin.googleapis.com/mcp` | instance-required |
| `dak-spanner` | `https://spanner.googleapis.com/mcp` | instance-required |
| `dak-bigtable-data` | `https://bigtable.googleapis.com/mcp` | instance-required |
| `dak-spark` | `https://dataproc-$GCP_REGION.googleapis.com/mcp` | instance-required |
| `dak-notebook` | local (plugin) | local |
| `dak-viz` | local (plugin) | local |
| `dak-bigtable` | `https://bigtableadmin.googleapis.com/mcp` | **IAM-denied for agents** (admin plane; wired, no role granted) |

Pipeline surfaces with skills but no MCP server (Dataform/dbt, Managed
Airflow) are covered in the policy's `pipeline_surfaces_without_mcp_servers`.

## Install (per surface)

- Claude Code: `claude plugin marketplace add https://github.com/GoogleCloudPlatform/data-agent-kit-plugin` then `claude plugin install dak@dak-marketplace`
- Codex CLI: `codex plugin marketplace add GoogleCloudPlatform/data-agent-kit-plugin` then `codex plugin add dak@dak-marketplace`
- Antigravity CLI: `agy plugin install https://github.com/GoogleCloudPlatform/data-agent-kit-plugin`
- VS Code-family IDEs: the Data Agent Kit extension (same config + identity rules)

Prerequisites: Node.js, `gcloud` authenticated, ADC (`gcloud auth application-default login`).

**Telemetry hook:** the plugin ships a PreToolUse telemetry hook that
reports tool use. In fleet installs it stays DISABLED (install-layer control
in the policy) until the owner reviews it. Verify after install; the
SessionStart setup-sync hook may stay.

Not wired: Jules (cloud agent; MCPs live in Jules' own settings, kit targets
local agents) and on-device Termux agents (remote-first; device consumes
results, not the kit).

## The fleet rule this skill implements

**A destructive-action rule that lives only in instructions is not a
guardrail.** Two tiers, never conflated:

- **ENFORCED (IAM tier):** agents connect only by impersonating the
  `dak-readonly` service account (ADC; no SA keys, ever; never the owner's
  user credentials for data work). It holds only the per-server read-only
  roles in the policy, plus an IAM deny policy on any MCP tool where
  `tool.isReadOnly` is false. If you are connected as anything else, stop —
  you are outside the wiring.
- **ADVISORY (skill tier):** the kit's 37 skills (grouped inventory in the
  design doc) and this skill steer behavior. They can be ignored or injected
  against; never cite them as enforcement in docs, admission evidence, or
  reports.

## Working rules

1. Read-only posture on every server: SELECT, schema/catalog inspection, job
   history, dry runs. Writes are denied at the identity layer; do not route
   around it (no user credentials, no key creation, no role escalation).
2. Dry run before any non-trivial BigQuery query; partition keys first;
   `maximum_bytes_billed` on the telemetry dataset is the enforced cap.
3. Any write need = a separate design: separate service account, separate
   owner approval. Skill consent language does not authorize writes.
4. Report status honestly from the catalog entry's `status` field
   (`wired_full_pending_gcp_project` until the fleet GCP project exists and
   activation evidence is recorded). Fully wired is not the same as live.

## Exit

No fleet pipeline depends on this path. Exit = remove the catalog entry +
client config, uninstall the plugin, delete the `dak-readonly` SA. Data exits
BigQuery via GCS export to JSONL/Parquet back into repo artifacts.
