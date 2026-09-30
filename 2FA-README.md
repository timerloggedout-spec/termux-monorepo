# Termux 2FA Toolchain

Local, scriptable TOTP generation for GitHub, built to run unattended.

## Inventory

- GPG key ID:       `ED76C8D85C3E731F` (ed25519, no expiry)
- Encryption subkey: `3B53A11DA699FE29` (cv25519)
- Pass store:        `~/.password-store/`
- TOTP entry:        `secret/github`
- Passphrase file:   `~/.gnupg/.2fa-pass` (mode 600, no trailing newline)
- Agent cache:       default 8h idle / 24h max; preset via `gpg-prime` uses no-TTL

## Commands

    gh2fa              # print current GitHub TOTP code (auto-reprime on failure)
    ghcode             # raw pass otp output
    gh2fa-copy         # code + clipboard via termux-clipboard-set
    gh2fa-status       # show which keygrips the agent has cached
    gh2fa-prime        # force re-prime the agent
    pass otp secret/github   # raw pass call

## Adding another TOTP entry

    pass otp insert secret/<name>
    # paste the otpauth:// URI at both prompts
    pass otp secret/<name>

## Rotating the GitHub TOTP secret

1. GitHub -> Settings -> Password and authentication -> Two-factor authentication -> Disable
2. Re-enable -> "enter this text code instead" -> copy the new setup key
3. pass otp insert secret/github  (paste new URI, confirm overwrite)
4. gh2fa                          (paste code into GitHub's verify box)
5. Done

## Unattended / agent usage

Any agent entrypoint should run:

    export GPG_TTY=$(tty 2>/dev/null) || true
    gpg-prime >/dev/null 2>&1 || true
    CODE=$(gh2fa)

The cache lives in gpg-agent RAM and is lost when:

- gpgconf --kill gpg-agent is run
- Termux is killed by Android (Doze, memory pressure, reboot)
- The TTLs expire (8h idle / 24h max) -- gpg-prime uses no-TTL, so priming
  once is enough until the agent dies

gh-code already re-primes and retries once on failure.

## Boot persistence

~/.termux/boot/50-gpg-prime primes the agent 15s after Termux:Boot fires:

    #!/data/data/com.termux/files/usr/bin/sh
    sleep 15
    /data/data/com.termux/files/home/bin/gpg-prime >/dev/null 2>&1 || true

Requires the Termux:Boot app to be installed and launched once.

## Threat model

The passphrase is stored in plaintext at ~/.gnupg/.2fa-pass so unattended
agents can decrypt without a TTY. The security boundary is therefore
"whoever can read this Termux home directory."

What you still get:

- Encrypted pass store at rest
- Android app sandbox (no other UID can read the home dir)
- chmod 600 on the passphrase file

If you do not need unattended access:

    shred -u ~/.gnupg/.2fa-pass   # or: rm -P

...then type the passphrase once per session. gpg-agent caches it for 8h.

## Troubleshooting

| Symptom                                                     | Fix |
|-------------------------------------------------------------|-----|
| public key decryption failed: No such file or directory     | GPG_TTY invalid; .zshrc precmd hook should refresh it |
| public key decryption failed: Operation cancelled           | pinentry could not render; ensure a real pty |
| public key decryption failed: Timeout                       | agent unprimed; run gpg-prime |
| Prompts every call                                          | cache wiped; run gpg-prime |
| No public key on insert                                     | pass init used wrong ID; run: pass init ED76C8D85C3E731F |
| command not found: gpg-prime                                | ~/bin not on PATH |
| Agent only has 1 keygrip                                    | old gpg-prime; current version presets all keygrips |

## Regenerating from scratch

    pkg install gnupg pass pass-otp oathtool pinentry-curses
    gpg --full-generate-key         # ECC / Curve 25519 / no expiry
    gpg --list-secret-keys --keyid-format=long
    pass init <LONG_KEY_ID>
    pass otp insert secret/github   # paste otpauth:// URI

Then update GPG_KEY_ID in .zshrc, ~/bin/gpg-prime, and this file.

## History

- 2026-09-25 -- initial setup: GPG key ED76C8D85C3E731F, pass store,
  secret/github entry, gpg-prime + gh-code scripts, boot hook.
  Root cause of setup failures: GPG_TTY captured as the literal string
  "not a tty", and gpg-prime presetting only the primary keygrip (not
  the encryption subkey). Both fixed.
