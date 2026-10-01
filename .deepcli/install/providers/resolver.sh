#!/data/data/com.termux/files/usr/bin/bash
# resolver.sh <provider-type> <args>...   exit 0 = present, 1 = missing
case "${1:-}" in
  file)   shift; for _f in "$@"; do [ -e "$_f" ] || { echo "missing file: $_f"; exit 1; }; done ;;
  env)    shift; for _v in "$@"; do [ -n "${!_v:-}" ] || { echo "missing env: $_v"; exit 1; }; done ;;
  gh-cli) command -v gh >/dev/null || { echo "gh missing"; exit 1; }; gh auth status >/dev/null 2>&1 || { echo "gh not authed"; exit 1; } ;;
  *) echo "unknown provider: ${1:-}"; exit 2 ;;
esac
