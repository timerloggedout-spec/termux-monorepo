# Data Agent Kit — Wiring Design (iDEAL)

**Status:** wired in repo, READ-ONLY, pending fleet GCP project (owner items below)
**Upstream:** Google Data Agent Kit — https://github.com/GoogleCloudPlatform/data-agent-kit-plugin
**Machine-readable policy:** `ops/data_agent_kit/guardrail-policy.yaml`
**Catalog SSOT for wiring state:** `mcp-hub/catalog.json`, host `google-data-agent-kit` (`status` field)
**Fleet skill:** `.agents/skills/data-agent-kit/SKILL.md`
**Client config:** `mcp-hub/client-configs/data-agent-kit.json`

## 1. What the kit is (verified from upstream, 2026-10-27)

- Google's Data Agent Kit reached GA on 2026-09-30 (Google Cloud blog, "Data
  Agent Kit is now GA"). Free; standard pricing applies only to the Google
  Cloud services used. Plugin repo is Apache-2.0, v1.1.0.
- It connects coding agents (Antigravity CLI, Claude Code, Codex CLI, any
  Agent Plugins-compatible client; IDE extension for VS Code-family editors)
  to 15+ Google Data Cloud services through MCP, plus 37 Google-authored
  open-source skills.
- Verified server map (from the plugin's own `mcp_config.json`): the data
  servers are Google-hosted remote MCP endpoints, reached through a small
  local stdio proxy bundled with the plugin — `dak-bigquery`
  (bigquery.googleapis.com/mcp), `dak-alloydb`, `dak-cloudsql` (sqladmin),
  `dak-spanner`, `dak-bigtable-data`, `dak-bigtable` (admin), `dak-gcs`
  (storage.googleapis.com/storage/mcp), `dak-kc` (dataplex.googleapis.com/mcp,
  Knowledge Catalog), `dak-spark` (dataproc), plus local `dak-notebook` and
  `dak-viz` servers.
- Auth model: the agent connects as you, or as a service account you
  impersonate, via gcloud ADC — so IAM, row/column security, and deny
  policies apply to everything the agent does.
- Prerequisites: Node.js, gcloud CLI authenticated + ADC login. Setup
  (`/dak:dak-setup`) selects a project, enables APIs, installs matching
  skills, and writes the MCP configuration.

## 2. The design lesson, adopted as a fleet rule

The kit ships two control tiers and is explicit that they are not
equivalent:

- Its **skills ask** — e.g. `accidental-data-loss-prevention` instructs the
  agent it MUST obtain explicit consent before DROP TABLE, TRUNCATE, or a
  DELETE without a WHERE clause. This is advisory: an agent can ignore,
  misread, or be prompt-injected past it.
- Its **IAM policy blocks** — Google's own GA guidance for read-only agents
  is a dedicated read-only service account (impersonated), or an IAM deny
  policy that blocks any MCP tool where `tool.isReadOnly` is false.

Fleet rule, now recorded in the guardrail policy: **a destructive-action
rule that lives only in an agent's instructions is not a guardrail.**
Enforcement sits at the credential/permission layer. Skills are for behavior
quality; they are never cited as enforcement in documentation, admission
evidence, or reports. This matches the fleet's existing posture elsewhere
(hub_mcp capability tiers; MCP admission evidence) and extends it to data
access.

## 3. Surface recon — where fleet agents touch data today

- **MCP plane:** `mcp-hub/` (catalog + client-configs; github-remote is the
  live primary for URL-only agents), `hub_mcp/` (governed signed-envelope
  model, no public endpoint), `docs/ops/MCP-ADMISSION-EVIDENCE.schema.json`
  governs MCP admission. The kit enters through the same plane: a catalog
  host entry + a client-config file, not a side door.
- **Agent surfaces:** Claude Code, Codex, Gemini-family (Antigravity),
  Grok, ChatGPT, Manus work the repo through the owner PAT; Jules works
  cloud-side with its own MCP settings (Linear, v0, Render connected;
  Neon/Supabase contested/open); DeepSeek CLI agents run on the origin
  device under route-named GitHub access.
- **Data lanes that would use this:** telemetry (HindSight/Provenance),
  reviewer metrics, quota/provider observations, evidence artifacts — today
  these live in repo files and Actions artifacts. The kit's first job is a
  real query surface over that class of data (MVT/DoE analysis), not a new
  store for it.
- **Data services reality:** the fleet's operational databases are
  Neon/Supabase/Turso/Upstash — none are Google services. Fleet recon
  (2026-10-21, PR #1511) established **no fleet GCP account presence**.

## 4. Wiring decision

**Surfaces (plugin-supported, fleet-used):** Claude Code, Codex CLI,
Antigravity CLI.

**Not wired:** Jules (cloud agent; the kit targets local coding agents and
Jules' MCPs are configured in its own settings — a separate owner decision),
and on-device Termux agents (kit requires Node + gcloud + interactive Google
sign-in; origin-device constraints are remote-first — the device consumes
results, it does not host the kit).

**First-cohort services (3 of 11 servers), all read-only:**

| Server | Why this one |
|---|---|
| `dak-bigquery` | The telemetry/analytics fit: provenance, HindSight, reviewer-metrics, and quota observations are the fleet's MVT/DoE data; BigQuery is the query surface for them. |
| `dak-gcs` | Evidence/artifact storage adjunct to Actions artifacts; read-only object access. |
| `dak-kc` (Dataplex / Knowledge Catalog) | Discovery and lineage over the two above; read-only by role. |

**Deferred, with reasons (do not wire because they exist):** AlloyDB, Cloud
SQL, Spanner, Bigtable (data + admin), Spark — the fleet has no data on any
of them. The Bigtable *admin* server stays excluded even if Bigtable is ever
adopted, under the read-only posture. Notebook/viz are per-surface local
tooling, adoptable later without a fleet decision.

## 5. Guardrail tier map (summary; policy YAML is the SSOT)

| Action class | Tier | Mechanism |
|---|---|---|
| Read schemas/catalogs/job history; SELECT and dry-run queries | Enforced allow | `dak-readonly` SA bindings: `bigquery.dataViewer` (telemetry dataset scope only), `bigquery.jobUser` (project), `storage.objectViewer` (evidence bucket only), `datacatalog.viewer` |
| CREATE / INSERT / UPDATE / DELETE / DROP / TRUNCATE | Enforced deny | No write role exists on the identity; second layer: IAM deny policy on MCP tools where `tool.isReadOnly == false` |
| Credential handling | Enforced | ADC impersonation only; SA keys forbidden; agent data work on owner user credentials forbidden |
| Row/column-level access | Enforced (inherited) | BigQuery policies apply automatically via the impersonated identity |
| Consent before destructive actions; dry-run-first; partition/cost discipline | Advisory | Kit skills (37, incl. `accidental-data-loss-prevention`) + fleet skill — behavior steering, never enforcement |
| Writes via any future identity | Out of scope | Requires a separate design + separate SA + owner approval; skill consent language does not authorize it |

Available hardening recorded in the policy for later: Model Armor MCP
screening, VPC Service Controls, Principal Access Boundary, and BigQuery
`maximum_bytes_billed` (the enforced version of the cost rule).

## 6. Live vs pending — read this before citing the wiring as live

**Wired now (in this repo):** catalog host entry, client config (first
cohort), fleet skill, this design doc, and the machine-readable guardrail
policy with the full IAM binding spec + provisioning commands.

**Pending (owner items — nothing below is faked as done):**

1. **GCP project + billing.** Create the fleet GCP project and attach a
   billing account (card-gated). No fleet GCP presence exists today; this is
   the single step that makes the wiring live.
2. **Sign-in path.** gcloud auth / ADC for the owner Google account lands
   prompts on the origin B160V (broken screen) — plan that session; do not
   improvise it inside another flow.

Once the project exists, an agent session with project access runs the
provisioning commands in `ops/data_agent_kit/guardrail-policy.yaml`
(enable APIs → create `dak-readonly` → grant the four bindings → apply the
deny policy; creates no keys, grants no write roles), then flips the catalog
`status` to `live_readonly` with the run evidence.

## 7. Mortality / exit

Per the fleet free-tier rule, no critical lane single-homes here: the kit is
an additional read path over telemetry-class data; HindSight/Provenance and
the evidence lanes run unchanged without it, and nothing is stored only in
GCP (BigQuery datasets export to GCS as JSONL/Parquet and back into repo
artifacts). The kit itself is Apache-2.0 and its configuration is portable
JSON kept in this repo. Exit: remove the catalog entry + client config,
uninstall the plugin per surface, delete the `dak-readonly` service account
(one action revokes all agent data access). One session, end to end.
