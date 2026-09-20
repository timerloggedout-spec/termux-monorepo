#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
if [[ -d refTemplates/smods/AuditEngine_fork/.git ]] || [[ -f refTemplates/smods/AuditEngine_fork/.git ]]; then
  git submodule update --init --depth 1 refTemplates/smods/AuditEngine_fork
  exit 0
fi
git submodule add --depth 1 -b main \
  https://github.com/timerloggedout-spec/AuditEngine_fork.git \
  refTemplates/smods/AuditEngine_fork
echo "Added AuditEngine_fork. Commit .gitmodules + gitlink after review."
