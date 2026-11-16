#!/bin/bash
# Cleanup script for duplicate iOS-Termux PRs and branches
# Run this with: bash scripts/cleanup-ios-termux-duplicates.sh

set -euo pipefail

# Requires gh CLI and authenticated GitHub token
# Make sure you have write access to both:
# - credkellar/iOS-Termux (to close PRs)
# - timerloggedout-spec/iOS-Termux_fork (to delete branches)

echo "=== iOS-Termux Duplicate Cleanup Script ==="
echo ""

# Configuration
TARGET_REPO="credkellar/iOS-Termux"
FORK_REPO="timerloggedout-spec/iOS-Termux_fork"
PR_TITLE="Enhance translations: add 22 new command pairs and 4 new path mappings"
KEEP_PR="2"  # Keep PR #2, close PR #1

echo "Target Repository: $TARGET_REPO"
echo "Fork Repository: $FORK_REPO"
echo "Keeping PR: #$KEEP_PR"
echo ""

# Step 1: List all open PRs with matching title
echo "Step 1: Finding duplicate PRs..."
PRS=$(gh api "repos/$TARGET_REPO/pulls?state=open" | jq -r ".[] | select(.title == \"$PR_TITLE\") | .number")
echo "Found PRs: $PRS"
echo ""

# Step 2: Close all duplicate PRs except the one we want to keep
echo "Step 2: Closing duplicate PRs..."
for pr_num in $PRS; do
    if [ "$pr_num" != "$KEEP_PR" ]; then
        echo "  Closing PR #$pr_num..."
        gh api -X PATCH "repos/$TARGET_REPO/pulls/$pr_num" \
            -f state="closed" \
            -f "title=$(gh api repos/$TARGET_REPO/pulls/$pr_num | jq -r .title)" 2>/dev/null || \
            echo "    Failed to close PR #$pr_num (may need manual cleanup)"
    else
        echo "  Keeping PR #$pr_num"
    fi
done
echo ""

# Step 3: List all contribution branches in fork
echo "Step 3: Finding duplicate branches in fork..."
BRANCHES=$(gh api "repos/$FORK_REPO/branches" | jq -r ".[] | select(.name | startswith(\"contribution-enhancements\")) | .name")
echo "Found branches:"
echo "$BRANCHES"
echo ""

# Step 4: Delete all contribution branches (they will be recreated by workflow)
echo "Step 4: Deleting duplicate branches from fork..."
for branch in $BRANCHES; do
    echo "  Deleting branch: $branch..."
    gh api -X DELETE "repos/$FORK_REPO/git/refs/heads/$branch" 2>/dev/null || \
        echo "    Failed to delete branch $branch (may need manual cleanup)"
done
echo ""

# Step 5: Verify cleanup
echo "Step 5: Verifying cleanup..."
echo "  Remaining open PRs:"
gh api "repos/$TARGET_REPO/pulls?state=open" | jq -r ".[] | select(.title == \"$PR_TITLE\") | \"  PR #\(.number): \(.state)\"" 2>/dev/null || echo "    None found"

echo "  Remaining contribution branches:"
gh api "repos/$FORK_REPO/branches" | jq -r ".[] | select(.name | startswith(\"contribution-enhancements\")) | \"  - \(.name)\"" 2>/dev/null || echo "    None found"

echo ""
echo "=== Cleanup Complete ==="
echo "Kept: PR #$KEEP_PR in $TARGET_REPO"
echo "All duplicate branches deleted from $FORK_REPO"
