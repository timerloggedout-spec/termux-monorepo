# ArchWiz sentinel: route must remain a function, never an alias
typeset -g ARCHWIZ_ROUTE_GUARD=1
# Enable comments (fixes zsh 'unknown file attribute: h' warnings)
setopt INTERACTIVE_COMMENTS

# Powerlevel10k instant prompt
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Load Powerlevel10k
source ~/powerlevel10k/powerlevel10k.zsh-theme

# Custom ecosystem segment
function prompt_ecosystem() {
  bash ~/workspace/llm_map/ecosystem_prompt.sh
}
POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(ecosystem)

# Aliases
alias tui="cd ~/deepcli-tui && python3 tui.py"
alias forensic-query="$HOME/harmony_hub/utility_belt/forensic-query"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
alias task-list="python3 ~/workspace/llm_map/agent_shell.py list"
alias workflow="bash ~/harmony_hub/utility_belt/workflow"
alias dispatch-adaptive="bash ~/workspace/llm_map/dispatch_adaptive.sh"
alias truth-report="python3 ~/workspace/llm_map/generate_diff_report.py"
alias logged="python3 ~/workspace/llm_map/tool_logger.py"
alias dispatch-parallel="bash ~/workspace/llm_map/dispatch_parallel.sh"
setopt EXTENDED_HISTORY
alias workspace-check="bash ~/harmony_hub/utility_belt/workspace-check"
alias account-activity="bash ~/harmony_hub/utility_belt/account-activity"
[ -n "$BASH_VERSION" ] && source ~/.bashrc
alias fts-query="bash ~/harmony_hub/utility_belt/fts-query"
route() { python3 ~/workspace/llm_map/router_agent.py "$@"; }

# ── 4_51GH7 Ecosystem Aliases ─────────────────────
alias archwiz='~/archwiz/archwiz.sh'

# fix Powerlevel10k instant prompt warning
typeset -g POWERLEVEL9K_INSTANT_PROMPT=quiet
# ── Recovered ArchWiz aliases (from archaeologist recovery) ──
alias map='mmap'
alias mupdate='python3 ~/workspace/llm_map/llm_mapper_pro.py update'
alias mfull='python3 ~/workspace/llm_map/llm_mapper_pro.py full-scan'
alias mmap='python3 ~/workspace/llm_map/llm_mapper_pro.py generate-map'
alias mtree='python3 ~/workspace/llm_map/llm_mapper_pro.py graph-tree'
alias mdot='python3 ~/workspace/llm_map/llm_mapper_pro.py graph-dot'
alias mkprofile='python3 ~/workspace/llm_map/llm_mapper_pro.py profile-create'
alias map-func='python3 ~/workspace/llm_map/func_indexer.py'
alias map-graph='bash ~/workspace/llm_map/graph_fzf.sh'
alias map-set='export LLM_PROFILE=$1 && echo "Profile set to $LLM_PROFILE"'
alias funcfind='function _ff(){ jq -r "select(.file | test(\"$1\")) | \"\(.name) \t line \(.line) \t \(.sig[:60])\"" ~/workspace/llm_map/func_index.jsonl; }; _ff'
alias dep='bash ~/workspace/llm_map/depgraph.sh'
alias depmenu='bash ~/workspace/llm_map/depmenu.sh'
alias dispatch='python3 ~/workspace/llm_map/dispatch_task.py'
alias promote='python3 ~/workspace/llm_map/promote.py'
alias oracle='python3 ~/workspace/llm_map/impact_oracle.py'
alias fore='python3 ~/workspace/llm_map/foresight_collect.py'
alias archaeo='python3 ~/workspace/llm_map/archaeologist.py'
alias agent-shell='python3 ~/workspace/llm_map/agent_shell.py'
alias task-watch='bash ~/workspace/llm_map/task_watcher.sh'
alias map-query='bash ~/harmony_hub/utility_belt/map-query.sh 2>/dev/null || echo "map-query not yet built"'
alias deepcli="python3 ~/workspace/llm_map/deepcli_send.py"

