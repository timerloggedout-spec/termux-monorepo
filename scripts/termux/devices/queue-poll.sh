#!/usr/bin/env bash
# queue-poll.sh — P1 device pull-queue poller (spec docs/ops/P1-PULL-QUEUE-SPEC.md §8).
# Runs under Termux job 43112 every 15 min. Outbound HTTPS only: claim one task
# from the queue Worker, run it locally, post a receipt. No tunnel, no inbound
# port, no GitHub round-trip. Unprovisioned nodes exit 0 silently.
set -uo pipefail

TMX_CONFIG_DIR="${TMX_CONFIG_DIR:-$HOME/.config/tmx-device}"
TMX_STATE_DIR="${TMX_STATE_DIR:-$HOME/.local/state/tmx-device}"
IDENTITY_ENV="$TMX_CONFIG_DIR/identity.env"
QUEUE_ENV="$TMX_CONFIG_DIR/queue.env"

# Step 1: provisioning gate — silent exit when this node has no queue identity.
[ -r "$IDENTITY_ENV" ] && [ -r "$QUEUE_ENV" ] || exit 0
# shellcheck disable=SC1090
. "$IDENTITY_ENV"
# shellcheck disable=SC1090
. "$QUEUE_ENV"
[ -n "${DEVICE_QUEUE_URL:-}" ] && [ -n "${DEVICE_QUEUE_DEVICE_TOKEN:-}" ] && [ -n "${TERMUX_DEVICE_ID:-}" ] || exit 0

LOG_FILE="$TMX_STATE_DIR/queue-poll.log"
RECEIPTS_DIR="$TMX_STATE_DIR/receipts"
mkdir -p "$TMX_STATE_DIR" "$RECEIPTS_DIR"
# Step 7: rotate the local log at 1 MB (own state dir only; not telemetry).
if [ -f "$LOG_FILE" ] && [ "$(stat -c %s "$LOG_FILE" 2>/dev/null || echo 0)" -gt 1048576 ]; then
  mv -f "$LOG_FILE" "$LOG_FILE.1"
fi
log() { printf '[queue-poll %s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG_FILE"; }

ROLE="${DEVICE_QUEUE_ROLE:-engineer}"
REPO_ROOT="${TERMUX_MONOREPO_ROOT:-$HOME}"
ALLOWLIST="${TMX_QUEUE_ALLOWLIST:-$TMX_CONFIG_DIR/queue-allowlist.txt}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -r "$ALLOWLIST" ] || ALLOWLIST="$SCRIPT_DIR/queue-allowlist.default.txt"
SNAPSHOT="${TMX_RESOURCE_SNAPSHOT:-$REPO_ROOT/scripts/termux-resource-snapshot.sh}"
DEEPAGENT_RUNNER="${TMX_DEEPAGENT_RUNNER:-$REPO_ROOT/scripts/termux/run-deepagent-task.sh}"
RETRY_DELAY="${TMX_POLL_RETRY_DELAY:-30}"
AUTH=(-H "Authorization: Bearer $DEVICE_QUEUE_DEVICE_TOKEN")

# Expected on-device footprint per kind (MB). The pre-claim floor is
# max(500, 2 x footprint); the heaviest kind (deepagent-run, 250) sets it: 500.
footprint_mb() {
  case "$1" in
    deepagent-run) echo 250 ;;
    git-sync) echo 100 ;;
    git-commit-push) echo 50 ;;
    shell-allowlisted) echo 25 ;;
    *) echo 1 ;;
  esac
}
FLOOR_MB=500
for k in deepagent-run git-sync git-commit-push shell-allowlisted heartbeat-only; do
  f=$(( 2 * $(footprint_mb "$k") )); [ "$f" -gt "$FLOOR_MB" ] && FLOOR_MB="$f"
done
HEAVY_KINDS=" deepagent-run git-sync "

post_receipt_file() { # <task_id> <file> -> 0 on 2xx
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 -X POST \
    "$DEVICE_QUEUE_URL/tasks/$1/receipt" "${AUTH[@]}" \
    -H 'Content-Type: application/json' --data-binary @"$2" 2>/dev/null)" || return 1
  [ "${code:0:1}" = "2" ]
}

