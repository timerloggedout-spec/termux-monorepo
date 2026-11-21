# Secrets provisioning map

Names only; no values live in this repo. Set values from the device with `scripts/termux/provision-secrets.sh set` (reads hidden input or `termux-clipboard-get`, pipes to `gh secret set`).

Token sources refer to the inventory in #184. Least privilege: prefer a new fine-grained PAT scoped to the named repo(s); never use the admin-scoped classic PATs (`Gh_actions`, `timers-full+accessPAT`, classic `DEEPSEEK_API_KEY`) for Actions secrets.

| Repo | Secret | Required | Token to use | Needed by |
|---|---|---|---|---|
| gh-aw-mcpg_fork | `CROSS_REPO_PAT` | yes | NEW fine-grained (Issues RW on gh-aw-mcpg_fork + target repos); fallback gitlab_cicd (classic, repo) | Gateway Issue Dispatcher: "Input required and not supplied: github-token" |
| gh-aw-mcpg_fork | `GH_AW_GITHUB_TOKEN` | yes | ARCHWIZ_GITHUB_TOKEN (fine-grained) if it covers the fork; fallback gitlab_cicd | all 29 scheduled agentic workflows (safe outputs) |
| gh-aw-mcpg_fork | `GH_AW_GITHUB_MCP_SERVER_TOKEN` | yes | NEW fine-grained read-only (Contents/Issues/PRs/Actions read); fallback gitlab_cicd-w+org_view | GitHub MCP server inside agent jobs |
| gh-aw-mcpg_fork | `GH_AW_CI_TRIGGER_TOKEN` | no | NEW fine-grained (Contents RW); fallback gitlab_cicd | 7 workflows that push and must trigger CI |
| gh-aw_fork | `GH_AW_GITHUB_TOKEN` | yes | ARCHWIZ_GITHUB_TOKEN (fine-grained) if it covers the fork; fallback gitlab_cicd | all 239 scheduled agentic workflows |
| gh-aw_fork | `GH_AW_GITHUB_MCP_SERVER_TOKEN` | yes | NEW fine-grained read-only; fallback gitlab_cicd-w+org_view | GitHub MCP server inside agent jobs |
| gh-aw_fork | `COPILOT_GITHUB_TOKEN` | yes | NEW fine-grained with "Copilot Requests" permission (no #184 token fits; do not use admin classics) | 153 Copilot-engine workflows |
| gh-aw_fork | `GH_AW_CI_TRIGGER_TOKEN` | no | NEW fine-grained (Contents RW); fallback gitlab_cicd | 56 workflows that push and must trigger CI |
| gh-aw_fork | `GH_AW_AGENT_TOKEN` | no | NEW fine-grained (Issues/PRs RW, Actions RW) | 13 workflows that assign the Copilot coding agent |
| gh-aw_fork | `ANTHROPIC_API_KEY` | no | provider key (not a GitHub token) | 49 Claude-engine workflows |
| gh-aw_fork | `OPENAI_API_KEY` | no | provider key (not a GitHub token) | 59 Codex-engine workflows |
| gh-aw_fork | `CODEX_API_KEY` | no | provider key; same value as OPENAI_API_KEY | 58 Codex-engine workflows |
| termux-monorepo | `OPERATOR_GITHUB_TOKEN` | yes | ARCHWIZ_GITHUB_TOKEN (fine-grained, termux-monorepo: Contents/Issues/PRs/Actions/Workflows RW) | 23 workflows (preferred operator token) |
| termux-monorepo | `REPOSITORY_PROVISIONER_TOKEN` | yes | NEW fine-grained PAT for personal account `timerloggedout-spec`, Repository creation: write only | `.github/workflows/repository-provisioner.yml` |
| termux-monorepo | `OPERATOR_TOKEN` | no | same value as OPERATOR_GITHUB_TOKEN | 22 workflows (legacy name) |
| termux-monorepo | `ARCHWIZ_GITHUB_TOKEN` | no | ARCHWIZ_GITHUB_TOKEN (fine-grained) | 22 workflows (fallback chain) |
| termux-monorepo | `GH_PAT` | no | NEW fine-grained (Contents RW on timerloggedout-spec.github.io) | tribute-dashboard-deploy mirror |
| termux-monorepo | `CODESPACE_CREATE_TOKEN` | no | NEW fine-grained (Codespaces RW); fallback none of #184 without admin scopes | codespace-create / codespace-start |
| termux-monorepo | `RECON_INTEL_GITHUB_WRITE_TOKEN` | no | NEW fine-grained (Issues RW) | recon-intel-reconcile |
| termux-monorepo | `REPOSITORY_OBSERVATORY_TOKEN` | no | gitlab_cicd-w+org_view (read:org, repo) or NEW fine-grained read-only | repository-observatory |
| termux-monorepo | `DEEPSEEK_API_KEY` | no | DeepSeek platform API key (NOT the GitHub classic PAT also named DEEPSEEK_API_KEY) | deepseek-ci |
| termux-monorepo | `LINEAR_API_KEY` | no | Linear API key | agent-feedback-linear-sync, context-relationship-linear-freshness |
| termux-monorepo | `JULES_API_KEY` | no | Jules API key | agent-jules-on-issues, agent-review-auto-jules |

## Controller export repository provisioning

1. Create a fine-grained PAT owned by `timerloggedout-spec` with the single account permission `Repository creation: write`. GitHub added this least-privilege permission in October 2026; it replaces the broader `Administration: write` requirement for this endpoint.
2. On the Termux device, store it as the Actions secret using the existing hidden-input helper:

   ```bash
   scripts/termux/provision-secrets.sh set --only REPOSITORY_PROVISIONER_TOKEN --repo timerloggedout-spec/termux-monorepo
   ```

3. Dispatch and watch the exact personal-account provisioning run:

   ```bash
   scripts/termux/provision-secrets.sh provision-controller-export
   ```

The workflow enforces token identity `timerloggedout-spec`, creates `controller-2-export` as public, and emits a run receipt. The general operator token remains scoped to the monorepo.

## Notes
- `REPOSITORY_PROVISIONER_TOKEN` is a dedicated account-level creation credential for `/user/repos`; keep it separate from `OPERATOR_GITHUB_TOKEN`, which is scoped to the existing monorepo. The provisioner verifies the token identity is `timerloggedout-spec`. GitHub fine-grained PAT permission: `Repository creation: write` (least-privilege alternative to broad Administration: write).
- `gh-aw_fork` and `gh-aw-mcpg_fork` run upstream github/gh-aw schedules (268 scheduled `.lock.yml`). Until required secrets are set, `provision-secrets.sh pause-forks` disables them reversibly; `resume-forks` restores exactly that list.
- gh-aw_fork has Issues disabled, so the `conclusion` job cannot open failure-tracking issues; enable Issues on the fork or accept that warning.
- Optional, leave unset unless wanted: GH_AW_OTEL_* (Sentry/Grafana), GH_AW_DEFAULT_OTLP_HEADERS, DOCKER_*, DD_*, SLACK_BOT_TOKEN, TAVILY_API_KEY.
- The classic PAT named `DEEPSEEK_API_KEY` in #184 is a GitHub token, not a DeepSeek key. Do not store it as the `DEEPSEEK_API_KEY` secret.
- Security: #184 is public and lists never-expiring admin-scoped classic PATs. Rotate them, set expirations, and revoke unused ones (`DEEPSEEK_API_KEY` classic, `timers-full+accessPAT`, `gitlab_cicd` are marked never used).
