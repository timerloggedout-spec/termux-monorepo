#!/usr/bin/env bash
set -euo pipefail

scanner="$(dirname "$0")/../scripts/pre-commit-secret-scan.sh"
repo="$(mktemp -d)"
trap 'rm -rf "$repo"' EXIT
git -C "$repo" init -q
git -C "$repo" config user.email test@example.invalid
git -C "$repo" config user.name scanner-test
cp "$scanner" "$repo/scanner.sh"
chmod +x "$repo/scanner.sh"
printf '%s\n' '# Security tokens and credentials are never committed.' > "$repo/AGENTS.md"
git -C "$repo" add AGENTS.md
if ! (cd "$repo" && ./scanner.sh); then
  echo "Documentation-only staged content must pass the credential scan" >&2
  exit 1
fi
