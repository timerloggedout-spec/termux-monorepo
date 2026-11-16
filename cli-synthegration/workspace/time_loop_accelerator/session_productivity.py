#!/usr/bin/env python3
"""
session_productivity.py – Per‑session metrics for the Time‑Loop Accelerator.
Groups comprehensive provenance by session; writes ranked productivity.
Feeds into Chronos live stats.
"""
import json, statistics, sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

HOME = Path.home()
OUT = HOME / "cli-synthegration/workspace/time_loop_accelerator"
PROV = HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json"
SESSION_PROD = OUT / "session_productivity.json"
LOOPS_DIR = HOME / "cli-synthegration/metrics/loops"

if not PROV.exists():
    print("Run comprehensive_fast.py first.")
    sys.exit(1)

with open(PROV) as f:
    data = json.load(f)

# Group by session
session_versions = defaultdict(list)
for fname, versions in data.items():
    for v in versions:
        session_versions[v['session']].append({**v, 'file': fname})

print(f"Sessions: {len(session_versions)}")

# Compute per‑session metrics
session_stats = {}
for sid, versions in session_versions.items():
    # Sort by timestamp
    versions_sorted = sorted(versions, key=lambda v: v['timestamp_utc'])
    delays = [v.get('delay_s', 0) for v in versions_sorted if v.get('delay_s') is not None]
    timestamps = [v['timestamp_utc'] for v in versions_sorted]
    files = list(set(v['file'] for v in versions_sorted))

    # Batch detection: group timestamps within 10s of each other
    batches = []
    if timestamps:
        batch_start = timestamps[0]
        batch_count = 1
        for ts in timestamps[1:]:
            t_prev = datetime.fromisoformat(batch_start).timestamp()
            t_curr = datetime.fromisoformat(ts).timestamp()
            if t_curr - t_prev <= 10:
                batch_count += 1
            else:
                batches.append(batch_count)
                batch_start = ts
                batch_count = 1
        batches.append(batch_count)

    session_stats[sid] = {
        'session': sid,
        'file_count': len(files),
        'version_count': len(versions),
        'median_delay_s': statistics.median(delays) if delays else None,
        'first_version': versions_sorted[0]['timestamp_utc'],
        'last_version': versions_sorted[-1]['timestamp_utc'],
        'total_span_s': (
            datetime.fromisoformat(versions_sorted[-1]['timestamp_utc']).timestamp() -
            datetime.fromisoformat(versions_sorted[0]['timestamp_utc']).timestamp()
        ),
        'batch_count': len(batches),
        'max_batch_size': max(batches) if batches else 0,
        'mean_batch_size': statistics.mean(batches) if batches else 0,
        'top_files': files[:5],
        'strategies': {
            'hash': sum(1 for v in versions if v.get('strategy') == 'hash'),
            'similarity': sum(1 for v in versions if v.get('strategy') == 'similarity'),
            'time': sum(1 for v in versions if v.get('strategy') == 'time'),
        }
    }

# Rank by file_count
ranked = sorted(session_stats.values(), key=lambda s: s['file_count'], reverse=True)

# Write session productivity
with open(SESSION_PROD, 'w') as f:
    json.dump(ranked, f, indent=2)
print(f"Session productivity → {SESSION_PROD}")

# Feed into Chronos
try:
    sys.path.insert(0, str(HOME / "cli-synthegration"))
    from Chronos import accelerator as chronos
    loop_file = Path(chronos.LOOPS_DIR) / "session_productivity.json"
    loop_file.parent.mkdir(parents=True, exist_ok=True)
    with open(loop_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'top_sessions': ranked[:5],
            'total_sessions': len(session_stats),
            'total_files': sum(s['file_count'] for s in ranked),
        }, f, indent=2)
    print(f"Chronos metrics updated → {loop_file}")
except Exception as e:
    print(f"Chronos update skipped: {e}")

# Print top 5
print("\n=== Top 5 Sessions by File Count ===")
for s in ranked[:5]:
    span_min = s['total_span_s'] / 60
    print(f"  {s['session'][:40]}...")
    print(f"    Files: {s['file_count']}  Versions: {s['version_count']}  Batches: {s['batch_count']}  MaxBatch: {s['max_batch_size']}")
    print(f"    Median delay: {s['median_delay_s']:.0f}s  Span: {span_min:.0f}min")
    print(f"    Strategies: {s['strategies']}")
    print()
