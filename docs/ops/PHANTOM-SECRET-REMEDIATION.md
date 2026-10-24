# Phantom-Secret Remediation

Generated 2026-10-24T19:54:31.573217+00:00 by the phantom-secrets audit (repo-native, repeatable: `.github/workflows/phantom-secrets-audit.yml`). Counts are derived live at generation time. Names only — no secret values exist in this document.

- Phantom names: **81** across **194** references
- case-variant: 9 references
- compiled: 20 references
- dead-branch: 28 references
- provisioning: 137 references

## Repointed — case variants (PR #1637)

- `secrets.Fly_io_ORG_TOKEN` → `secrets.FLY_IO_ORG_TOKEN` (case-variant of the provisioned name) — deploy-hindsight.yml, fly-diag.yml, fly-fast-diag.yml, fly-hindsight-config.yml, fly-ssh-diag.yml

## Retired — dead fallback branches (PR #1638)

Each reference below was one branch of a `||` fallback chain that also names a provisioned secret; the branch could never resolve and was removed. Behavior is unchanged — the chains resolve exactly as they did before, now without the phantom name.

- `secrets.AWS_WAF_TOKEN` — deepseek-ci.yml
- `secrets.CODESPACE_CREATE_TOKEN` — codespace-create.yml, codespace-start.yml
- `secrets.DEEPSEEK_AUTH_TOKEN` — deepseek-ci.yml
- `secrets.DEEPSEEK_TOKEN` — deepseek-ci.yml
- `secrets.DEEPSEEK_TOKEN_ACCOUNT_1` — deepseek-ci.yml
- `secrets.DEEPSEEK_TOKEN_PRIMARY` — deepseek-ci.yml
- `secrets.DEEPSEEK_WAF_TOKEN` — deepseek-ci.yml
- `secrets.GH_PAT` — help-wanted-dashboard-deploy.yml
- `secrets.GOOGLE_API_KEY` — provider-batch.yml
- `secrets.NEXUSCLI_TOKEN` — deepseek-ci.yml
- `secrets.OPERATOR` — delphi-intake.yml, operator-wake.yml, provider-batch.yml
- `secrets.RECON_INTEL_GITLAB_READ_TOKEN` — recon-intel-discovery.yml, recon-intel-reconcile.yml
- `secrets.REPOSITORY_OBSERVATORY_TOKEN` — repository-observatory.yml
- `secrets.WAF_AWS_TOKEN` — deepseek-ci.yml

## Owner provisioning checklist

No verified provisioned replacement exists for these names. Each is an explicit owner provisioning item: provision the name (with its real value) if the integration should be live, or remove the reference. Nothing here was guessed or silently mapped.

