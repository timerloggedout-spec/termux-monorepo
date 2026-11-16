#!/usr/bin/env bash
set -euo pipefail
TASK_ID="${DEEPCLI_TASK_ID:?}"
ROLE="${DEEPCLI_ROLE:-engineer}"
TRANSPORT="${DEEPCLI_TRANSPORT:-auto}"
TASK="${DEEPCLI_TASK:?}"
ROOT="${DEEPCLI_HOME:-$HOME/deepcli}"
LOG_DIR="$HOME/.deepcli/logs"
mkdir -p "$LOG_DIR"
START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
set +e
DEEPCLI_ROLE="$ROLE" DEEPCLI_TASK_ID="$TASK_ID" DEEPCLI_TRANSPORT="$TRANSPORT" \
  python3 "$ROOT/deepagent.py" --role "$ROLE" --task-id "$TASK_ID" --transport "$TRANSPORT" "$TASK" \
  >"$LOG_DIR/task-$TASK_ID.out" 2>"$LOG_DIR/task-$TASK_ID.err"
RC=$?
set -e
END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 - "$LOG_DIR/task-$TASK_ID.receipt.json" "$RC" "$START" "$END" "$TASK_ID" "$ROLE" "$TRANSPORT" <<'PY'
import json,sys
path,rc,start,end,task_id,role,transport=sys.argv[1:]
print(json.dumps({
 "schema_version":1,"task_id":task_id,"role":role,"transport":transport,
 "started_at":start,"finished_at":end,"exit_code":int(rc),
 "stdout_path":f"~/.deepcli/logs/task-{task_id}.out",
 "stderr_path":f"~/.deepcli/logs/task-{task_id}.err",
 "completion_status":"completed" if int(rc)==0 else "failed"
},indent=2))
open(path,"w").write(json.dumps({
 "schema_version":1,"task_id":task_id,"role":role,"transport":transport,
 "started_at":start,"finished_at":end,"exit_code":int(rc),
 "stdout_path":f"~/.deepcli/logs/task-{task_id}.out",
 "stderr_path":f"~/.deepcli/logs/task-{task_id}.err",
 "completion_status":"completed" if int(rc)==0 else "failed"
},indent=2)+"\n")
PY
cat "$LOG_DIR/task-$TASK_ID.receipt.json"
exit "$RC"
