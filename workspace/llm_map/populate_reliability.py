#!/usr/bin/env python3
"""Run impact_oracle.py on all indexed files, populate reliability.db with timestamps.
Uses BatchResumer for crash safety. Each run becomes a time‑series row.
"""
import json, subprocess, sqlite3, sys
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MAP = HOME / 'workspace/llm_map'
INDEX = MAP / 'llm_index_compact.jsonl'
DB = MAP / 'reliability.db'
STATE_FILE = MAP / 'reliability_scan.state'
BATCH_SIZE = 20

# Load all file paths
with open(INDEX) as f:
    all_files = [json.loads(line)['p'] for line in f]

total = len(all_files)

# Resume from checkpoint
processed = 0
if STATE_FILE.exists():
    processed = int(STATE_FILE.read_text().strip())

print(f"📋 {total} files total, resuming from {processed}")

# Ensure DB has a time‑series table (not just single row per file)
conn = sqlite3.connect(DB)
conn.execute('''CREATE TABLE IF NOT EXISTS reliability_series (
    file_path TEXT,
    shockwave INTEGER,
    nexus INTEGER,
    reliability INTEGER,
    stability_days INTEGER,
    echo_returns INTEGER,
    staged_in_blast INTEGER,
    run_at TEXT,
    PRIMARY KEY (file_path, run_at)
)''')
conn.commit()

success = 0
failed = 0

for i in range(processed, total):
    f = all_files[i]
    try:
        result = subprocess.run(
            ['python3', str(MAP / 'impact_oracle.py'), f],
            capture_output=True, text=True, timeout=30
        )
        # Parse the output for scores (they're printed to stdout)
        out = result.stdout
        shockwave = nexus = reliability = stability = echo = staged = 0
        
        for line in out.split('\n'):
            if 'Shockwave Index' in line:
                shockwave = int(line.split(':')[1].split('/')[0].strip())
            elif 'Nexus Rank' in line:
                nexus = int(line.split(':')[1].split('/')[0].strip())
            elif 'Reliability Score' in line:
                reliability = int(line.split(':')[1].split('/')[0].strip())
            elif 'Forged Stability' in line:
                stability = int(line.split(':')[1].split('/')[0].split('(')[0].strip())
            elif 'Echo Return' in line:
                echo = int(line.split(':')[1].split('PASS')[0].strip())
            elif 'staged files in shockwave' in line:
                staged = int(line.split(':')[1].split('staged')[0].strip())

        now = datetime.now(timezone.utc).isoformat()
        conn.execute('''INSERT OR REPLACE INTO reliability_series
            (file_path, shockwave, nexus, reliability, stability_days, echo_returns, staged_in_blast, run_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (f, shockwave, nexus, reliability, stability, echo, staged, now))
        
        # Also update the single-row table for quick lookup
        conn.execute('''INSERT OR REPLACE INTO reliability
            (file_path, last_shockwave, last_nexus, last_reliability,
             last_stability_days, last_echo, staged_in_blast, last_run)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (f, shockwave, nexus, reliability, stability, echo, staged, now))
        
        success += 1
        
    except Exception as e:
        failed += 1
        if failed <= 5:
            print(f"  ⚠️  {f[:60]}: {e}")

    # Batch commit and checkpoint
    if (i + 1) % BATCH_SIZE == 0 or (i + 1) == total:
        conn.commit()
        STATE_FILE.write_text(str(i + 1))
        pct = (i + 1) / total * 100
        print(f"  🔄 {i + 1}/{total} ({pct:.1f}%) — {success} ok, {failed} fail", end='\r')

conn.commit()
conn.close()
STATE_FILE.unlink()
print(f"\n✅ Complete: {success} files scored, {failed} failures")
print(f"   Time‑series rows: {conn.execute('SELECT COUNT(*) FROM reliability_series').fetchone()[0]}")
