# Encrypted vault lane

Private data (session archives, backups, large binaries) is **encrypted before it leaves the node** and only ciphertext is stored in this public repository or in external storage.

| Piece | Where |
|---|---|
| Public recipient (encrypt) | `ops/vault/recipients.txt` (age X25519) |
| Private key (decrypt) | Node: `~/.config/tmx-vault/age.key` (600). CI: secret `TMX_VAULT_AGE_KEY` (Actions + Codespaces) |
| Ciphertext in Git | `vault/**/*.age`, stored via Git LFS (`.gitattributes`) |
| Ciphertext mirrors | rclone remotes listed in `TMX_VAULT_REMOTES` (Box, Dropbox, others) |
| Tool | `scripts/vault/vault.sh seal / open / mirror` |

## Use in a workflow

```yaml
- uses: actions/checkout@v4
  with: { lfs: true }
- run: sudo apt-get install -y age
- run: scripts/vault/vault.sh open vault/example.age /tmp/example
  env: { TMX_VAULT_AGE_KEY: "${{ secrets.TMX_VAULT_AGE_KEY }}" }
```

## Rules
- Never commit plaintext session data; seal it.
- Refer to devices only by opaque IDs (`tmx-node-primary`, `tmx-node-55619bd5`).
- LFS objects in a public repo are downloadable by anyone; they are safe only because they are encrypted.
- Rotating the key: generate a new key, add its public line to `recipients.txt`, re-seal, update the secret, then remove the old line.
