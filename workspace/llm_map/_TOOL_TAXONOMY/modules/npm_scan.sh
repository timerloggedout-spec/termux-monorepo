#!/data/data/com.termux/files/usr/bin/bash
source "$(dirname "$0")/common.sh"
MODE="$1"; STATE_DIR="$2"; OUTFILE="$3"
npm list -g --depth=0 --json 2>/dev/null > "$STATE_DIR/npm_curr.json"
if should_full_scan || ! diff -q "$STATE_DIR/npm_curr.json" "$STATE_DIR/npm_prev.json" >/dev/null 2>&1; then
    python3 -c "
import json, os
with open('$STATE_DIR/npm_curr.json') as f: data = json.load(f)
deps = data.get('dependencies', {})
with open('$OUTFILE', 'w') as out:
    for pkg, info in deps.items():
        bin_dir = '/data/data/com.termux/files/usr/bin'
        for root, dirs, files in os.walk(os.path.join('/data/data/com.termux/files/usr/lib/node_modules', pkg)):
            for fn in files:
                if fn == 'package.json':
                    with open(os.path.join(root, fn)) as pf: pdata = json.load(pf)
                    bin = pdata.get('bin', {})
                    bin_name = pkg if isinstance(bin, str) else list(bin.keys())[0] if bin else pkg
                    if os.path.exists(os.path.join(bin_dir, bin_name)):
                        out.write(json.dumps({'name': bin_name, 'package': f'npm:{pkg}', 'path': os.path.join(bin_dir, bin_name), 'source': 'npm'}) + '\n')
" 2>/dev/null
    cp "$STATE_DIR/npm_curr.json" "$STATE_DIR/npm_prev.json"
fi
