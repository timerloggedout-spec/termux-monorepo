#!/usr/bin/env python3
"""Sync provenance entries into true_versions.json using:
   - hash‑strategy entries first, then similarity, then time.
   - If the file exists on disk, store the actual file hash as a safe fallback."""
import json, hashlib
from pathlib import Path

HOME = Path.home()
PROV = json.loads((HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json").read_text())
TRUE = HOME / "cli-synthegration/workspace/provenance/true_versions.json"
tv = json.loads(TRUE.read_text()) if TRUE.exists() else {}

for fpath, entries in PROV.items():
    if not entries:
        continue

    # Prefer hash entries, then similarity > 0.8, then any with snippet
    hash_entries = [e for e in entries if e.get("strategy") == "hash"]
    sim_entries = [e for e in entries if e.get("strategy") == "similarity" and e.get("similarity", 0) >= 0.8]
    time_entries = [e for e in entries if e.get("strategy") == "time" and e.get("snippet")]
    candidate = None
    if hash_entries:
        candidate = max(hash_entries, key=lambda e: e.get("timestamp_utc", ""))
    elif sim_entries:
        candidate = max(sim_entries, key=lambda e: (e.get("similarity", 0), e.get("timestamp_utc", "")))
    elif time_entries:
        candidate = max(time_entries, key=lambda e: e.get("timestamp_utc", ""))

    if candidate:
        snippet = candidate.get("snippet", "")
        if snippet:
            version_hash = hashlib.sha256(snippet.strip().encode()).hexdigest()
        else:
            continue
    else:
        # Last resort: use current on‑disk file hash
        fpath_abs = HOME / fpath
        if fpath_abs.exists():
            version_hash = hashlib.sha256(fpath_abs.read_bytes()).hexdigest()
        else:
            continue

    tv[fpath] = {
        "hash": version_hash,
        "session": candidate.get("session", "unknown") if candidate else "unknown",
        "timestamp_utc": candidate.get("timestamp_utc", "") if candidate else ""
    }

TRUE.write_text(json.dumps(tv, indent=2))
print(f"Synced {len(tv)} files to true_versions.json")
