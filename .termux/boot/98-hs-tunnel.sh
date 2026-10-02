#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
sleep 30
_nf="$HOME/.deepcli/cs-hindsight-name.txt"
[ -f "$_nf" ] || exit 0
_cs=$(cat "$_nf")
[ -z "$_cs" ] && exit 0
# Only reconnect if codespace is Available
_st=$(gh codespace view -c "$_cs" --json state --jq '.state' 2>/dev/null)
[ "$_st" = "Available" ] || exit 0
pkill -f "ssh.*-L 18888" 2>/dev/null
nohup ssh -N -L 18888:localhost:8888 \
  "cs.${_cs}.feat-gh-actions-deepseek-integrates-itself" >/dev/null 2>&1 &
