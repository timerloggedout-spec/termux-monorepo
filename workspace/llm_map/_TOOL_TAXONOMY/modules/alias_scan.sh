#!/data/data/com.termux/files/usr/bin/bash
MODE="$1"; STATE_DIR="$2"; OUTFILE="$3"
for cfg in "$HOME/.zshrc" "$HOME/.bashrc"; do
    [ -f "$cfg" ] || continue
    python3 -c "
import re, json, sys
with open('$cfg') as f:
    lines = f.readlines()
comment = ''
for line in lines:
    stripped = line.strip()
    if stripped.startswith('#'):
        comment = stripped.lstrip('#').strip()
        continue
    m = re.match(r'alias\s+([^=]+)=(.+)', stripped)
    if m:
        name = m.group(1).strip()
        value = m.group(2).strip().strip('\'').strip('\"')
        desc = comment if comment else ('Alias: ' + value)
        # escape for JSON safety
        obj = {'name': name, 'package': 'alias', 'path': '', 'source': 'alias', 'description': desc}
        print(json.dumps(obj))
        comment = ''
    elif not stripped.startswith('#') and stripped != '':
        comment = ''
"
done > "$OUTFILE"
