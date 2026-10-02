#!/usr/bin/env bash
# @tool dashboard-verify
# @version 0.2.0
set -u
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
LIFE="$(CDPATH= cd -- "$ROOT/.." && pwd)"
PASS=0; FAIL=0
ok(){ printf '  PASS %s\n' "$1"; PASS=$((PASS+1)); }
bad(){ printf '  FAIL %s\n' "$1"; FAIL=$((FAIL+1)); }

for f in "$ROOT"/sections/*.sh; do
 [ -f "$f" ] || continue
 bash -n "$f" && ok "syntax: $(basename "$f")" || bad "syntax: $(basename "$f")"
 head -1 "$f" | grep -qx '#!/usr/bin/env bash' && ok "shebang: $(basename "$f")" || bad "shebang: $(basename "$f")"
 grep -q '^# @section ' "$f" && ok "metadata: $(basename "$f")" || bad "metadata: $(basename "$f")"
 if grep -Eq '(^|[[:space:]])(pkill|kill|systemctl|service|dropdb|createdb)([[:space:]]|$)' "$f"; then
  bad "mutation/process command forbidden: $(basename "$f")"
 else ok "mutation/process guard: $(basename "$f")"; fi
 if grep -Eq '(^|[[:space:]])(rm|mv|cp|install|tee)([[:space:]]|$)|(^|[[:space:]])(>>?|<<)[[:space:]]*/tmp/hs-stack/' "$f"; then
  bad "pipeline-state mutation forbidden: $(basename "$f")"
 else ok "pipeline-state mutation guard: $(basename "$f")"; fi
 if grep -Eq 'bash[[:space:]].*purge-stale\.sql|psql[[:space:]].*purge-stale\.sql' "$f"; then
  bad "purge execution forbidden: $(basename "$f")"
 else ok "purge execution guard: $(basename "$f")"; fi
done

PURGE="$LIFE/purge-stale.sql"
if [ -f "$PURGE" ]; then
 grep -q '\\set ON_ERROR_STOP on' "$PURGE" && ok "purge: ON_ERROR_STOP" || bad "purge: missing ON_ERROR_STOP"
 grep -q 'BEGIN;' "$PURGE" && grep -q 'COMMIT;' "$PURGE" && ok "purge: transaction boundary" || bad "purge: transaction boundary"
 grep -q 'pg_advisory_xact_lock' "$PURGE" && ok "purge: advisory lock" || bad "purge: advisory lock"
 if grep -Eq 'DROP[[:space:]]+CONSTRAINT|ALTER[[:space:]]+TABLE.*DROP' "$PURGE"; then
  bad "purge: constraint dropping is forbidden"
 else ok "purge: no constraint dropping"; fi
 grep -q "SET bank_id = \$1 WHERE bank_id = \$2" "$PURGE" && ok "purge: schema-driven bank reconciliation" || bad "purge: reconciliation contract"
 grep -q 'purge_apply=1' "$PURGE" && ok "purge: explicit apply gate" || bad "purge: explicit apply gate"
else
 bad "purge: file missing"
fi

echo
printf '==== DASHBOARD VERIFY PASS=%s FAIL=%s ====\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
