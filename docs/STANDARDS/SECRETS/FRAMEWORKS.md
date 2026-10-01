# Secrets Scanning Frameworks — installed + doctrine

## Layers

| Layer | Tool | Location | Runtime | Trigger |
|---|---|---|---|---|
| Local pre-commit | gitleaks | ~/.local/bin/gitleaks 8.30.1 | sub-second on staged diff | pre-commit hook (off by default; RUN_HEAVY_HOOKS=1) |
| Local entropy | scripts/entropy_scan.py | Shannon ≥4.5 on 20+ char runs | pre-commit when enabled |
| Local commit-msg | scripts/commit-msg.sh | Conventional Commits + DO Framework | pre-commit always |
| CI push/PR | .github/workflows/secrets-scan.yml | gitleaks diff + entropy diff | every push + PR |
| CI scheduled fast | .github/workflows/cadence-dispatch.yml (6h cron) | gitleaks full-repo-tree | every 6h |
| CI scheduled deep | cadence-dispatch (Sunday 03:00 UTC) | gitleaks history + trufflehog verified | weekly |
| Cache primer | .github/workflows/hooks-cache.yml | pip + gitleaks + pre-commit cache | Monday 02:00 |
| One-shot mirror | .github/workflows/mirror-secrets.yml (deleted after use) | Actions → Codespaces secret propagation |
| Manual device scan | ~/.local/bin/secrets-scan | bounded detect-secrets (100KB cap) | on demand |
| Baseline suppression | .secrets.baseline | detect-secrets baseline | versioned in repo |
| Path allowlist | .gitleaks.toml | docs/ tests/ session_store/ agent_workspaces/ | versioned in repo |

## Tools present on device

| Binary | Version | Purpose |
|---|---|---|
| gitleaks | 8.30.1 | Primary scanner — diff + full history |
| trufflehog | 3.63.7 (vendor/ only — SIGSYS on Termux) | CI-only; deep verified scan |
| detect-secrets | pip | Baseline + manual scan |
| pre-commit | pip | Framework runner (optional) |
| ruff | 0.16.9 | Python lint (bundled with hook stack) |

## Incident response

1. Detection fires (local, CI, or scheduled).
2. Rotate credential at issuer (per `~/.deepcli/creds/collaborators/README.md`).
3. Log rotation to `~/.deepcli/logs/hygiene/key-rotation.jsonl`.
4. Update `.secrets.baseline` if false positive; add regex to `.gitleaks.toml` allowlist.
5. If committed: rewrite history via BFG or filter-repo; force-push; notify collaborators.
6. Post-mortem to `docs/STANDARDS/RETROSPECTIVES/`.

## False-positive categories (allowlisted)

- `ghp_xxxxxxxx+` — placeholder x-runs in docs
- `test-token-\d+` — fixture tokens
- `Bearer eyJ[...]\.test` — test JWT fragments
- Documentation paths (docs/, *.md)
- Agent workspaces (agent_workspaces/)
- Session transcripts (session_store/) — content, not credentials

## Known gaps

- No device-side trufflehog (SIGSYS blocked by Android seccomp). Falls back to
  gitleaks + entropy on device; trufflehog runs in CI only.
- Codespaces secrets are write-only from API/CLI; mirror workflow is the only
  read path (privileged job context).
- No git-history rewrite has been performed; prior leaked tokens remain in
  history unless rotated. Rotation is authoritative.
