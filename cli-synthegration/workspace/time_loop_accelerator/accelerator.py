#!/usr/bin/env python3
"""
Time‑Loop Accelerator – Analyse copy‑paste cycle times and iteration speedups.
Uses versioned_provenance_full.json to compute per‑session metrics.
"""
import json, statistics
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
VERSIONED = HOME / "cli-synthegration/workspace/provenance/versioned_provenance_full.json"
OUT_DIR = HOME / "cli-synthegration/workspace/time_loop_accelerator"
OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(VERSIONED) as f:
    data = json.load(f)

# --- Per‑session metrics ---
session_files = defaultdict(list)  # session -> [(file, delay, version_index)]
for fname, versions in data.items():
    for vi, v in enumerate(versions):
        session_files[v['session']].append((fname, v['delay_s'], vi))

session_stats = {}
for sid, entries in session_files.items():
    delays = [e[1] for e in entries]
    iter_indices = [e[2] for e in entries]  # 0 = first write, 1 = second, etc.
    session_stats[sid] = {
        'files_touched': len(entries),
        'mean_delay_s': statistics.mean(delays),
        'median_delay_s': statistics.median(delays),
        'total_versions': sum(1 for e in entries),
        'first_write_count': sum(1 for e in entries if e[2] == 0),
        'iteration_count': sum(1 for e in entries if e[2] > 0),
    }

# --- Acceleration: compare first‑write delays to iteration delays ---
first_delays = []
iter_delays = []
for fname, versions in data.items():
    if len(versions) >= 2:
        first_delays.append(versions[0]['delay_s'])
        for v in versions[1:]:
            iter_delays.append(v['delay_s'])

acceleration = {}
if first_delays and iter_delays:
    acceleration = {
        'first_write_median_s': statistics.median(first_delays),
        'iteration_median_s': statistics.median(iter_delays),
        'speedup_factor': round(statistics.median(first_delays) / statistics.median(iter_delays), 2) if statistics.median(iter_delays) > 0 else None,
        'files_with_iterations': len([f for f, v in data.items() if len(v) >= 2]),
    }

# --- Bottlenecks: files with unusually long first‑write delays ---
threshold = statistics.median(first_delays) + 2 * statistics.stdev(first_delays) if len(first_delays) > 1 else float('inf')
bottlenecks = [
    (fname, versions[0]['delay_s'], versions[0]['session'])
    for fname, versions in data.items()
    if versions[0]['delay_s'] > threshold
]
bottlenecks.sort(key=lambda b: b[1], reverse=True)

# --- Optimal loop timing ---
# Median delay per session tells you when to expect the next file drop
if session_stats:
    best_session = min(session_stats.items(), key=lambda s: s[1]['median_delay_s'])
    worst_session = max(session_stats.items(), key=lambda s: s[1]['median_delay_s'])

# --- Write outputs ---
output = {
    'acceleration': acceleration,
    'bottlenecks_top20': [{'file': b[0], 'delay_s': b[1], 'session': b[2]} for b in bottlenecks[:20]],
    'optimal_session': {
        'session': best_session[0],
        'median_delay_s': best_session[1]['median_delay_s'],
        'files_touched': best_session[1]['files_touched']
    } if session_stats else {},
    'total_files_versioned': len(data),
    'total_sessions': len(session_stats),
}
with open(OUT_DIR / "acceleration_report.json", 'w') as f:
    json.dump(output, f, indent=2)

print(f"Acceleration report → {OUT_DIR / 'acceleration_report.json'}")
print(f"  Speedup factor (iter vs first): {acceleration.get('speedup_factor', 'N/A')}x")
print(f"  Top bottleneck: {bottlenecks[0][0] if bottlenecks else 'None'} ({bottlenecks[0][1]:.0f}s)" if bottlenecks else "")
