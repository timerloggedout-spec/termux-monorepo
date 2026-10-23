# Phantom-Secrets Audit — 2026-10-22

[MUSEai]@{role:{inventory}} — names only; no secret values exist in this document or were read by the audit.

## Why this exists

Collaborators keep writing workflows that reference `secrets.*` names which were never
provisioned, then failing silently or expecting the name to magically exist. The canonical
case: `REPOSITORY_OBSERVATORY_TOKEN` — referenced by the Repository Observatory, never
provisioned; the workflow silently fell back to `github.token` and produced an empty
Watching table until PR #1560 pointed it at the already-provisioned `OPERATOR_GITHUB_TOKEN`.

## Method

Blobless partial clone + sparse checkout of `.github/workflows` (all files in seconds),
expression-level extraction of `${{ secrets.* }}` references, compared against every
provisioned store read live at audit time: Actions, Codespaces, Dependabot, and all 14
environment stores. Counts below are derived from that live read, not copied forward.

## Totals (live, 2026-10-22)

- Workflow files scanned: **170**
- Provisioned secret names (unique, all stores): **38** (Actions 37, Codespaces 7 with overlap, Dependabot 0, all 14 environment stores 0)
- Distinct `secrets.*` names referenced: **107** in real expressions (109 raw incl. non-expression text)
- Referenced AND provisioned: **26**
- **Phantom names (referenced, never provisioned): 79 hard phantoms + 1 case-variant** (table below lists all 80; excl. `GITHUB_TOKEN`, which GitHub provides)

## Diagnostics before conclusions

- `Fly_io_ORG_TOKEN` (5 fly workflows) is a **case-variant** of provisioned `FLY_IO_ORG_TOKEN` — a spelling-normalisation fix, counted separately from hard phantoms.
- `provision-secrets.yml` references many phantoms **by design** (it is the provisioning/rotation catalog; its own log text anticipates missing secrets). Those are known-absent entries, not silent breakage.
- The provider-key cluster (~25 names) concentrates in `provider-availability.yml` + `provider-batch.yml`: optional probes for provider keys that were never provisioned. They degrade silently — the exact failure shape this audit exists to expose.
- Filename false positives (`redact_secrets.cjs`, `provision-secrets.sh` in a comment) were excluded.

## Phantom names by workflow count