# opencode
export PATH=/data/data/com.termux/files/home/.opencode/bin:$PATH
alias aether="python3 ~/archwiz/aether.py"
alias aether="python3 ~/archwiz/aether.py"
alias taxapply='python3 ~/workspace/llm_map/_TOOL_TAXONOMY/modules/taxapply.py'
alias taxtool='bash ~/workspace/llm_map/_TOOL_TAXONOMY/build_tool_taxonomy.sh'
alias taxrefactor='python3 ~/workspace/llm_map/_TOOL_TAXONOMY/modules/post_refactor.py'
alias taxdiff='python3 ~/workspace/llm_map/_TOOL_TAXONOMY/modules/taxdiff.py'
export PYTHONPATH="$HOME/colab-cli/lib:$PYTHONPATH"
alias map-build='cd ~/workspace/llm_map && python3 build_final_all_profile.py'
alias oracle2='python3 ~/archwiz/oracle_v2.py'
alias oracle2="python3 ~/archwiz/oracle_v2.py"
alias block-verdicts='python3 ~/archwiz/block_verdicts.py'
export PATH=/data/data/com.termux/files/home/.local/bin:$PATH
export PATH="$HOME/.local/bin:$PATH"
alias coderabbit="grun ~/.local/bin/coderabbit"
alias da='~/.local/bin/deepagent-cli'
alias da-dry='~/.local/bin/deepagent-cli --dry-run'
alias da-fresh='~/.local/bin/deepagent-cli --fresh'
alias da-task='~/.local/bin/deepagent-cli --task-file'

# ── Safe command hygiene (Session 143)
rm()  { echo "REFUSED: use rm-safe --confirm for local, git-rm-safe for tracked"; return 1; }
alias gtrm='~/.local/bin/git-rm-safe'

# ── Session 143 · anti-sweep stash guard
git() {
  if [ "${1:-}" = "stash" ]; then
    shift
    command ~/.local/bin/git-stash-safe "$@"
  else
    command git "$@"
  fi
}

# ── gh-status integration (Session 143)
# Auto-check GitHub status when `gh` or `git push/fetch` fails.
_gh_fail_hook() {
  local _rc=$?
  if [ "$_rc" -ne 0 ]; then
    printf '\n[gh-status] command failed — checking githubstatus.com\n' >&2
    ~/.local/bin/gh-status check 2>&1 | head -2 >&2
  fi
  return "$_rc"
}
# Wrap gh (function; guard against re-wrap)
if ! typeset -f gh >/dev/null 2>&1; then
  gh() {
    command gh "$@"
    _gh_fail_hook
  }
fi
# Wrap git push/fetch only (not status/log/etc.)
git() {
  local _sub="${1:-}"
  command git "$@"
  local _rc=$?
  case "$_sub" in
    push|fetch|pull|clone|remote) _gh_fail_hook ;;
    *) return "$_rc" ;;
  esac
  return "$_rc"
}
alias ghs='~/.local/bin/gh-status summary'
alias ghs-check='~/.local/bin/gh-status check'
alias ghs-inc='~/.local/bin/gh-status incidents'
alias ghs-watch='~/.local/bin/gh-status watch'
alias ghs-history='~/.local/bin/gh-status history'

# ── archive doctrine
archive() { ~/.local/bin/archive.sh "$@"; }
alias rm-arch='~/.local/bin/archive.sh'

export HS_REMOTE_URL="https://hs-0345-7vj97vj49jp9cg45-8888.app.github.dev"
export HINDSIGHT_BASE_URL="https://hs-0345-7vj97vj49jp9cg45-8888.app.github.dev"

export PATH="$HOME/bin:$PATH"
source ~/.zsh/hooks/mvt-status.zsh

# account-2 env (bearer-equivalent; source-only, mode 600)
[ -f "$HOME/.deepcli/account2.env" ] && . "$HOME/.deepcli/account2.env"

# >>> shell-forge (managed block — do not edit) >>>
[ -f "/data/data/com.termux/files/home/.config/shell-forge/aliases.zsh" ]  && source "/data/data/com.termux/files/home/.config/shell-forge/aliases.zsh"
# <<< shell-forge <<<

# >>> shell-forge preexec lint >>>

# Gate .py writes with ruff + ast.parse at command time.
__sf_lint_py() {
  local cmd="$1"
  case "$cmd" in
    *".py"*) ;;
    *) return 0 ;;
  esac
  case "$cmd" in
    *ruff*|*ast.parse*|*python3\ -c*|*pytest*|*git\ diff*|*git\ log*|*git\ show*|*git\ grep*|*rg\ *|*grep\ *|*ls\ *|*cat\ *) return 0 ;;
  esac
  local f
  for f in ${(z)cmd}; do
    if [[ "$f" == *.py && -f "$f" ]]; then
      if command -v ruff >/dev/null 2>&1; then
        ruff check --select E9,F63,F7,F82 "$f" >/dev/null 2>&1 \
          || { print -P "%F{red}[lint] ruff issues in $f%f"; ruff check --select E9,F63,F7,F82 "$f"; }
      fi
      python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$f" 2>/dev/null \
        || print -P "%F{red}[lint] ast.parse FAIL $f%f"
    fi
  done
}
autoload -Uz add-zsh-hook 2>/dev/null
add-zsh-hook preexec __sf_lint_py 2>/dev/null || true
# <<< shell-forge preexec lint <<<
