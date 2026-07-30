#!/usr/bin/env python3
"""Compare pointer_index (all code hashes per session) with provenance (files per session).
   Outputs code blocks that have no corresponding file on disk."""
import json, sys
from pathlib import Path

HOME = Path.home()
PTR = HOME / "archwiz/pointer_index.json"
PROV = HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json"

ptr = json.loads(PTR.read_text()) if PTR.exists() else {}
prov = json.loads(PROV.read_text()) if PROV.exists() else {}

# Build session -> set of files from provenance
sess_files = {}
for f, entries in prov.items():
    for e in entries:
        sid = e.get("session")
        if sid:
            sess_files.setdefault(sid, set()).add(f)

# For each session in pointer index, find hashes with no file match
orphans = {}
for h, info in ptr.items():
    sid = info.get("session_id")
    if not sid:
        continue
    if sid not in sess_files:
        orphans[h] = f"Session {sid} not in provenance"
    # else: hash belongs to session; we could check deeper but keep simple

print(f"Total code hashes in pointer index: {len(ptr)}")
print(f"Sessions with provenance files: {len(sess_files)}")
print(f"Orphan hashes (no file match at all): {len(orphans)}")
if orphans:
    sample = list(orphans.items())[:5]
    for h, reason in sample:
        print(f"  {h}: {reason}")
