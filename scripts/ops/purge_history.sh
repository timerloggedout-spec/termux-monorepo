#!/usr/bin/env bash
# Termux-Monorepo Security History Remediation
# Excises Class 3/4 paths from all reachable git objects.
# WARNING: This rewrites history. Coordinated force-push required.

set -e

# Ensure we are in the repo root
cd "$(dirname "$0")/../.."

echo "--- Security History Remediation ---"
echo "Targeting Class 3/4 artifacts for total excision..."

# List of paths/patterns to excise
# Based on repo_gate.py and PR #3 lineage
PATHS=(
    ".deepcli/session_store/"
    ".pi/"
    ".synthegration/"
    "browser-data/"
    "Cookies"
    "Local State"
    "*.pi"
    "*.deepcli"
    "*.cedar"
    "*.cookie"
    "*.token"
    "**/Cookies"
    "**/Local State"
    "**/.deepcli/session_store/**"
)

# Build the filter-repo command
CMD="git filter-repo --force"
for p in "${PATHS[@]}"; do
    CMD="$CMD --path-glob '$p' --invert-paths"
done

echo "Executing: $CMD"
eval "$CMD"

echo "History remediation complete."
echo "NEXT STEPS:"
echo "1. Verify the tree is clean: git log --all --full-history -- <path>"
echo "2. Rotate all credentials found in the old history."
echo "3. Coordinate force-push to origin/master-staging."
