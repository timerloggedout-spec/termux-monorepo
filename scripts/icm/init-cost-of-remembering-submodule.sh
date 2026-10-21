#!/usr/bin/env bash
# One-shot: finish the cost-of-remembering_fork gitlink after .gitmodules is present.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

if [[ -d refTemplates/smods/cost-of-remembering_fork/.git ]] || [[ -f refTemplates/smods/cost-of-remembering_fork/.git ]]; then
  echo "already present"
  git submodule update --init --depth 1 refTemplates/smods/cost-of-remembering_fork
  exit 0
fi

git submodule add --depth 1 -b main \
  https://github.com/timerloggedout-spec/cost-of-remembering_fork.git \
  refTemplates/smods/cost-of-remembering_fork

echo "Submodule added. Review, then:"
echo "  git add .gitmodules refTemplates/smods/cost-of-remembering_fork"
echo "  git commit -m 'chore(submodule): pin cost-of-remembering_fork'"
