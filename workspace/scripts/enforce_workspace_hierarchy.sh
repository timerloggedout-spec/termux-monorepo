#!/bin/bash
# enforce_workspace_hierarchy.sh – ensure every project has a workspace,
# move caveman tools into them, and set up cross-project symlinks.
set -e
echo "=== Enforcing Caveman Workspace Hierarchy ==="
# Root workspace (ecosystem-level)
mkdir -p ~/workspace/scripts
# Project workspaces
PROJECTS=(deepcli deepcli-tui deepseek-cli cli-synthegration termux-multi-agent synthegration-cli harmonizer-prod_cli chronos_checkout)
for proj in "${PROJECTS[@]}"; do
    mkdir -p ~/"$proj"/workspace
    echo "  ✅ $proj/workspace"
done
# Move existing tools to their correct workspaces (idempotent)
echo "  Placing map & bloat tools → cli-synthegration/workspace/caveman_map"
mkdir -p ~/cli-synthegration/workspace/caveman_map
[ -f ~/map_final_with_watch.sh ] && mv ~/map_final_with_watch.sh ~/cli-synthegration/workspace/caveman_map/
[ -f ~/discover_bloat.sh ] && mv ~/discover_bloat.sh ~/cli-synthegration/workspace/caveman_map/
[ -f ~/bloat_exclusions.lst ] && mv ~/bloat_exclusions.lst ~/cli-synthegration/workspace/caveman_map/
echo "  Placing dedup script → deepseek-cli/workspace"
[ -f ~/dedup_react_helper.py ] && mv ~/dedup_react_helper.py ~/deepseek-cli/workspace/
echo "  Placing time correlation assets → cli-synthegration/workspace"
[ -f ~/caveman_time_correlation/correlation_index.json ] && mv ~/caveman_time_correlation/correlation_index.json ~/cli-synthegration/workspace/
[ -f ~/build_correlation.py ] && mv ~/build_correlation.py ~/cli-synthegration/workspace/
# Symlink for convenience
ln -sf ~/workspace/scripts/enforce_workspace_hierarchy.sh ~/enforce_hierarchy.sh
echo "=== Hierarchy enforced. Tools graduated. ==="
