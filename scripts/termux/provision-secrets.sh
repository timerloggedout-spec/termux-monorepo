#!/data/data/com.termux/files/usr/bin/env bash
# Provision GitHub Actions secrets from the Termux device with gh CLI.
# Values are read from a hidden prompt or termux-clipboard-get, piped straight
# into `gh secret set` on stdin, and never echoed, logged, or written to disk.
#
# Usage:
#   provision-secrets.sh status                 # which mapped secrets are set / missing per repo
#   provision-secrets.sh set [--clipboard] [--only NAME] [--repo OWNER/REPO] [--required-only]
#   provision-secrets.sh pause-forks            # gh workflow disable every active *.lock.yml in the forks (records list)
#   provision-secrets.sh resume-forks           # re-enable exactly what pause-forks disabled
#   provision-secrets.sh rerun                  # re-run latest failed run of each affected workflow
#
# Map (names only): docs/ops/secrets-provisioning-map.md
set -uo pipefail
OWNER=timerloggedout-spec
STATE="${XDG_STATE_HOME:-$HOME/.local/state}/termux-monorepo"
mkdir -p "$STATE"

# repo|secret|required|suggested #184 token (least privilege first)|purpose
MAP=$(cat <<'M'
gh-aw-mcpg_fork|CROSS_REPO_PAT|yes|NEW fine-grained (Issues RW on gh-aw-mcpg_fork + target repos); fallback gitlab_cicd (classic, repo)|Gateway Issue Dispatcher: "Input required and not supplied: github-token"
gh-aw-mcpg_fork|GH_AW_GITHUB_TOKEN|yes|ARCHWIZ_GITHUB_TOKEN (fine-grained) if it covers the fork; fallback gitlab_cicd|all 29 scheduled agentic workflows (safe outputs)
gh-aw-mcpg_fork|GH_AW_GITHUB_MCP_SERVER_TOKEN|yes|NEW fine-grained read-only (Contents/Issues/PRs/Actions read); fallback gitlab_cicd-w+org_view|GitHub MCP server inside agent jobs
gh-aw-mcpg_fork|GH_AW_CI_TRIGGER_TOKEN|no|NEW fine-grained (Contents RW); fallback gitlab_cicd|7 workflows that push and must trigger CI
gh-aw_fork|GH_AW_GITHUB_TOKEN|yes|ARCHWIZ_GITHUB_TOKEN (fine-grained) if it covers the fork; fallback gitlab_cicd|all 239 scheduled agentic workflows
gh-aw_fork|GH_AW_GITHUB_MCP_SERVER_TOKEN|yes|NEW fine-grained read-only; fallback gitlab_cicd-w+org_view|GitHub MCP server inside agent jobs
gh-aw_fork|COPILOT_GITHUB_TOKEN|yes|NEW fine-grained with "Copilot Requests" permission (no #184 token fits; do not use admin classics)|153 Copilot-engine workflows
gh-aw_fork|GH_AW_CI_TRIGGER_TOKEN|no|NEW fine-grained (Contents RW); fallback gitlab_cicd|56 workflows that push and must trigger CI
gh-aw_fork|GH_AW_AGENT_TOKEN|no|NEW fine-grained (Issues/PRs RW, Actions RW)|13 workflows that assign the Copilot coding agent
gh-aw_fork|ANTHROPIC_API_KEY|no|provider key (not a GitHub token)|49 Claude-engine workflows
gh-aw_fork|OPENAI_API_KEY|no|provider key (not a GitHub token)|59 Codex-engine workflows
gh-aw_fork|CODEX_API_KEY|no|provider key; same value as OPENAI_API_KEY|58 Codex-engine workflows
termux-monorepo|OPERATOR_GITHUB_TOKEN|yes|ARCHWIZ_GITHUB_TOKEN (fine-grained, termux-monorepo: Contents/Issues/PRs/Actions/Workflows RW)|23 workflows (preferred operator token)
termux-monorepo|OPERATOR_TOKEN|no|same value as OPERATOR_GITHUB_TOKEN|22 workflows (legacy name)
termux-monorepo|ARCHWIZ_GITHUB_TOKEN|no|ARCHWIZ_GITHUB_TOKEN (fine-grained)|22 workflows (fallback chain)
termux-monorepo|GH_PAT|no|NEW fine-grained (Contents RW on timerloggedout-spec.github.io)|help-wanted-dashboard-deploy mirror
termux-monorepo|CODESPACE_CREATE_TOKEN|no|NEW fine-grained (Codespaces RW); fallback none of #184 without admin scopes|codespace-create / codespace-start
termux-monorepo|RECON_INTEL_GITHUB_WRITE_TOKEN|no|NEW fine-grained (Issues RW)|recon-intel-reconcile
termux-monorepo|REPOSITORY_OBSERVATORY_TOKEN|no|gitlab_cicd-w+org_view (read:org, repo) or NEW fine-grained read-only|repository-observatory
termux-monorepo|DEEPSEEK_API_KEY|no|DeepSeek platform API key (NOT the GitHub classic PAT also named DEEPSEEK_API_KEY)|deepseek-ci
termux-monorepo|LINEAR_API_KEY|no|Linear API key|agent-feedback-linear-sync, context-relationship-linear-freshness
termux-monorepo|JULES_API_KEY|no|Jules API key|agent-jules-on-issues, agent-review-auto-jules
M
)

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1" >&2; exit 1; }; }
need gh

existing() { gh secret list -R "$OWNER/$1" --json name --jq '.[].name' 2>/dev/null; }

cmd_status() {
  local last="" have=""
  while IFS='|' read -r repo name req hint purpose; do
    [ -z "$repo" ] && continue
    if [ "$repo" != "$last" ]; then have="$(existing "$repo")"; last="$repo"; echo "== $OWNER/$repo"; fi
    if grep -qx "$name" <<<"$have"; then s="set    "; else s="MISSING"; fi
    printf '  %s %-32s required=%-3s  %s\n' "$s" "$name" "$req" "$purpose"
  done <<<"$MAP"
}

read_value() {  # prints value on stdout only into a pipe; never to the terminal
  local v=""
  if [ "$CLIP" = 1 ]; then need termux-clipboard-get; v="$(termux-clipboard-get)"
  else IFS= read -rs v </dev/tty; echo >/dev/tty; fi
  printf '%s' "$v"
}

cmd_set() {
  local last="" have=""
  while IFS='|' read -r repo name req hint purpose; do
    [ -z "$repo" ] && continue
    [ -n "$ONLY" ] && [ "$name" != "$ONLY" ] && continue
    [ -n "$REPO" ] && [ "$OWNER/$repo" != "$REPO" ] && continue
    [ "$REQ_ONLY" = 1 ] && [ "$req" != yes ] && continue
    if [ "$repo" != "$last" ]; then have="$(existing "$repo")"; last="$repo"; fi
    echo >/dev/tty
    echo "[$OWNER/$repo] $name  ($purpose)" >/dev/tty
    echo "  use: $hint" >/dev/tty
    grep -qx "$name" <<<"$have" && echo "  (already set; entering a value overwrites it)" >/dev/tty
    if [ "$CLIP" = 1 ]; then printf '  copy the value, then press Enter (s = skip): ' >/dev/tty
    else printf '  paste value, then Enter (empty = skip): ' >/dev/tty; fi
    if [ "$CLIP" = 1 ]; then IFS= read -r ans </dev/tty; [ "$ans" = s ] && continue; fi
    val="$(read_value)"
    if [ -z "$val" ]; then echo "  skipped" >/dev/tty; unset val; continue; fi
    if printf '%s' "$val" | gh secret set "$name" -R "$OWNER/$repo" >/dev/null 2>&1; then
      echo "  ✓ set" >/dev/tty
    else
      echo "  ✗ gh secret set failed (check gh auth scopes: repo + admin rights on $repo)" >/dev/tty
    fi
    unset val
    [ "$CLIP" = 1 ] && command -v termux-clipboard-set >/dev/null && termux-clipboard-set "" 2>/dev/null
  done <<<"$MAP"
}

cmd_pause() {
  for repo in gh-aw_fork gh-aw-mcpg_fork; do
    f="$STATE/paused-$repo.txt"; : >"$f"
    gh workflow list -R "$OWNER/$repo" --all --json path,state --jq '.[] | select(.state=="active") | .path' \
      | grep '\.lock\.yml$' | while read -r p; do
        w="$(basename "$p")"
        gh workflow disable "$w" -R "$OWNER/$repo" >/dev/null 2>&1 && echo "$w" >>"$f"
      done
    echo "$repo: disabled $(wc -l <"$f") workflows (list: $f)"
  done
}

cmd_resume() {
  for repo in gh-aw_fork gh-aw-mcpg_fork; do
    f="$STATE/paused-$repo.txt"; [ -s "$f" ] || { echo "$repo: nothing recorded"; continue; }
    n=0; while read -r w; do gh workflow enable "$w" -R "$OWNER/$repo" >/dev/null 2>&1 && n=$((n+1)); done <"$f"
    echo "$repo: re-enabled $n workflows"
  done
}

cmd_rerun() {
  for pair in "gh-aw-mcpg_fork:gateway-issue-dispatcher.lock.yml" "gh-aw_fork:contribution-check.lock.yml" "gh-aw_fork:aw-failure-investigator.lock.yml" \
              "termux-monorepo:help-wanted-dashboard-deploy.yml"; do
    repo="${pair%%:*}"; wf="${pair#*:}"
    gh workflow enable "$wf" -R "$OWNER/$repo" >/dev/null 2>&1 || true
    gh workflow run "$wf" -R "$OWNER/$repo" >/dev/null 2>&1 && echo "dispatched $repo/$wf" || echo "could not dispatch $repo/$wf"
  done
}

CLIP=0; ONLY=""; REPO=""; REQ_ONLY=0
sub="${1:-status}"; shift || true
while [ $# -gt 0 ]; do case "$1" in
  --clipboard) CLIP=1 ;; --only) ONLY="$2"; shift ;; --repo) REPO="$2"; shift ;; --required-only) REQ_ONLY=1 ;;
  *) echo "unknown arg $1" >&2; exit 2 ;; esac; shift; done
case "$sub" in
  status) cmd_status ;; set) cmd_set ;; pause-forks) cmd_pause ;; resume-forks) cmd_resume ;; rerun) cmd_rerun ;;
  *) sed -n '2,14p' "$0"; exit 2 ;;
esac