| Secret name (NOT provisioned) | Workflows | Referenced in |
|---|---|---|
| `OMNI_API_KEY` | 9 | `continuous-evaluation.yml`, `gemini-after-peers.yml`, `gemini-invoke.yml`, `gemini-review.yml` … |
| `Fly_io_ORG_TOKEN` | 5 | `deploy-hindsight.yml`, `fly-diag.yml`, `fly-fast-diag.yml`, `fly-hindsight-config.yml` … |
| `OMNIROUTE_API_KEY` | 5 | `gemini-after-peers.yml`, `gemini-invoke.yml`, `gemini-review.yml`, `gemini-triage.yml` … |
| `OMNI_BASE_URL` | 4 | `gemini-after-peers.yml`, `gemini-invoke.yml`, `gemini-review.yml`, `gemini-triage.yml` |
| `VERCEL_ORG_ID` | 4 | `help-wanted-dashboard-deploy.yml`, `tribute-vercel-prod.yml`, `vercel-batch-deploy.yml`, `vercel-quota-probe.yml` |
| `HF_API_TOKEN` | 3 | `provider-availability.yml`, `provider-batch.yml`, `team-mvt.yml` |
| `HUGGINGFACE_TOKEN` | 3 | `provider-availability.yml`, `provider-batch.yml`, `team-mvt.yml` |
| `HUGGING_FACE_HUB_TOKEN` | 3 | `provider-availability.yml`, `provider-batch.yml`, `team-mvt.yml` |
| `NEON_API_KEY` | 3 | `lane-events-recorder.yml`, `tribute-system1.yml`, `vercel-quota-probe.yml` |
| `AION_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `APP_PRIVATE_KEY` | 2 | `github-app-capability-probe.yml`, `remote-knowledge-fabric.yml` |
| `CEREBRAS_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `CODESPACE_CREATE_TOKEN` | 2 | `codespace-create.yml`, `codespace-start.yml` |
| `COHERE_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `GH_AW_GITHUB_MCP_SERVER_TOKEN` | 2 | `agentic-repository-operations-report.lock.yml`, `provision-secrets.yml` |
| `GH_AW_GITHUB_TOKEN` | 2 | `agentic-repository-operations-report.lock.yml`, `provision-secrets.yml` |
| `GOOGLE_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `GROQ_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `HF_TOKEN` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `KILO_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `LANE_EVENTS_DATABASE_URL` | 2 | `lane-events-recorder.yml`, `tribute-system1.yml` |
| `LLM7_API_TOKEN` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `MISTRAL_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `NVIDIA_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `NVIDIA_NIM_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `OLLAMA_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `OPERATOR` | 2 | `provider-batch.yml`, `provision-secrets.yml` |
| `RECON_INTEL_GITLAB_READ_TOKEN` | 2 | `recon-intel-discovery.yml`, `recon-intel-reconcile.yml` |
| `REPOSITORY_OBSERVATORY_TOKEN` | 2 | `provision-secrets.yml`, `repository-observatory.yml` |
| `SAMBANOVA_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `SILICONFLOW_API_KEY` | 2 | `provider-availability.yml`, `provider-batch.yml` |
| `ANTHROPIC_API_KEY` | 1 | `provision-secrets.yml` |
| `AWS_WAF_TOKEN` | 1 | `deepseek-ci.yml` |
| `CODEX_API_KEY` | 1 | `provision-secrets.yml` |
| `COOKIES` | 1 | `deepseek-ci.yml` |
| `COPILOT_GITHUB_TOKEN` | 1 | `provision-secrets.yml` |
| `CROSS_REPO_PAT` | 1 | `provision-secrets.yml` |
| `DEEPSEEK_AUTH_TOKEN` | 1 | `deepseek-ci.yml` |
| `DEEPSEEK_COOKIES` | 1 | `deepseek-ci.yml` |
| `DEEPSEEK_COOKIES_1` | 1 | `deepseek-ci.yml` |
| `DEEPSEEK_COOKIES_2` | 1 | `deepseek-ci.yml` |
| `DEEPSEEK_TOKEN` | 1 | `deepseek-ci.yml` |
| `DEEPSEEK_TOKEN_ACCOUNT_1` | 1 | `deepseek-ci.yml` |
| `DEEPSEEK_TOKEN_ACCOUNT_2` | 1 | `deepseek-ci.yml` |
| `DEEPSEEK_TOKEN_PRIMARY` | 1 | `deepseek-ci.yml` |
| `DEEPSEEK_TOKEN_SECONDARY` | 1 | `deepseek-ci.yml` |
| `DEEPSEEK_WAF_TOKEN` | 1 | `deepseek-ci.yml` |
| `DEEPWIKI_LLM_API_KEY` | 1 | `remote-knowledge-fabric.yml` |
| `DEEPWIKI_TOKEN` | 1 | `remote-knowledge-fabric.yml` |
| `GAMUT_JUDGE_API_KEY` | 1 | `remote-gamut-evaluation.yml` |
| `GH_ACTIONS` | 1 | `provision-secrets.yml` |
| `GH_AW_AGENT_TOKEN` | 1 | `provision-secrets.yml` |
| `GH_AW_CI_TRIGGER_TOKEN` | 1 | `provision-secrets.yml` |
| `GH_PAT` | 1 | `help-wanted-dashboard-deploy.yml` |
| `GITLAB_CICD` | 1 | `provision-secrets.yml` |
| `GITLAB_CICD_W_ORG_VIEW` | 1 | `provision-secrets.yml` |
| `GOVERNED_AUTOMERGE_APP_PRIVATE_KEY` | 1 | `governed-pr-auto-merge-readiness.yml` |
| `GRAFANA_API_KEY` | 1 | `grafana-mcp-smoke.yml` |
| `GRAFANA_SERVICE_ACCOUNT_TOKEN` | 1 | `grafana-mcp-smoke.yml` |
| `GRAFANA_TOKEN` | 1 | `grafana-mcp-smoke.yml` |
| `GRAFANA_URL` | 1 | `grafana-mcp-smoke.yml` |
| `IFLYTEK_SPARK_API_PASSWORD` | 1 | `provider-batch.yml` |
| `KOYEB_API_TOKEN` | 1 | `koyeb-hindsight-deploy.yml` |
| `MODELSCOPE_TOKEN` | 1 | `provider-availability.yml` |
| `N8N_SHE_WEBHOOK_URL` | 1 | `n8n-she-bridge.yml` |
| `NEXUSCLI_TOKEN` | 1 | `deepseek-ci.yml` |
| `OPENAI_API_KEY` | 1 | `provision-secrets.yml` |
| `OPENTYPHOON_API_KEY` | 1 | `provider-batch.yml` |
| `OPERATOR_MATRIX_PROJECT_URL` | 1 | `ops-operator-matrix-project-sync.yml` |
| `OVHCLOUD_API_KEY` | 1 | `provider-availability.yml` |
| `RENDER_API_KEY` | 1 | `vercel-quota-probe.yml` |
| `REQUESTY_API_KEY` | 1 | `provider-batch.yml` |
| `ROUTEWAY_API_KEY` | 1 | `provider-batch.yml` |
| `SEALION_API_KEY` | 1 | `provider-batch.yml` |
| `SWE_EVALUATION_API_KEY` | 1 | `swe-reference-evaluation.yml` |
| `TYPHOON_API_KEY` | 1 | `provider-batch.yml` |
| `UNOROUTER_API_KEY` | 1 | `provider-batch.yml` |
| `WAF_AWS_TOKEN` | 1 | `deepseek-ci.yml` |
| `XFYUN_API_KEY` | 1 | `provider-batch.yml` |
| `XKIRO_API_KEY` | 1 | `provider-batch.yml` |

## The rule going forward

1. A workflow may reference only secret names **verified provisioned** at authoring time (check the stores, or reuse an existing provisioned name as #1560 did).
2. A genuinely new secret is an **owner provisioning act** — name it in the PR as an explicit owner item; never let a workflow silently depend on an unprovisioned name.
3. Optional probes must log the missing name loudly; silent degradation is the bug, not the absence.
4. Re-run this audit when the workflow fleet changes materially; counts are live-derived at report time, never copied forward.
