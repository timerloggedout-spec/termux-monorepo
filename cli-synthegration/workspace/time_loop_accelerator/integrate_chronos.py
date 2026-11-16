#!/usr/bin/env python3
"""
integrate_chronos.py – Bridge true_versions.json into the existing Chronos accelerator.
Feeds file delays into get_live_stats() and computes realistic speedup.
"""
import json, sys, statistics
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
sys.path.insert(0, str(HOME / "cli-synthegration"))

# Load clean provenance
TRUE_VERSIONS = HOME / "cli-synthegration/workspace/provenance/true_versions.json"
with open(TRUE_VERSIONS) as f:
    true_data = json.load(f)

# --- Compute acceleration from clean data ---
first_delays = []
iter_delays = []
multi_version_files = 0

for fname, versions in true_data.items():
    if len(versions) >= 2:
        first_delays.append(versions[0]['delay_s'])
        for v in versions[1:]:
            iter_delays.append(v['delay_s'])
        multi_version_files += 1
    elif len(versions) == 1:
        first_delays.append(versions[0]['delay_s'])

first_median = statistics.median(first_delays) if first_delays else None
iter_median = statistics.median(iter_delays) if iter_delays else None
speedup = round(first_median / iter_median, 2) if (first_median and iter_median and iter_median > 0) else None

# --- Push to Chronos live stats if possible ---
try:
    from Chronos import accelerator as chronos
    # Check if there's a function to ingest external metrics
    if hasattr(chronos, 'get_live_stats'):
        stats = chronos.get_live_stats()
        print(f"Chronos live stats before update: {stats}")
    # If there's a setter or updater, call it
    if hasattr(chronos, 'update_metrics'):
        chronos.update_metrics({
            'provenance_files': len(true_data),
            'first_write_median_s': first_median,
            'iteration_median_s': iter_median,
            'speedup_factor': speedup,
            'multi_version_files': multi_version_files
        })
        print("Chronos metrics updated.")
    elif hasattr(chronos, 'LOOPS_DIR'):
        # Write a loop metrics file that Chronos can read
        loop_file = Path(chronos.LOOPS_DIR) / "provenance_metrics.json"
        loop_file.parent.mkdir(parents=True, exist_ok=True)
        with open(loop_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'files_with_provenance': len(true_data),
                'first_write_median_s': first_median,
                'iteration_median_s': iter_median,
                'speedup_factor': speedup,
                'multi_version_files': multi_version_files
            }, f, indent=2)
        print(f"Metrics written to {loop_file} for Chronos ingestion.")
except Exception as e:
    print(f"Chronos integration skipped: {e}")

# --- Write final report ---
report = {
    'source': 'true_versions.json (content‑matched, 2026 sessions)',
    'files_with_provenance': len(true_data),
    'multi_version_files': multi_version_files,
    'first_write_median_s': first_median,
    'iteration_median_s': iter_median,
    'speedup_factor': speedup,
    'interpretation': (
        f"Median first-write delay of {first_median:.0f}s. "
        f"Files that went through multiple iterations (n={multi_version_files}) "
        f"show a {speedup}x speedup on subsequent edits." if speedup else ""
    )
}
OUT = HOME / "cli-synthegration/workspace/time_loop_accelerator/clean_acceleration.json"
with open(OUT, 'w') as f:
    json.dump(report, f, indent=2)
print(f"\nFinal acceleration report → {OUT}")
print(f"First-write median: {first_median:.0f}s")
print(f"Speedup factor: {speedup}x")
print(f"Multi-version files: {multi_version_files}")
