#!/usr/bin/env bash
# Encrypted storage lane: age-encrypt locally, store ciphertext in Git LFS and/or rclone remotes.
# Decryption key: $TMX_VAULT_AGE_KEY (Actions/Codespaces secret) or ~/.config/tmx-vault/age.key on the node.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
RECIP="$ROOT/ops/vault/recipients.txt"
VAULT="$ROOT/vault"
keyfile() {
  if [ -n "${TMX_VAULT_AGE_KEY:-}" ]; then
    local t; t="$(mktemp)"; chmod 600 "$t"; printf '%s\n' "$TMX_VAULT_AGE_KEY" > "$t"; echo "$t"
  elif [ -f "$HOME/.config/tmx-vault/age.key" ]; then echo "$HOME/.config/tmx-vault/age.key"
  else echo "no decryption key (set TMX_VAULT_AGE_KEY)" >&2; exit 2; fi
}
case "${1:-}" in
  seal)   # seal <src> [name]  -> vault/<name>.age  (plaintext never written to the repo)
    src="$2"; name="${3:-$(basename "$src")}"; mkdir -p "$VAULT"
    if [ -d "$src" ]; then tar -C "$(dirname "$src")" -cf - "$(basename "$src")" | zstd -q -19 -T0 | age -R "$RECIP" -o "$VAULT/$name.tar.zst.age"; echo "$VAULT/$name.tar.zst.age"
    else age -R "$RECIP" -o "$VAULT/$name.age" "$src"; echo "$VAULT/$name.age"; fi ;;
  open)   # open <file.age> [out]
    k="$(keyfile)"; out="${3:-${2%.age}}"; age -d -i "$k" -o "$out" "$2"; [ "$k" != "$HOME/.config/tmx-vault/age.key" ] && rm -f "$k"; echo "$out" ;;
  mirror) # mirror -> copies vault/ ciphertext to each rclone remote in $TMX_VAULT_REMOTES (e.g. "box:tmx-vault dropbox:tmx-vault")
    for r in ${TMX_VAULT_REMOTES:-}; do rclone copy "$VAULT" "$r" --exclude ".gitkeep"; echo "mirrored -> $r"; done ;;
  *) echo "usage: vault.sh seal <src> [name] | open <file.age> [out] | mirror"; exit 1 ;;
esac
