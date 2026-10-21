#!/data/data/com.termux/files/usr/bin/env bash
# Agentic-auth heartbeat for the gh/git CLI path DeepAgent and the operator use
# to push and open PRs from Termux. Read-only by default.
#
#   check-gh-agentic-auth.sh            # print JSON status, exit 0 ok / 1 degraded
#   check-gh-agentic-auth.sh --publish  # also write ops/agentic-auth/heartbeat.json
#                                       # to branch ops/agentic-auth-heartbeat via gh api
#
# Never prints tokens. Never runs destructive git commands (no reset/clean/force).
set -uo pipefail
REPO="${AGENTIC_AUTH_REPO:-timerloggedout-spec/termux-monorepo}"
BRANCH="${AGENTIC_AUTH_BRANCH:-ops/agentic-auth-heartbeat}"
DEVICE_ID="${DEVICE_ID:-$(cat "$HOME/.config/termux-monorepo/device_id" 2>/dev/null || echo unknown)}"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ok=true; checks=()

add() { checks+=("{\"name\":\"$1\",\"ok\":$2,\"detail\":\"$(printf '%s' "$3" | tr -d '"\\' | head -c 200)\"}"); [ "$2" = true ] || ok=false; }

if command -v gh >/dev/null 2>&1; then
  if gh auth status -h github.com >/dev/null 2>&1; then
    user="$(gh api user --jq .login 2>/dev/null || echo '?')"
    add gh_auth true "authenticated as $user"
    scopes="$(gh api -i user 2>/dev/null | tr -d '\r' | awk -F': ' 'tolower($1)=="x-oauth-scopes"{print $2}')"
    add gh_scopes true "${scopes:-fine-grained or app token}"
    perm="$(gh api "repos/$REPO" --jq '.permissions.push' 2>/dev/null || echo false)"
    [ "$perm" = true ] && add repo_push_permission true "push allowed on $REPO" || add repo_push_permission false "no push permission on $REPO"
  else
    add gh_auth false "gh auth status failed"
  fi
else
  add gh_installed false "gh not installed"
fi

if git ls-remote "https://github.com/$REPO.git" HEAD >/dev/null 2>&1; then
  add git_ls_remote true "remote reachable"
else
  add git_ls_remote false "git ls-remote failed"
fi

root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$root" ]; then
  if git -C "$root" push --dry-run --porcelain origin "HEAD:refs/heads/canary/agentic-auth-dry-run" >/dev/null 2>&1; then
    add git_push_dry_run true "dry-run push accepted"
  else
    add git_push_dry_run false "dry-run push rejected (credential helper or permission)"
  fi
fi

json="{\"schema_version\":\"agentic-auth.heartbeat.v1\",\"observed_at\":\"$now\",\"device_id\":\"$DEVICE_ID\",\"repo\":\"$REPO\",\"status\":\"$([ "$ok" = true ] && echo ok || echo degraded)\",\"checks\":[$(IFS=,; echo "${checks[*]}")]}"
printf '%s\n' "$json"

if [ "${1:-}" = "--publish" ]; then
  if ! gh api "repos/$REPO/branches/$BRANCH" >/dev/null 2>&1; then
    base="$(gh api "repos/$REPO/git/ref/heads/master" --jq .object.sha)"
    gh api -X POST "repos/$REPO/git/refs" -f ref="refs/heads/$BRANCH" -f sha="$base" >/dev/null
  fi
  path="ops/agentic-auth/heartbeat.json"
  sha="$(gh api "repos/$REPO/contents/$path?ref=$BRANCH" --jq .sha 2>/dev/null || true)"
  args=(-X PUT "repos/$REPO/contents/$path" -f message="chore(agentic-auth): heartbeat $now" -f branch="$BRANCH" -f content="$(printf '%s\n' "$json" | base64 | tr -d '\n')")
  [ -n "$sha" ] && args+=(-f sha="$sha")
  gh api "${args[@]}" >/dev/null && echo "published heartbeat to $BRANCH" >&2 || { echo "publish failed" >&2; exit 2; }
fi
[ "$ok" = true ]
