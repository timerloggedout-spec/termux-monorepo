#!/data/data/com.termux/files/usr/bin/env bash
# agentic-auth-heartbeat.sh — prove the device's gh/git agentic auth can write.
#
# Non-destructive by design (repo is also the origin-device backup):
#   - never resets, checks out, stashes, or rewrites any branch or working tree
#   - builds a commit object from HEAD's existing tree with `git commit-tree`
#     and force-pushes it only to the custom ref refs/heartbeat/agentic-auth
#     (not a branch or tag: triggers no workflows, shows in no branch list)
# Read by .github/workflows/agentic-auth-canary.yml.
#
# Usage: scripts/termux/agentic-auth-heartbeat.sh [--dry-run]
# Cron/boot: run hourly, e.g. from termux-job-scheduler or ~/.termux/boot.
set -euo pipefail

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1
REPO_DIR="${TERMUX_MONOREPO_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || echo "$HOME/termux-monorepo")}"
REMOTE="${HEARTBEAT_REMOTE:-origin}"
REF="refs/heartbeat/agentic-auth"
cd "$REPO_DIR"

# Opaque device id (schema v3, PR #1245). Never derived from hardware/software fingerprints.
DEVICE_ID="${TMX_DEVICE_ID:-}"
if [ -z "$DEVICE_ID" ] && [ -f "$HOME/.config/termux-monorepo/device_id" ]; then
  DEVICE_ID="$(tr -d '[:space:]' < "$HOME/.config/termux-monorepo/device_id")"
fi
DEVICE_ID="${DEVICE_ID:-tmx-node-primary}"

ok()   { printf '[ok]   %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; FAILED=1; }
FAILED=0

GH_LOGIN=""
if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then ok "gh auth status"; else fail "gh auth status"; fi
  GH_LOGIN="$(gh api user -q .login 2>/dev/null || true)"
  [ -n "$GH_LOGIN" ] && ok "gh api user ($GH_LOGIN)" || fail "gh api user"
else
  fail "gh not installed"
fi

if git ls-remote --exit-code "$REMOTE" HEAD >/dev/null 2>&1; then ok "git ls-remote $REMOTE"; else fail "git ls-remote $REMOTE"; fi

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
CHECKS="$([ "$FAILED" = 0 ] && echo pass || echo fail)"
MSG="$(printf 'heartbeat: agentic-auth %s\n\n{"device_id":"%s","gh_login":"%s","checks":"%s","at":"%s"}\n' \
  "$TS" "$DEVICE_ID" "$GH_LOGIN" "$CHECKS" "$TS")"
TREE="$(git rev-parse 'HEAD^{tree}')"
COMMIT="$(printf '%s' "$MSG" | git commit-tree "$TREE" -p HEAD)"

if [ "$DRY_RUN" = 1 ]; then
  git push --dry-run --force "$REMOTE" "$COMMIT:$REF" && ok "push --dry-run $REF" || fail "push --dry-run $REF"
else
  git push --force --quiet "$REMOTE" "$COMMIT:$REF" && ok "pushed $REF ($COMMIT)" || fail "push $REF"
fi

exit "$FAILED"
