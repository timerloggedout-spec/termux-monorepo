#!/usr/bin/env bash
# Vercel Ignored Build Step helper.
# Exit 0 only when the current project has no relevant source changes.
# Any missing input, unknown project, or Git error fails open to a build.
set -u

PROJECT="${1:-}"
PREVIOUS="${VERCEL_GIT_PREVIOUS_SHA:-}"
CURRENT="${VERCEL_GIT_COMMIT_SHA:-}"

if [[ -z "$PROJECT" || -z "$PREVIOUS" || -z "$CURRENT" ]]; then
  echo "[vercel-ignore] missing project or Git SHA; continue build"
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[vercel-ignore] cannot resolve repository root; continue build"
  exit 1
}

case "$PROJECT" in
  mcp-hub)
    PATHS=(':(top)mcp-hub/')
    ;;
  help-wanted-dashboard)
    PATHS=(
      ':(top)apps/help-wanted-dashboard/'
      ':(top)docs/ops/generated/help-wanted-status.json'
      ':(top)docs/ops/generated/lane-matrix-status.json'
      ':(top)scripts/ci/help_wanted_status.py'
      ':(top)scripts/ci/verify_help_wanted_dashboard.py'
    )
    ;;
  demo-portal)
    PATHS=(':(top)demo-portal/public/')
    ;;
  *)
    echo "[vercel-ignore] unknown project '$PROJECT'; continue build"
    exit 1
    ;;
esac

set +e
git -C "$ROOT" diff --quiet "$PREVIOUS" "$CURRENT" -- "${PATHS[@]}"
DIFF_RC=$?
set -e

if [[ "$DIFF_RC" -eq 0 ]]; then
  echo "[vercel-ignore] project=$PROJECT no relevant changes; skip deployment"
  exit 0
fi

if [[ "$DIFF_RC" -eq 1 ]]; then
  echo "[vercel-ignore] project=$PROJECT relevant changes found; build deployment"
  exit 1
fi

echo "[vercel-ignore] project=$PROJECT git diff failed (rc=$DIFF_RC); fail open to build"
exit 1
