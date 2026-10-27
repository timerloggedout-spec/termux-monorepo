---
name: data-agent-kit
description: Use Google's Data Agent Kit (GA, Apache-2.0) to give coding agents read-only access to fleet Google Data Cloud data — BigQuery telemetry, Cloud Storage evidence, Knowledge Catalog discovery — under fleet guardrails. Use when a task needs querying or exploring fleet data in Google Cloud, or when wiring/evaluating MCP data servers. Enforcement is IAM-tier only (impersonated read-only service account + deny policy); skills and prompts are advisory and never counted as guardrails.
---

# Data Agent Kit (fleet wiring)

**Design SSOT:** `docs/ops/DATA-AGENT-KIT-WIRING.md`
**Guardrail policy (machine-readable):** `ops/data_agent_kit/guardrail-policy.yaml`
**Catalog entry:** `mcp-hub/catalog.json` host `google-data-agent-kit`
**Client config:** `mcp-hub/client-configs/data-agent-kit.json`
**Upstream:** https://github.com/GoogleCloudPlatform/data-agent-kit-plugin (plugin v1.1.0)

## What is wired

First cohort only — three of the kit's eleven MCP servers, all read-only:

| Server | Endpoint | Fleet use |
|---|---|---|
| `dak-bigquery` | `https://bigquery.googleapis.com/mcp` | Telemetry / provenance / reviewer-metrics / quota analysis (MVT-DoE lane) |
| `dak-gcs` | `https://storage.googleapis.com/storage/mcp` | Evidence artifacts (read-only) |
| `dak-kc` | `https://dataplex.googleapis.com/mcp` | Knowledge Catalog discovery |

The other servers (alloydb, cloudsql, spanner, bigtable, spark, notebook, viz)
are NOT wired: the fleet has no data on them. Do not wire a server because it
exists; wire it when fleet data lands on the service.

## Install (per surface)

- Claude Code: `claude plugin marketplace add https://github.com/GoogleCloudPlatform/data-agent-kit-plugin` then `claude plugin install dak@dak-marketplace`
- Codex CLI: `codex plugin marketplace add GoogleCloudPlatform/data-agent-kit-plugin` then `codex plugin add dak@dak-marketplace`
- Antigravity CLI: `agy plugin install https://github.com/GoogleCloudPlatform/data-agent-kit-plugin`

Prerequisites: Node.js, `gcloud` authenticated, ADC (`gcloud auth application-default login`).

Not wired: Jules (cloud agent; MCPs live in Jules' own settings, kit targets
local agents) and on-device Termux agents (remote-first; device consumes
results, not the kit).

## The fleet rule this skill implements

**A destructive-action rule that lives only in instructions is not a
guardrail.** Two tiers, never conflated:

- **ENFORCED (IAM tier):** agents connect only by impersonating the
  `dak-readonly` service account (ADC; no SA keys, ever; never the owner's
  user credentials for data work). It holds read-only roles scoped per
  dataset/bucket, plus an IAM deny policy on any MCP tool where
  `tool.isReadOnly` is false. If you are connected as anything else, stop —
  you are outside the wiring.
- **ADVISORY (skill tier):** the kit's 37 skills (incl.
  `accidental-data-loss-prevention`) and this skill steer behavior. They can
  be ignored or injected against; never cite them as enforcement in docs,
  admission evidence, or reports.

## Working rules

1. Read-only posture: SELECT, schema/catalog inspection, job history, dry runs.
   Writes are denied at the identity layer; do not attempt to route around it
   (no switching to user credentials, no key creation).
2. Dry run before any non-trivial BigQuery query; check partition keys first
   (cost discipline — skills steer this, `maximum_bytes_billed` enforces it
   once set on the dataset).
3. Any future write need = a separate design: separate service account,
   separate owner approval. The consent language in the kit's skills does not
   authorize writes under this wiring.
4. Report status honestly from the catalog entry's `status` field
   (`wired_readonly_pending_gcp_project` until the fleet GCP project exists).
   Wired in the repo is not the same as live against data.

## Exit

No fleet pipeline depends on this path. Exit = remove the catalog entry +
client config, uninstall the plugin, delete the `dak-readonly` SA. Data exits
BigQuery via GCS export to JSONL/Parquet back into repo artifacts.
