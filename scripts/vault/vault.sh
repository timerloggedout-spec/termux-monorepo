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
  mirror) # mirror -> requires >=2 distinct configured rclone destinations and verifies each copy
    read -r -a remotes <<< "${TMX_VAULT_REMOTES:-}"
    if (( ${#remotes[@]} < 2 )); then
      echo "mirror requires at least two configured rclone destinations in TMX_VAULT_REMOTES" >&2
      exit 3
    fi
    if [ ! -d "$VAULT" ] || [ -z "$(find "$VAULT" -type f -name '*.age' -print -quit)" ]; then
      echo "mirror requires at least one encrypted .age artifact in $VAULT" >&2
      exit 4
    fi
    declare -A seen=()
    for r in "${remotes[@]}"; do
      if [[ -n "${seen[$r]:-}" ]]; then
        echo "duplicate vault destination: $r" >&2
        exit 5
      fi
      seen["$r"]=1
      rclone mkdir "$r"
      rclone copy "$VAULT" "$r" --exclude ".gitkeep"
      rclone check "$VAULT" "$r" --one-way --exclude ".gitkeep"
      printf 'verified ciphertext mirror -> %s\\n' "$r"
    done ;;
  verify) # verify one encrypted artifact can be restored and decrypted from every configured remote
    read -r -a remotes <<< "${TMX_VAULT_REMOTES:-}"
    if (( ${#remotes[@]} < 2 )); then
      echo "verify requires at least two configured rclone destinations in TMX_VAULT_REMOTES" >&2
      exit 3
    fi
    artifact="$(find "$VAULT" -type f -name '*.age' -print -quit 2>/dev/null || true)"
    if [ -z "$artifact" ]; then
      echo "verify requires at least one encrypted .age artifact in $VAULT" >&2
      exit 4
    fi
    k="$(keyfile)"
    tmp="$(mktemp -d)"
    cleanup() {
      rm -rf "$tmp"
      [ "$k" = "$HOME/.config/tmx-vault/age.key" ] || rm -f "$k"
    }
    trap cleanup EXIT
    age -d -i "$k" -o "$tmp/local.plain" "$artifact"
    rel="${artifact#"$VAULT"/}"
    declare -A seen=()
    for r in "${remotes[@]}"; do
      if [[ -n "${seen[$r]:-}" ]]; then
        echo "duplicate vault destination: $r" >&2
        exit 5
      fi
      seen["$r"]=1
      copy="$tmp/$(printf '%s' "$r" | tr '/:' '__').age"
      plain="$tmp/$(printf '%s' "$r" | tr '/:' '__').plain"
      rclone copyto "${r%/}/${rel}" "$copy"
      cmp -s "$artifact" "$copy" || { echo "ciphertext mismatch at $r" >&2; exit 6; }
      age -d -i "$k" -o "$plain" "$copy"
      cmp -s "$tmp/local.plain" "$plain" || { echo "plaintext mismatch after restore from $r" >&2; exit 7; }
      printf 'restore + decrypt verified <- %s\\n' "$r"
    done ;;
  *) echo "usage: vault.sh seal <src> [name] | open <file.age> [out] | mirror | verify"; exit 1 ;;
esac
