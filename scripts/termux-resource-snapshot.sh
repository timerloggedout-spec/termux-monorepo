#!/data/data/com.termux/files/usr/bin/sh
# Read-only health snapshot for a constrained Termux agentic hub.
set -eu

warn=0
say() {
  printf '%s\n' "$1"
}
kb_to_mib() {
  awk -v value="$1" 'BEGIN { printf "%.0f", value / 1024 }'
}

mem_total_kb="$(awk '/^MemTotal:/ { print $2 }' /proc/meminfo)"
mem_available_kb="$(awk '/^MemAvailable:/ { print $2 }' /proc/meminfo)"
swap_total_kb="$(awk '/^SwapTotal:/ { print $2 }' /proc/meminfo)"
swap_free_kb="$(awk '/^SwapFree:/ { print $2 }' /proc/meminfo)"
storage_line="$(df -Pk "$HOME" | awk 'NR == 2 { print $2, $3, $4, $5 }')"
set -- $storage_line
storage_total_kb="$1"
storage_used_kb="$2"
storage_avail_kb="$3"
storage_use_pct="${4%%%}"

say "timestamp=$(date -Iseconds)"
say "memory_total_mib=$(kb_to_mib "$mem_total_kb")"
say "memory_available_mib=$(kb_to_mib "$mem_available_kb")"
say "swap_total_mib=$(kb_to_mib "$swap_total_kb")"
say "swap_free_mib=$(kb_to_mib "$swap_free_kb")"
say "storage_total_mib=$(kb_to_mib "$storage_total_kb")"
say "storage_used_mib=$(kb_to_mib "$storage_used_kb")"
say "storage_available_mib=$(kb_to_mib "$storage_avail_kb")"
say "storage_used_percent=$storage_use_pct"

if [ "$mem_available_kb" -lt 153600 ]; then
  say "WARNING: memory_available_below_150_mib"
  warn=1
fi
if [ "$swap_total_kb" -gt 0 ] && [ "$swap_free_kb" -lt 131072 ]; then
  say "WARNING: swap_free_below_128_mib"
  warn=1
fi
if [ "$storage_avail_kb" -lt 1048576 ] || [ "$storage_use_pct" -ge 95 ]; then
  say "WARNING: storage_pressure"
  warn=1
fi

say "top_processes_rss_kib:"
if ps -eo pid,comm,rss --sort=-rss >/dev/null 2>&1; then
  ps -eo pid,comm,rss --sort=-rss | head -n 8
else
  ps -ef | head -n 8
fi

if [ "$warn" -eq 0 ]; then
  say "status=OK"
else
  say "status=PRESSURE"
fi
