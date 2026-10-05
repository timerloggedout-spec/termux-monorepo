#!/data/data/com.termux/files/usr/bin/bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WT="$HERE/tribute_worktree.py"
RC="$HERE/recon_repo.py"

cmd="${1:-}"; shift || true

case "$cmd" in
  recon)
    python3 "$RC" "${1:?owner/repo}" ;;
  run)
    repo="${1:?owner/repo}"; shift
    [ "$#" -ge 1 ] || { echo "run needs a command"; exit 2; }
    python3 "$RC" "$repo" || exit 3
    python3 "$WT" prepare "$repo" || exit 4
    slug="${repo//\//__}"
    cwd="$HOME/.cache/tribute/$slug"
    echo "--- exec in $cwd ---"
    ( cd "$cwd" && "$@" )
    touch "$cwd" 2>/dev/null || true
    python3 "$WT" sweep --ttl-hours 6 >/dev/null 2>&1 || true
    exit "$?"
    ;;
  prep)  repo="${1:?owner/repo}"; shift; python3 "$WT" prepare "$repo" "$@" ;;
  size)  python3 "$WT" size "${1:?owner/repo}" ;;
  list)  python3 "$WT" list ;;
  sweep) python3 "$WT" sweep "$@" ;;
  hygiene) python3 "$HERE/repo_hygiene.py" "$@" ;;
  *)
    echo "usage: tribute_lane.sh {recon|run|prep|size|list|sweep|hygiene} ..."
    exit 2 ;;
esac
