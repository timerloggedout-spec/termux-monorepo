# Credential inventory (names only)

Policy for issue #184. **Never commit secret values.** Rotate expired tokens off-repo.

## Operator rules
- Inventory records name, owner surface, last-used class, and intended scope.
- Values live in GitHub Actions secrets / device keyrings only.
- Classic PATs with unused admin scopes should be rotated to fine-grained tokens.
- Expired fine-grained tokens must be deleted, not reused.

## Named surfaces (no values)

| Name | Class | Intended use | Notes |
|---|---|---|---|
| `OPERATOR` | Actions secret | repo admin automation | Full access granted for steward ops; do not echo |
| `ARCHWIZ_GITHUB_TOKEN` | fine-grained PAT | unused historically | Rotate or delete if still present |
| `DeepSeek_account-1` | fine-grained PAT | expired | Delete; do not renew as classic |
| `Gh_actions` | classic PAT | Actions + API | Prefer fine-grained replacement |
| `gitlab_cicd-w+org_view` | classic PAT | GitLab non-gate | GitLab remains non-blocking |
| `gitlab_cicd` | classic PAT | unused | Candidate delete |
| `timers-full+accessPAT` | classic PAT | unused | Candidate delete |
| `DEEPSEEK_API_KEY` | classic PAT name collision | unused | Name is not an API key store in-repo |

## App classes (non-gate)
CodeRabbit, Qodo, Devin, Jules, Copilot, Vercel, Linear, Grok GitHub App are review/deploy adapters. Dual-gate remains `repo-gate` + `termux-smoke` on the candidate SHA.

## Rotation checklist
1. Confirm last-used class from GitHub settings UI (do not paste tokens).
2. Replace unused classic admin-scope tokens with fine-grained repo-scoped tokens.
3. Delete expired tokens.
4. Rebind Actions secrets by name only.
5. Record rotation date here without values.

Last inventory pass: 2026-09-24 (names-only recon; no secret material).
