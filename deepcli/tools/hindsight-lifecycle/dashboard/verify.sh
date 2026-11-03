#!/usr/bin/env bash
# @tool dashboard-verify
# @version 0.1.1
set -u
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
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
echo
printf '==== DASHBOARD VERIFY PASS=%s FAIL=%s ====\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
