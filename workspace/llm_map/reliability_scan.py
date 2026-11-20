#!/usr/bin/env python3
"""Reliability scanner — scores source files incrementally, resumable."""
import json, subprocess, sqlite3, sys, re, time
from pathlib import Path
from datetime import datetime, timezone

MAP = Path(__file__).resolve().parent
INDEX = MAP / 'llm_index_compact.jsonl'
DB = MAP / 'reliability.db'
ORACLE = MAP / 'impact_oracle.py'
STATE_FILE = MAP / 'reliability_scan.state'
BATCH_SIZE = 10          # small batches to keep memory low
SLEEP_BETWEEN = 0.5      # seconds between files to avoid CPU spikes

# ── Load source files ──────────────────────────────────
with open(INDEX) as f:
    all_files = [json.loads(line)['p'] for line in f]

src_files = [f for f in all_files if f.endswith(('.py','.js','.ts','.sh','.mjs','.rs'))]
total = len(src_files)

# ── Resume from checkpoint ──────────────────────────────
processed = 0
if STATE_FILE.exists():
    processed = int(STATE_FILE.read_text().strip())

print(f"📋 {total} source files, resuming from {processed}")

# ── Database setup ──────────────────────────────────────
conn = sqlite3.connect(str(DB))
conn.execute('''CREATE TABLE IF NOT EXISTS reliability_series (
    file_path TEXT, shockwave INTEGER, nexus INTEGER, reliability INTEGER,
    stability_days INTEGER, echo_returns INTEGER, staged_in_blast INTEGER, run_at TEXT,
    PRIMARY KEY (file_path, run_at))''')
conn.commit()

def first_int(line):
    m = re.search(r'\b(\d+)\b', line)
    return int(m.group(1)) if m else 0

ok = fail = 0

# ── Batch‑Resume Loop ──────────────────────────────────
for i in range(processed, total):
    f = src_files[i]
    try:
        r = subprocess.run(
            ['python3', str(ORACLE), f],
            capture_output=True, text=True, timeout=30,
            cwd=str(MAP)
        )
        out = r.stdout
        vals = {'shockwave':0,'nexus':0,'reliability':0,'stability':0,'echo':0,'staged':0}

        for line in out.split('\n'):
            if 'Shockwave Index' in line:
                vals['shockwave'] = first_int(line)
            elif 'Nexus Rank' in line:
                vals['nexus'] = first_int(line)
            elif 'Reliability Score' in line:
                vals['reliability'] = first_int(line)
            elif 'Forged Stability' in line:
                vals['stability'] = first_int(line)
            elif 'Echo Return' in line:
                vals['echo'] = first_int(line)
            elif 'staged files in shockwave' in line:
                vals['staged'] = first_int(line)

        now = datetime.now(timezone.utc).isoformat()
        conn.execute('''INSERT OR REPLACE INTO reliability_series VALUES (?,?,?,?,?,?,?,?)''',
            (f, vals['shockwave'], vals['nexus'], vals['reliability'],
             vals['stability'], vals['echo'], vals['staged'], now))
        conn.execute('''INSERT OR REPLACE INTO reliability VALUES (?,?,?,?,?,?,?,?)''',
            (f, vals['shockwave'], vals['nexus'], vals['reliability'],
             vals['stability'], vals['echo'], vals['staged'], now))
        ok += 1
    except Exception as e:
        fail += 1
        if fail <= 3:
            print(f"  ⚠️  {f[:60]}: {e}")

    # Save progress every BATCH_SIZE files
    if (i + 1) % BATCH_SIZE == 0 or (i + 1) == total:
        conn.commit()
        STATE_FILE.write_text(str(i + 1))
        pct = (i + 1) / total * 100
        print(f"  🔄 {i+1}/{total} ({pct:.1f}%) — {ok} scored, {fail} failed")

    # Small sleep to avoid CPU spikes
    time.sleep(SLEEP_BETWEEN)

conn.commit()
conn.close()
if STATE_FILE.exists():
    STATE_FILE.unlink()
print(f"\n✅ Done: {ok} scored, {fail} failures")
