#!/usr/bin/env python3
"""Create and populate a per‑file reliability database."""
import sqlite3, json
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
DB = HOME / 'workspace/llm_map/reliability.db'
METRICS = HOME / 'workspace/llm_map/metrics_log.jsonl'

conn = sqlite3.connect(DB)
conn.execute('''CREATE TABLE IF NOT EXISTS reliability (
    file_path TEXT PRIMARY KEY,
    last_shockwave INTEGER,
    last_nexus INTEGER,
    last_reliability INTEGER,
    last_stability_days INTEGER,
    last_echo INTEGER,
    staged_in_blast INTEGER,
    last_run TEXT
)''')

if METRICS.exists():
    with open(METRICS) as f:
        for line in f:
            entry = json.loads(line)
            conn.execute('''INSERT OR REPLACE INTO reliability
                (file_path, last_shockwave, last_nexus, last_reliability,
                 last_stability_days, last_echo, staged_in_blast, last_run)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (entry['file'], entry['shockwave'], entry['nexus'],
                 entry['reliability'], entry['stability_days'],
                 entry['echo'], entry['staged_in_blast'], entry['timestamp']))
    conn.commit()
    print(f"✅ reliability.db populated with {conn.execute('SELECT COUNT(*) FROM reliability').fetchone()[0]} entries")
else:
    print("ℹ️  No metrics_log.jsonl yet. Run impact_oracle.py on files to populate.")

conn.close()
