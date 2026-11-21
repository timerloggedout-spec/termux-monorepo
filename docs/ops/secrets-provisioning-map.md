# Secrets provisioning map

Names only; secret values stay in GitHub Actions / device keyrings. The existing administrator token chain is documented in `docs/ops/ARCHWIZ-ADMIN-TOKEN.md`: `ARCHWIZ_GITHUB_TOKEN`, `OPERATOR_GITHUB_TOKEN`, then `OPERATOR_TOKEN`. The repository provisioner specifically consumes `OPERATOR_GITHUB_TOKEN`; values stay out of source, logs, and chat.

| Repo | Secret | Required | Purpose |
|---|---|---|---|
| termux-monorepo | `ARCHWIZ_GITHUB_TOKEN` / `OPERATOR_GITHUB_TOKEN` / `OPERATOR_TOKEN` | yes | Existing administrator credential chain; follows repository-documented precedence |
| termux-monorepo | `OPERATOR_GITHUB_TOKEN` | yes | Fine-grained operator token for routine repo-scoped automation |
| termux-monorepo | `TMX_VAULT_AGE_KEY` | yes for vault operations | Age private key for vault restore |

## Controller export repository provisioning

The committed manifest at `ops/provisioning/controller-2-export.json` is the request record. The audited `operator-wake` command `provision-controller-export` reads the manifest, dispatches `.github/workflows/repository-provisioner.yml`, and watches the run. The provisioner uses the existing `OPERATOR_GITHUB_TOKEN` secret, verifies its identity is the personal account `timerloggedout-spec`, creates the public repository with GitHub's default README initialization, validates returned metadata, and publishes a run receipt. The request uses the existing `<!-- request-operator-wake -->` issue-comment marker; the provisioning workflow remains `workflow_dispatch` only.

The separate `REPOSITORY_PROVISIONER_TOKEN` setup path is retired.

## Credential boundaries

- `ARCHWIZ_GITHUB_TOKEN`, `OPERATOR_GITHUB_TOKEN`, and `OPERATOR_TOKEN` stay inside Actions as the existing repo-admin credential chain.
- `OPERATOR_GITHUB_TOKEN` remains the least-privilege routine automation credential.
- Keep credential values out of Git, Actions summaries, artifacts, and chat.
- The public export repository receives redacted export artifacts only; raw Device 2 source data remains private until explicitly approved for export.
