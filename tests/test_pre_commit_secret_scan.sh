#!/usr/bin/env bash
set -euo pipefail

scanner="$(dirname "$0")/../scripts/pre-commit-secret-scan.sh"
chmod +x "$scanner"

git add AGENTS.md
if ! "$scanner"; then
  echo "Documentation-only staged content must pass the credential scan" >&2
  exit 1
fi
git reset -- AGENTS.md >/dev/null
