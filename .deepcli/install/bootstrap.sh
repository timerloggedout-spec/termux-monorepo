#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
_tier="${1:-tier-0-local}"
_m="$HOME/.deepcli/install/releases/$_tier.yml"
[ -f "$_m" ] || { echo "no manifest: $_m"; exit 2; }
echo "bootstrap: $_tier"
python3 - "$_m" <<'PY'
import sys, yaml
m = yaml.safe_load(open(sys.argv[1]))
print(f"  requires: {m.get('requires', [])}")
print(f"  install_hooks: {m.get('install_hooks', [])}")
print(f"  health_checks: {[c['name'] for c in m.get('health_checks', [])]}")
PY
