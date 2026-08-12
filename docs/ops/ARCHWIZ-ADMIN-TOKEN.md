# ArchWiz Admin Token (4π¢hw12)

**Role:** Second Administrator PAT for Grok / OPERATOR / ArchWiz automation.
**Scope target:** Everything the primary `OPERATOR` token has **except** `delete_repo`.

> GitHub does **not** allow minting classic/fine-grained PATs via API.
> An account owner (or org admin) must create the token in the UI, then store it as a repository/org secret. This document is the SSOT for *what* to create and *where* to wire it.

## Why a second token

| Token | Purpose |
|-------|---------|
| `OPERATOR_GITHUB_TOKEN` / `OPERATOR_TOKEN` | Primary privileged GHA + continuous-ops |
| **`ARCHWIZ_GITHUB_TOKEN`** | Parallel admin lane (ArchWiz / 4π¢hw12) — same repo powers, no delete |
| `GITHUB_TOKEN` | Default job token (limited, short-lived) |
| `DEEPSEEK_TOKEN` | **Model auth only** (DeepSeek web-wrapper / API) — **not** a GitHub PAT |

Never use a GitHub PAT as DeepSeek model auth. Never use `DEEPSEEK_TOKEN` for `gh` / REST admin calls.

## Create the PAT (owner UI — 2 minutes)

### Option A — Fine-grained (preferred)

1. GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate**
2. **Resource owner:** `timerloggedout-spec` (user or org)
3. **Repository access:** Only `termux-monorepo` (or All repos if you intentionally want org-wide)
4. **Permissions** (match OPERATOR, omit destructive repo delete):

| Permission | Access |
|------------|--------|
| Contents | Read and write |
| Metadata | Read-only |
| Pull requests | Read and write |
| Issues | Read and write |
| Actions | Read and write |
| Checks | Read and write |
| Commit statuses | Read and write |
| Workflows | Read and write |
| Administration | Read and write *(repo settings, not delete)* |
| Secrets | Read and write *(optional; for secret rotation jobs)* |
| Variables | Read and write *(optional)* |
| Environments | Read and write *(optional)* |
| Pages | Read and write *(if used)* |
| Deployments | Read and write *(if used)* |

5. **Do not** grant organization `delete_repos` / repository delete capabilities.
6. Generate → copy once → store as secret (below).

### Option B — Classic PAT

Scopes:

```text
repo                  # full repo (includes private)
workflow              # update GHA workflows
write:packages        # if packages used
read:org              # if org membership needed
admin:repo_hook       # if hooks managed via API
```

**Omit:** any org-level delete. Classic `repo` cannot delete the repo by itself; still never store a token that is also used for `DELETE /repos/{owner}/{repo}` automation.

## Store as GitHub Actions secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|--------------|-------|
| `ARCHWIZ_GITHUB_TOKEN` | the new PAT |
| `OPERATOR_GITHUB_TOKEN` | existing primary (keep) |
| `DEEPSEEK_TOKEN` | DeepSeek session/API token only |

Optional alias (if you want one name everywhere):

| Secret name | Notes |
|--------------|-------|
| `OPERATOR_TOKEN` | Fallback some workflows already accept |

## Workflow consumption pattern

```yaml
env:
  # Admin / git / PR writes — ArchWiz first, then OPERATOR, then default
  GH_TOKEN: ${{ secrets.ARCHWIZ_GITHUB_TOKEN || secrets.OPERATOR_GITHUB_TOKEN || secrets.OPERATOR_TOKEN || secrets.GITHUB_TOKEN }}
  # Model auth — never the GH PAT
  DEEPSEEK_TOKEN: ${{ secrets.DEEPSEEK_TOKEN }}
```

`deepseek-ci.yml` and continuous-ops already prefer OPERATOR; follow-up commits add `ARCHWIZ_GITHUB_TOKEN` to the chain.

## Rotation / compromise

1. Revoke the leaked PAT in GitHub settings immediately.
2. Mint a replacement with the same matrix above.
3. Update **only** the secret value — no code change required if the secret *name* is stable.
4. Re-run a canary workflow (`workflow_dispatch` on continuous-ops or deepseek-ci).

## Verification checklist

- [ ] PAT can `gh api user` and sees `timerloggedout-spec`
- [ ] PAT can open/comment on a test PR
- [ ] PAT can `workflow_dispatch` Actions
- [ ] PAT **cannot** be used as `DEEPSEEK_TOKEN` substitute (by policy)
- [ ] Secret scanning clean after paste (never commit the value)

## Trace

| Item | Link |
|------|------|
| DeepSeek CI safe PR | #162 |
| Continuous-ops | #161 |
| Connector catalog | `.github/connectors/README.md` |
| Monikers | `docs/ops/AGENT-MONIKERS.md` (`archW1z`) |

Signed-off-by: Grok (OPERATOR) / archW1z
