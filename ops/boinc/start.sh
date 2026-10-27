#!/bin/bash
# Start the BOINC client against a host-local data dir.
# Usage: start.sh <data_dir> [gui_rpc_password]
# Installs the client package if missing. The data dir is the host's
# identity: it holds the account XMLs (authenticators) - keep it 0700
# and never commit it.
set -eu
DATA_DIR="${1:?usage: start.sh <data_dir> [gui_rpc_password]}"
mkdir -p "$DATA_DIR"
chmod 700 "$DATA_DIR"
if [ -n "${2:-}" ]; then printf '%s' "$2" > "$DATA_DIR/gui_rpc_auth.cfg"; fi
cat > "$DATA_DIR/global_prefs_override.xml" <<'EOF'
<global_preferences>
  <max_ncpus_pct>100.0</max_ncpus_pct>
  <ram_max_used_busy_pct>50.0</ram_max_used_busy_pct>
  <disk_max_used_pct>10.0</disk_max_used_pct>
  <cpu_usage_limit>100.0</cpu_usage_limit>
</global_preferences>
EOF
[ -x /usr/bin/boinc ] || {
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
    --no-install-recommends boinc-client
}
exec /usr/bin/boinc --dir "$DATA_DIR" --daemon
