# GPG recovery — status

## State
- Passphrase file intact: `~/.gnupg/.2fa-pass` (14 bytes UTF-8, no trailing newline)
- Two private keys intact: `26687B1A...` (Curve25519) and `D0836B9B...` (Ed25519)
- Both grips cached: `gpg-connect-agent KEYINFO --list` returns D - - - P
- `pubring.kbx` is 32B (empty) — never restored
- `gpg --list-secret-keys` returns nothing

## What was attempted

| Attempt | Result |
|---|---|
| `EXPORT_KEY` via agent | `ERR Missing key - did you run KEYWRAP_KEY ?` |
| `IMPORT_KEY` with raw S-expr | Same error |
| `IMPORT_KEY --recompute` | Same error |
| Direct `gpg --import` of `.key` files | "no valid OpenPGP data" (S-expr, not OpenPGP) |
| S2K3-OCB decrypt via AESOCB3 | 108 combos, all InvalidTag |
| Passphrase variants (raw/strip/ascii) | All fail |
| Salt variants (hex / hex+null) | All fail |
| Key length (16/24/32) | All fail |
| Tag length (16/12/8) | All fail |

## Root cause hypothesis

GnuPG 2.5 (2026-09-25 key creation) uses a wrap key stored
ephemerally by the agent at key generation time. That key did not
persist across the `.gnupg` rename. The `.key` files hold the
encrypted blob but nothing to unwrap it.

The S2K3-OCB payload is AES-OCB, but the outer wrap layer that
GnuPG normally manages is missing.

## Recovery options

1. **Restore `pubring.kbx` from backup** — scanned `.gnupg.bak.pre-restore/`,
   `.gnupg.pre-rebuild.1790806576/`, `.gnupg.backup.1790984983/`,
   `.gnupg.backup.1790985516/`. All have 32B pubring (empty). None usable.

2. **Direct S2K3-OCB decrypt** — attempted, all 108 combos fail. The
   ciphertext is genuinely not decryptable with the stored passphrase alone.

3. **Fresh key + pass re-init** — requires the GitHub TOTP seed
   (otpauth:// URI or base32 secret). User confirmed: `no`.

4. **Regenerate GitHub TOTP** — GitHub UI → Settings → Password and
   authentication → Two-factor authentication → Recovery Codes →
   Configure authenticator app. Produces a fresh seed. Loses the old
   secret but restores the toolchain.

## Current disposition

Deferred. Not blocking other work. `gh-code` and related scripts
exist and syntax-check; they fail at `pass otp` only because gpg
is empty. Fresh-seed regeneration is the fastest path when the user
chooses to take it.

