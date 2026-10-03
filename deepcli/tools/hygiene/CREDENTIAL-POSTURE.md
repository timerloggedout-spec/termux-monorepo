# Credential posture — Termux monorepo

Generated 2026-10-03. Stat-only. No secret value is recorded here.

## Load-bearing credential files

| Path | Role | Owner-side fix |
|---|---|---|
| `~/.deepcli/config.json` | DeepSeek session token (core.py) | local FS, mode 600 |
| `~/.deepcli/hub.token` | bearer for /gh /run /v1/agent | not present; no active references |
| `~/storage/downloads/_doing/_1-build/DeepSeek/exports/cookies_2.json` | account-1 + account-2 auth cookies | **FUSE** — cannot chmod |
| `~/.gnupg/.2fa-pass` | GPG passphrase for TOTP key | local FS, mode 600 |
| `~/.password-store/secret/github.gpg` | encrypted TOTP seed | local FS, mode 600 |

## FUSE limitation

`/storage/emulated/0` (where `cookies_2.json` lives) is a FUSE mount
that Android exposes to apps. It ignores POSIX mode bits. `os.chmod`
returns success but the mode does not change.

**Implication:** the file is readable by anything with Android shared-
storage read permission — which is broad. Termux-side, there is no
`chmod` that changes this.

**Mitigation options (require consent — core.py dependency):**

1. **Relocate** to `~/.deepcli/cookies_2.json` and update core.py to
   read from there. Both accounts keep working; file becomes mode 600
   on local FS.
2. **Encrypt at rest** with gpg to the TOTP key, decrypt in memory on
   read. Requires a core.py patch to add the decrypt step.
3. **Accept** the exposure and rotate cookies on a schedule.

None of these are done unilaterally. Option 1 is the smallest delta.

## Anti-patterns (from doctrine §5)

- Never `cat`, `echo`, or `print` the contents of any of these files.
- Never log them at INFO level or higher.
- Never paste them into a chat or issue.
- Report only: path, size, mode, fs.

## Rotation log

Append-only: `~/.deepcli/logs/hygiene/key-rotation.jsonl`

Current entries:
- gh `gho_` token leaked via `gh auth status --show-token` (session 0d3639e8)
- DeepSeek `ors...` token leaked via verbatim `config.json` dump (this session)
