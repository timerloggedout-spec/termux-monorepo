#!/data/data/com.termux/files/usr/bin/bash
# Lean Termux Monorepo maintenance script
# Run after any significant session or weekly
set -e
cd "$HOME"

echo "[*] Git prune + gc"
git reflog expire --expire=now --all
git gc --prune=now

echo "[*] Clear rebuildable caches"
rm -rf .cache/go-build .cache/node-gyp .cache/pip 2>/dev/null || true

echo "[*] Report"
du -sh .git .cache .npm .cargo .local 2>/dev/null | sort -hr
git count-objects -vH
echo "[+] Lean check complete – $(date)"