- [ ] `secrets.AION_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.ANTHROPIC_API_KEY` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.APP_PRIVATE_KEY` — github-app-capability-probe.yml, remote-knowledge-fabric.yml
- [ ] `secrets.CEREBRAS_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.CODESPACE_CREATE_TOKEN` — codespace-create.yml
- [ ] `secrets.CODEX_API_KEY` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.COHERE_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.COOKIES` — deepseek-ci.yml
- [ ] `secrets.COPILOT_GITHUB_TOKEN` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.CROSS_REPO_PAT` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.DEEPSEEK_AUTH_TOKEN` — deepseek-ci.yml
- [ ] `secrets.DEEPSEEK_COOKIES` — deepseek-ci.yml
- [ ] `secrets.DEEPSEEK_COOKIES_1` — deepseek-ci.yml
- [ ] `secrets.DEEPSEEK_COOKIES_2` — deepseek-ci.yml
- [ ] `secrets.DEEPSEEK_TOKEN_ACCOUNT_2` — deepseek-ci.yml
- [ ] `secrets.DEEPSEEK_TOKEN_SECONDARY` — deepseek-ci.yml
- [ ] `secrets.DEEPWIKI_LLM_API_KEY` — remote-knowledge-fabric.yml
- [ ] `secrets.DEEPWIKI_TOKEN` — remote-knowledge-fabric.yml
- [ ] `secrets.GAMUT_JUDGE_API_KEY` — remote-gamut-evaluation.yml
- [ ] `secrets.GH_ACTIONS` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.GH_AW_AGENT_TOKEN` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.GH_AW_CI_TRIGGER_TOKEN` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.GH_AW_GITHUB_MCP_SERVER_TOKEN` — agentic-repository-operations-report.lock.yml — compiled gh-aw lock file; fix at the workflow source, not by hand-editing
- [ ] `secrets.GH_AW_GITHUB_MCP_SERVER_TOKEN` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.GH_AW_GITHUB_TOKEN` — agentic-repository-operations-report.lock.yml — compiled gh-aw lock file; fix at the workflow source, not by hand-editing
- [ ] `secrets.GH_AW_GITHUB_TOKEN` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.GITLAB_CICD` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.GITLAB_CICD_W_ORG_VIEW` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.GOOGLE_API_KEY` — provider-availability.yml
- [ ] `secrets.GOVERNED_AUTOMERGE_APP_PRIVATE_KEY` — governed-pr-auto-merge-readiness.yml
- [ ] `secrets.GRAFANA_API_KEY` — grafana-mcp-smoke.yml
- [ ] `secrets.GRAFANA_SERVICE_ACCOUNT_TOKEN` — grafana-mcp-smoke.yml
- [ ] `secrets.GRAFANA_TOKEN` — grafana-mcp-smoke.yml
- [ ] `secrets.GRAFANA_URL` — grafana-mcp-smoke.yml
- [ ] `secrets.GROQ_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.HF_API_TOKEN` — provider-availability.yml, provider-batch.yml, team-mvt.yml
- [ ] `secrets.HF_TOKEN` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.HUGGINGFACE_TOKEN` — provider-availability.yml, provider-batch.yml, team-mvt.yml
- [ ] `secrets.HUGGING_FACE_HUB_TOKEN` — provider-availability.yml, provider-batch.yml, team-mvt.yml
- [ ] `secrets.IFLYTEK_SPARK_API_PASSWORD` — provider-batch.yml
- [ ] `secrets.KILO_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.KOYEB_API_TOKEN` — koyeb-hindsight-deploy.yml
- [ ] `secrets.LANE_EVENTS_DATABASE_URL` — lane-events-recorder.yml, tribute-system1.yml
- [ ] `secrets.LLM7_API_TOKEN` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.MISTRAL_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.MODELSCOPE_TOKEN` — provider-availability.yml
- [ ] `secrets.N8N_SHE_WEBHOOK_URL` — n8n-she-bridge.yml
- [ ] `secrets.NEON_API_KEY` — lane-events-recorder.yml, tribute-system1.yml, vercel-quota-probe.yml
- [ ] `secrets.NEXUSCLI_TOKEN` — deepseek-ci.yml
- [ ] `secrets.NVIDIA_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.NVIDIA_NIM_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.OLLAMA_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.OMNIROUTE_API_KEY` — gemini-after-peers.yml, gemini-invoke.yml, gemini-review.yml, gemini-triage.yml, help-wanted-llm-assist.yml
- [ ] `secrets.OMNI_API_KEY` — continuous-evaluation.yml, gemini-after-peers.yml, gemini-invoke.yml, gemini-review.yml, gemini-triage.yml, help-wanted-llm-assist.yml, provider-availability.yml, provider-batch.yml, team-mvt.yml
- [ ] `secrets.OMNI_BASE_URL` — gemini-after-peers.yml, gemini-invoke.yml, gemini-review.yml, gemini-triage.yml
- [ ] `secrets.OPENAI_API_KEY` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.OPENTYPHOON_API_KEY` — provider-batch.yml
- [ ] `secrets.OPERATOR` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.OPERATOR_MATRIX_PROJECT_URL` — ops-operator-matrix-project-sync.yml
- [ ] `secrets.OVHCLOUD_API_KEY` — provider-availability.yml
- [ ] `secrets.RENDER_API_KEY` — vercel-quota-probe.yml
- [ ] `secrets.REPOSITORY_OBSERVATORY_TOKEN` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.REQUESTY_API_KEY` — provider-batch.yml
- [ ] `secrets.ROUTEWAY_API_KEY` — provider-batch.yml
- [ ] `secrets.SAMBANOVA_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.SEALION_API_KEY` — provider-batch.yml
- [ ] `secrets.SILICONFLOW_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.SUPABASE_SERVICE_ROLE_KEY` — quota-dispatch-tree.yml
- [ ] `secrets.SWE_EVALUATION_API_KEY` — swe-reference-evaluation.yml
- [ ] `secrets.TYPHOON_API_KEY` — provider-batch.yml
- [ ] `secrets.UNOROUTER_API_KEY` — provider-batch.yml
- [ ] `secrets.VERCEL_ORG_ID` — help-wanted-dashboard-deploy.yml, tribute-vercel-prod.yml, vercel-batch-deploy.yml, vercel-quota-probe.yml
- [ ] `secrets.XFYUN_API_KEY` — provider-batch.yml
- [ ] `secrets.XKIRO_API_KEY` — provider-batch.yml

## Rule

Workflows may reference only verified-provisioned secret names. A new secret is an owner provisioning act, named explicitly — never an assumption baked into a workflow.
