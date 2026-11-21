# Secrets provisioning map

Names only; secret values stay in GitHub Actions / device keyrings. The existing `OPERATOR` Actions secret is documented in `docs/ops/CREDENTIAL-INVENTORY.md` as full-access steward automation. The repository provisioner consumes it inside Actions; the value stays out of source, logs, and chat.

| Repo | Secret | Required | Purpose |
|---|---|---|---|
| termux-monorepo | `OPERATOR` | yes | Existing full-access steward credential for repository administration and account-level repository creation |
| termux-monorepo | `OPERATOR_GITHUB_TOKEN` | yes | Fine-grained operator token for routine repo-scoped automation |
| termux-monorepo | `TMX_VAULT_AGE_KEY` | yes for vault operations | Age private key for vault restore |

## Controller export repository provisioning

The committed manifest at `ops/provisioning/controller-2-export.json` is the request record. A push to `master` that changes this manifest starts `.github/workflows/repository-provisioner.yml`. The workflow uses the existing `OPERATOR` Actions secret, verifies its identity is the personal account `timerloggedout-spec`, creates the public `controller-2-export` repository with GitHub's default README initialization, verifies the returned repository identity, and publishes a run receipt.

The workflow is idempotent for an existing repository with matching owner, slug, and visibility. A manual `workflow_dispatch` reruns the same manifest-driven operation. The separate `REPOSITORY_PROVISIONER_TOKEN` setup path is retired.

## Credential boundaries

- `OPERATOR` stays inside Actions as the existing repo-admin credential.
- `OPERATOR_GITHUB_TOKEN` remains the least-privilege routine automation credential.
- Keep credential values out of Git, Actions summaries, artifacts, and chat.
- The public export repository receives redacted export artifacts only; raw Device 2 source data remains private until explicitly approved for export.
