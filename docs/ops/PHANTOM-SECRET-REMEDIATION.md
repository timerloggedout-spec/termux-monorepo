# Phantom-Secret Remediation

Generated 2026-10-28T01:10:06.074615+00:00 by the phantom-secrets audit (repo-native, repeatable: `.github/workflows/phantom-secrets-audit.yml`). Counts are derived live at generation time. Names only — no secret values exist in this document.

- Phantom names: **60** across **139** references
- compiled: 20 references
- dead-branch: 5 references
- provisioning: 114 references

## Retired — dead fallback branches (PR #1858)

Each reference below was one branch of a `||` fallback chain that also names a provisioned secret; the branch could never resolve and was removed. Behavior is unchanged — the chains resolve exactly as they did before, now without the phantom name.

- `secrets.HF_API_TOKEN` — provider-batch.yml, team-mvt.yml
- `secrets.HF_TOKEN` — provider-batch.yml
- `secrets.HUGGING_FACE_HUB_TOKEN` — provider-batch.yml, team-mvt.yml

## Owner provisioning checklist

No verified provisioned replacement exists for these names. Each is an explicit owner provisioning item: provision the name (with its real value) if the integration should be live, or remove the reference. Nothing here was guessed or silently mapped.

- [ ] `secrets.ANTHROPIC_API_KEY` — provision-secrets.yml — provisioning catalog entry (by design)
- [ ] `secrets.APP_PRIVATE_KEY` — github-app-capability-probe.yml, remote-knowledge-fabric.yml
- [ ] `secrets.CEREBRAS_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.CODESPACE_CREATE_TOKEN` — codespace-create.yml
- [ ] `secrets.CODEX_API_KEY` — provision-secrets.yml — provisioning catalog entry (by design)
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
- [ ] `secrets.DEVIN_API_KEY` — reconcile-devin-wiki-access.yml
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
- [ ] `secrets.GOVERNED_AUTOMERGE_APP_PRIVATE_KEY` — governed-pr-auto-merge-readiness.yml
- [ ] `secrets.GRAFANA_API_KEY` — grafana-mcp-smoke.yml
- [ ] `secrets.GRAFANA_SERVICE_ACCOUNT_TOKEN` — grafana-mcp-smoke.yml
- [ ] `secrets.GRAFANA_TOKEN` — grafana-mcp-smoke.yml
- [ ] `secrets.GRAFANA_URL` — grafana-mcp-smoke.yml
- [ ] `secrets.HF_API_TOKEN` — provider-availability.yml, team-mvt.yml
- [ ] `secrets.HF_TOKEN` — provider-availability.yml
- [ ] `secrets.HUGGING_FACE_HUB_TOKEN` — provider-availability.yml, team-mvt.yml
- [ ] `secrets.IFLYTEK_SPARK_API_PASSWORD` — provider-batch.yml
- [ ] `secrets.KILO_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.KOYEB_API_TOKEN` — koyeb-hindsight-deploy.yml
- [ ] `secrets.LANE_EVENTS_DATABASE_URL` — lane-events-recorder.yml, observer-poller-scheduled.yml, tribute-system1.yml
- [ ] `secrets.MISTRAL_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.MODELSCOPE_TOKEN` — provider-availability.yml
- [ ] `secrets.N8N_SHE_WEBHOOK_URL` — n8n-she-bridge.yml
- [ ] `secrets.NEON_API_KEY` — lane-events-recorder.yml, observer-poller-scheduled.yml, tribute-system1.yml, vercel-quota-probe.yml
- [ ] `secrets.NEXUSCLI_TOKEN` — deepseek-ci.yml
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
- [ ] `secrets.SILICONFLOW_API_KEY` — provider-availability.yml, provider-batch.yml
- [ ] `secrets.SWE_EVALUATION_API_KEY` — swe-reference-evaluation.yml
- [ ] `secrets.TYPHOON_API_KEY` — provider-batch.yml
- [ ] `secrets.UNOROUTER_API_KEY` — provider-batch.yml
- [ ] `secrets.VERCEL_ORG_ID` — help-wanted-dashboard-deploy.yml, tribute-vercel-prod.yml, vercel-batch-deploy.yml, vercel-quota-probe.yml
- [ ] `secrets.XFYUN_API_KEY` — provider-batch.yml
- [ ] `secrets.XKIRO_API_KEY` — provider-batch.yml

## Rule

Workflows may reference only verified-provisioned secret names. A new secret is an owner provisioning act, named explicitly — never an assumption baked into a workflow.
