#!/usr/bin/env bash
echo "[ RUN STATE — current tick ]"
if [ -f /tmp/mvt-run-state.json ]; then
  python3 -c "
import json
d = json.load(open('/tmp/mvt-run-state.json'))
print(f\"  source={d.get('source','?')}  provider={d.get('provider','?')}  model={d.get('model','?')}\")
print(f\"  ok={d.get('ok',0)}  fail={d.get('fail',0)}  429={d.get('429',0)}  abort={d.get('abort',False)}  elapsed={d.get('elapsed_s',0)}s\")
print(f\"  bank={d.get('bank','?')}\")
"
fi

echo
