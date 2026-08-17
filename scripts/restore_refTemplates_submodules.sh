#!/usr/bin/env bash
# Restore submodules (metadata-only, depth-1) for the refTemplates skeleton
# Run from repository root. This script will add the submodules (shallow) and perform sparse-checkout inside them

set -euo pipefail

add_submodule() {
  local url="$1"; shift
  local path="$1"; shift
  echo "Adding submodule: $path <- $url"
  git submodule add --depth 1 "$url" "$path"
  # Attempt to keep only metadata and README.md via sparse-checkout if supported
  if [ -d "$path" ]; then
    pushd "$path" >/dev/null || return
    git sparse-checkout init --cone || true
    # Keep README.md and any metadata/ directory if present
    git sparse-checkout set README.md metadata || true
    popd >/dev/null || return
  fi
}

# Preferred forks (already created in user account when available)
add_submodule https://github.com/timerloggedout-spec/hermes-agent_fork refTemplates/01_Agent_Runtime/hermes-agent
add_submodule https://github.com/timerloggedout-spec/Interpreted-Context-Methdology_fork refTemplates/Interpreted-Context-Methdology_fork
add_submodule https://github.com/timerloggedout-spec/lazycodex_fork refTemplates/12_External_Agents/lazycodex
add_submodule https://github.com/timerloggedout-spec/ChapitoAI_fork refTemplates/13_Third_Party_Refs/ChapitoAI-main
add_submodule https://github.com/timerloggedout-spec/deepterm_fork refTemplates/deepterm
add_submodule https://github.com/timerloggedout-spec/codex-termux_fork refTemplates/codex-termux
add_submodule https://github.com/timerloggedout-spec/deepcode-cli_fork refTemplates/deepcode-cli

# Note: For other refTemplates entries without a preferred fork in the account,
# see refTemplates/README_RECOVERY.md and individual SOURCE.txt files for search URLs

echo "Submodule add operations complete. Review changes and commit if satisfied."
