#!/bin/bash
cd ~
echo "==== 1. CLI entry points & help stubs ===="
for src in deepcli/main.py deepseek-cli/main.js deepseek-cli/index.js termux-multi-agent/run.py deepcli-tui/index.js; do
  [ -f "$src" ] && echo "--- $src ---" && head -50 "$src"
done

echo "==== 2. Deepcli TUI token handling ===="
grep -A10 "def get_token" ~/deepcli/core.py 2>/dev/null || grep -A10 "def get_token" ~/deepcli/src/core.py 2>/dev/null

echo "==== 3. Argument parsers (argparse/click/commander) ===="
grep -rn "add_argument\|@click\|\.command\b\|commander(" \
  ~/deepcli/ ~/deepseek-cli/ ~/deepcli-tui/ ~/termux-multi-agent/ \
  --include="*.py" --include="*.js" --include="*.ts" 2>/dev/null | head -30

echo "==== 4. CEDARscript / CedrLang references ===="
grep -rn "CEDARscript\|cedrlang\|cedar" \
  ~/deepseek-cli/ ~/termux-multi-agent/ ~/deepcli/ ~/deepcli-tui/ \
  --include="*.py" --include="*.sh" --include="*.md" --include="*.json" 2>/dev/null

echo "==== 5. Session / conversation table schemas ===="
grep -rn "CREATE TABLE\|session\|conversation" \
  ~/termux-multi-agent/src/db.py 2>/dev/null
[ -f ~/termux-multi-agent/local_repo.db ] && sqlite3 ~/termux-multi-agent/local_repo.db ".schema"

echo "==== 6. Existing token locations ===="
find ~/deepseek-cli/ -name '*.json' -maxdepth 1 -exec grep -l 'authorization' {} \;
cat ~/.deepseek_api_key 2>/dev/null && echo "Found .deepseek_api_key"