# Step 6 (first half): retry receipts persisted by earlier cycles BEFORE
# claiming new work — a network flap never loses a receipt.
for f in "$RECEIPTS_DIR"/*.json; do
  [ -e "$f" ] || break
  tid="$(basename "$f" .json)"
  if post_receipt_file "$tid" "$f"; then rm -f "$f"; log "reposted persisted receipt $tid";
  else log "receipt repost still failing for $tid"; fi
done

# Step 2: resource snapshot -> storage_free_mb; adaptive floor gate.
FREE_MB=""
if [ -r "$SNAPSHOT" ]; then
  FREE_MB="$(timeout 20 bash "$SNAPSHOT" 2>/dev/null | sed -n 's/^storage_available_mib=//p' | head -1)"
fi
case "$FREE_MB" in ''|*[!0-9]*) FREE_MB="$(df -Pk "$HOME" 2>/dev/null | awk 'NR==2 { printf "%d", $4/1024 }')" ;; esac
case "$FREE_MB" in ''|*[!0-9]*) FREE_MB=0 ;; esac
if [ "$FREE_MB" -lt "$FLOOR_MB" ]; then
  log "storage floor: free=${FREE_MB}MB < floor=${FLOOR_MB}MB; not claiming"
  exit 0
fi

# Step 3: claim one task (20 s timeout, one retry after a pause).
WORK="$(mktemp -d "$TMX_STATE_DIR/qp.XXXXXX")"; trap 'rm -rf "$WORK"' EXIT
claim_once() {
  curl -s -o "$WORK/claim.json" -w '%{http_code}' --max-time 20 \
    "$DEVICE_QUEUE_URL/tasks/next?role=$ROLE" "${AUTH[@]}" 2>/dev/null
}
CODE="$(claim_once)"; [ -n "$CODE" ] || CODE=000
if [ "$CODE" != "200" ] && [ "$CODE" != "204" ]; then
  sleep "$RETRY_DELAY"; CODE="$(claim_once)"; [ -n "$CODE" ] || CODE=000
fi
[ "$CODE" = "204" ] && { log "queue empty"; exit 0; }
[ "$CODE" = "200" ] || { log "claim failed http=$CODE"; exit 0; }

# Parse + validate the claim with python3 (jq is not guaranteed on-device).
python3 - "$WORK/claim.json" "$WORK" <<'PY' || { log "claim parse failed"; exit 0; }
import json, sys
d = json.load(open(sys.argv[1]))
t = d.get("task") or {}
open(sys.argv[2] + "/task_id", "w").write(str(t.get("id", "")))
open(sys.argv[2] + "/kind", "w").write(str(t.get("kind", "")))
open(sys.argv[2] + "/expires_at", "w").write(str(t.get("expires_at", "")))
p = t.get("payload") or "{}"
open(sys.argv[2] + "/payload.json", "w").write(p if isinstance(p, str) else json.dumps(p))
PY
TASK_ID="$(cat "$WORK/task_id")"; KIND="$(cat "$WORK/kind")"; EXPIRES_AT="$(cat "$WORK/expires_at")"
[ -n "$TASK_ID" ] || { log "claim carried no task id"; exit 0; }

now_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }
# Fabricate a schema-1 inner receipt (same shape run-deepagent-task.sh emits).
make_receipt() { # <exit_code> <status> <started> <file>
  python3 - "$4" "$TASK_ID" "$ROLE" "$3" "$1" "$2" <<'PY'
import json, sys
path, tid, role, start, rc, status = sys.argv[1:7]
json.dump({"schema_version": 1, "task_id": tid, "role": role, "transport": "queue-poll",
           "started_at": start, "finished_at": start, "exit_code": int(rc),
           "stdout_path": "", "stderr_path": "", "completion_status": status},
          open(path, "w"), indent=2)
PY
}
# Wrap an inner receipt per spec §5 and post it; persist on failure.
send_receipt() { # <inner_file> [note]
  python3 - "$WORK/inner.json" "$WORK/wrapper.json" "$TASK_ID" "$TERMUX_DEVICE_ID" "$FREE_MB" "${1:-}" <<'PY'
import json, sys
inner = json.load(open(sys.argv[1]))
w = {"schema_version": 1, "task_id": sys.argv[3], "device_id": sys.argv[4],
     "receipt": inner, "storage_free_mb": int(sys.argv[5])}
if sys.argv[6]: w["note"] = sys.argv[6]
json.dump(w, open(sys.argv[2], "w"), indent=2)
PY
  if post_receipt_file "$TASK_ID" "$WORK/wrapper.json"; then
    log "receipt posted $TASK_ID"
  else
    cp "$WORK/wrapper.json" "$RECEIPTS_DIR/$TASK_ID.json"
    log "receipt post failed; persisted $TASK_ID for next cycle"
  fi
}
reject() { # <reason>
  make_receipt 1 failed "$(now_iso)" "$WORK/inner.json"
  send_receipt "rejected:$1"
  log "rejected $TASK_ID: $1"; exit 0
}

# Step 4: on-device validation — allowlist, payload parses, not expired.
grep -qx "$KIND" "$ALLOWLIST" 2>/dev/null || reject "kind-not-allowlisted"
python3 -m json.tool "$WORK/payload.json" >/dev/null 2>&1 || reject "payload-not-json"
python3 - "$EXPIRES_AT" <<'PY' || reject "expired"
import sys, datetime
try:
    exp = datetime.datetime.fromisoformat(sys.argv[1].replace("Z", "+00:00"))
except Exception:
    sys.exit(1)
sys.exit(0 if exp > datetime.datetime.now(datetime.timezone.utc) else 1)
PY

# Heavy kinds need the wake-lock held; acquire it when the tool exists, else
# release the claim cleanly for a later cycle instead of running half-awake.
case "$HEAVY_KINDS" in
  *" $KIND "*)
    if [ ! -e "$TMX_STATE_DIR/wakelock.held" ]; then
      if command -v termux-wake-lock >/dev/null 2>&1; then termux-wake-lock >/dev/null 2>&1 || true
      else
        curl -s -o /dev/null --max-time 20 -X POST "$DEVICE_QUEUE_URL/tasks/$TASK_ID/release" \
          "${AUTH[@]}" -H 'Content-Type: application/json' -d '{"note":"wakelock-not-held"}' >/dev/null 2>&1 || true
        log "released $TASK_ID (heavy kind, wake-lock not held)"; exit 0
      fi
    fi ;;
esac

# Step 5: execute by kind.
STARTED="$(now_iso)"
case "$KIND" in
  heartbeat-only)
    make_receipt 0 completed "$STARTED" "$WORK/inner.json" ;;
  deepagent-run)
    TASK_TEXT="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("task",""))' "$WORK/payload.json")"
    [ -n "$TASK_TEXT" ] || reject "deepagent-run without payload.task"
    set +e
    DEEPCLI_TASK_ID="$TASK_ID" DEEPCLI_TASK="$TASK_TEXT" DEEPCLI_ROLE="$ROLE" \
      bash "$DEEPAGENT_RUNNER" >"$WORK/runner.out" 2>"$WORK/runner.err"
    RC=$?; set -e
    if python3 -m json.tool "$WORK/runner.out" >/dev/null 2>&1; then
      cp "$WORK/runner.out" "$WORK/inner.json"
    else
      make_receipt "$RC" "$([ "$RC" -eq 0 ] && echo completed || echo failed)" "$STARTED" "$WORK/inner.json"
    fi ;;
  git-sync)
    set +e; ( cd "$REPO_ROOT" && git pull --ff-only ) >"$WORK/git.out" 2>&1; RC=$?; set -e
    make_receipt "$RC" "$([ "$RC" -eq 0 ] && echo completed || echo failed)" "$STARTED" "$WORK/inner.json" ;;
  git-commit-push)
    MSG="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("message",""))' "$WORK/payload.json")"
    [ -n "$MSG" ] || MSG="device: queue task $TASK_ID"
    set +e
    ( cd "$REPO_ROOT" && git add -A \
      && { git diff --cached --quiet || git commit -m "$MSG" >/dev/null; } \
      && git push ) >"$WORK/git.out" 2>&1
    RC=$?; set -e
    make_receipt "$RC" "$([ "$RC" -eq 0 ] && echo completed || echo failed)" "$STARTED" "$WORK/inner.json" ;;
  shell-allowlisted)
    CMD="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("command",""))' "$WORK/payload.json")"
    LINE="$(grep -F -x "cmd:$CMD" "$ALLOWLIST" 2>/dev/null | head -1)"
    [ -n "$LINE" ] || reject "command-not-allowlisted"
    # Execute the allowlist file's own string, never the payload's copy.
    set +e; bash -c "${LINE#cmd:}" >"$WORK/shell.out" 2>&1; RC=$?; set -e
    make_receipt "$RC" "$([ "$RC" -eq 0 ] && echo completed || echo failed)" "$STARTED" "$WORK/inner.json" ;;
  *) reject "kind-unhandled" ;;
esac

send_receipt ""
log "done $TASK_ID kind=$KIND"
exit 0
