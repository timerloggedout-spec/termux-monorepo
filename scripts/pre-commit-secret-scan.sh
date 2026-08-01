#!/usr/bin/env bash
set -euo pipefail

echo "Running staged credential scan..."
violations=0

while IFS= read -r -d '' path; do
  if git show ":$path" 2>/dev/null | grep -I -q -E \
    'gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|Bearer[[:space:]]+[A-Za-z0-9._~+/=-]{12,}|-----BEGIN [A-Z ]*PRIVATE KEY-----'; then
    printf 'Suspicious credential-shaped value in staged file: %s\n' "$path" >&2
    violations=1
  fi
done < <(git diff --cached --name-only --diff-filter=ACMR -z)

if (( violations )); then
  echo "Commit blocked. Remove or rotate the credential before committing." >&2
  exit 1
fi
exit 0
