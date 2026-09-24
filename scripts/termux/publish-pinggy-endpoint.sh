#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
REPO="${TERMUX_BRIDGE_REPO:-timerloggedout-spec/termux-monorepo}"
BRANCH="${TERMUX_BRIDGE_BRANCH:-master}"
PATH_IN_REPO="${TERMUX_BRIDGE_PATH:-ops/termux-bridge/current.json}"
LOG="${TERMUX_REVERSE_SSH_LOG:-$HOME/.local/state/termux-mcp/reverse-ssh.log}"
USER_NAME="${TERMUX_SSH_USER:-$USER}"
TTL_MINUTES="${TERMUX_BRIDGE_TTL_MINUTES:-60}"
command -v gh >/dev/null || { echo "gh is required" >&2; exit 1; }
command -v python >/dev/null || { echo "python is required" >&2; exit 1; }
test -r "$LOG" || { echo "reverse SSH log not found: $LOG" >&2; exit 1; }
endpoint="$(awk '/^tcp:\/\// { v=$0; sub(/^tcp:\/\//,"",v); print v }' "$LOG" | tail -n 1)"
payload="$(python - "$endpoint" "$USER_NAME" "$TTL_MINUTES" <<'PY'
import json,socket,sys
from datetime import datetime,timedelta,timezone
endpoint,user,ttl=sys.argv[1],sys.argv[2],int(sys.argv[3]); now=datetime.now(timezone.utc)
d={"schema_version":2,"transport":"pinggy-tcp-over-ssh","source":"device-runtime","remote_target":"127.0.0.1:8022","ssh_user":user,"ttl_minutes":ttl}
if not endpoint or ":" not in endpoint:
 d.update(status="stale",endpoint=None,port=None,observed_at=None,expires_at=None,stale_reason="no Pinggy tcp endpoint found in reverse SSH log")
else:
 host,ps=endpoint.rsplit(":",1)
 if not host or not ps.isdigit(): raise SystemExit("invalid endpoint: "+endpoint)
 port=int(ps); ok=False
 try:
  with socket.create_connection((host,port),timeout=5): ok=True
 except OSError: pass
 if ok:
  d.update(status="active",endpoint=host,port=port,observed_at=now.isoformat().replace("+00:00","Z"),expires_at=(now+timedelta(minutes=ttl)).isoformat().replace("+00:00","Z"),stale_reason=None,note="Published only after TCP reachability verification; SSH private keys are never stored here.")
 else:
  d.update(status="stale",endpoint=host,port=port,observed_at=None,expires_at=None,stale_reason="latest Pinggy endpoint is not accepting TCP connections",note="Stale endpoint retained for diagnosis only; wait for the boot tunnel to reconnect.")
print(json.dumps(d,indent=2))
PY
)"
tmp="$(mktemp)"; old="$(mktemp)"; trap 'rm -f "$tmp" "$old"' EXIT; printf '%s
' "$payload" >"$tmp"
current="$(gh api "repos/$REPO/contents/$PATH_IN_REPO?ref=$BRANCH" --jq '.content' 2>/dev/null || true)"
if [ -n "$current" ]; then printf '%s' "$current" | tr -d '\n' | base64 -d >"$old" || true; fi
if [ -s "$old" ]; then python - "$old" "$tmp" <<'PY'
import json,sys
old=json.load(open(sys.argv[1])); new=json.load(open(sys.argv[2]))
same=old.get("endpoint")==new.get("endpoint") and old.get("port")==new.get("port")
if same and old.get("status")=="active" and new.get("status")=="active":
 new["observed_at"]=old.get("observed_at"); new["expires_at"]=old.get("expires_at")
elif same and old.get("status")=="stale" and new.get("status")=="stale": new=old
json.dump(new,open(sys.argv[2],"w"),indent=2); open(sys.argv[2],"a").write("\n")
PY
fi
if [ -s "$old" ] && cmp -s "$tmp" "$old"; then echo "bridge manifest unchanged"; exit 0; fi
sha="$(gh api "repos/$REPO/contents/$PATH_IN_REPO?ref=$BRANCH" --jq '.sha' 2>/dev/null || true)"
encoded="$(base64 -w 0 "$tmp")"
args=(-X PUT "repos/$REPO/contents/$PATH_IN_REPO" -f "message=ops(termux): refresh live bridge state" -f "content=$encoded" -f "branch=$BRANCH")
[ -z "$sha" ] || args+=(-f "sha=$sha")
gh api "${args[@]}" >/dev/null
cat "$tmp"
