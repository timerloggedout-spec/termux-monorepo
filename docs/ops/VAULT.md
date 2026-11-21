# Encrypted vault lane

Private data (session archives, backups, large binaries) is **encrypted before it leaves the node** and only ciphertext is stored in this public repository or in external storage.

| Piece | Where |
|---|---|
| Public recipient (encrypt) | `ops/vault/recipients.txt` (age X25519) |
| Private key (decrypt) | Node: `~/.config/tmx-vault/age.key` (600). CI: secret `TMX_VAULT_AGE_KEY` (Actions + Codespaces) |
| Ciphertext in Git | `vault/**/*.age`, stored via Git LFS (`.gitattributes`) |
| Ciphertext mirrors | rclone remotes listed in `TMX_VAULT_REMOTES` (Box, Dropbox, others) |
| Tool | `bash scripts/vault/vault.sh seal / open / mirror / verify` |

## Redundancy and restore checks

Configure `TMX_VAULT_REMOTES` with at least two distinct rclone destinations, for example `box:tmx-vault dropbox:tmx-vault`. Use separate providers or separately controlled accounts; two folders under one account provide location redundancy only.

- `mirror` requires at least two destinations and at least one `.age` artifact. It copies ciphertext and runs `rclone check --one-way` against each destination.
- `verify` downloads one encrypted artifact from every destination, compares ciphertext with the local copy, decrypts each restored copy with the active node key, and compares the plaintext outputs.
- Both commands fail closed when fewer than two destinations are configured. A successful check proves the configured destinations were reachable and the sampled artifact restored with the active key; it does not prove provider/account independence or independent key recovery.
- Current key custody is the node key plus the GitHub Actions secret `TMX_VAULT_AGE_KEY`. A second independently controlled recovery copy of the private key and a clean-device key-recovery drill remain required before grading key custody as redundant.

Run from the repository root:

```bash
TMX_VAULT_REMOTES="box:tmx-vault dropbox:tmx-vault" bash scripts/vault/vault.sh mirror
TMX_VAULT_REMOTES="box:tmx-vault dropbox:tmx-vault" bash scripts/vault/vault.sh verify
```

## Use in a workflow

```yaml
- uses: actions/checkout@v4
  with: { lfs: true }
- run: sudo apt-get install -y age
- run: bash scripts/vault/vault.sh open vault/example.age /tmp/example
  env: { TMX_VAULT_AGE_KEY: "${{ secrets.TMX_VAULT_AGE_KEY }}" }
```

## Rules
- Never commit plaintext session data; seal it.
- Refer to devices only by opaque IDs (`tmx-node-primary`, `tmx-node-55619bd5`).
- LFS objects in a public repo are downloadable by anyone; they are safe only because they are encrypted.
- Rotating the key: generate a new key, add its public line to `recipients.txt`, re-seal, update the secret, then remove the old line.
