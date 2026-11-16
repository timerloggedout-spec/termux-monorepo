#!/usr/bin/env python3
"""Cross-reference orphan code hashes with scavenged files in harmony_hub/utility_belt/ and export dirs."""
import json, os
from pathlib import Path

HOME = Path.home()
PTR = HOME / "archwiz/pointer_index.json"
UTIL = HOME / "harmony_hub/utility_belt"
EXPORTS = HOME / "synthegration_exports"

# Load orphans from previous script
ptr = json.loads(PTR.read_text()) if PTR.exists() else {}
prov_file = HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json"
prov = json.loads(prov_file.read_text()) if prov_file.exists() else {}
sess_files = {}
for f, entries in prov.items():
    for e in entries:
        sid = e.get("session")
        if sid:
            sess_files.setdefault(sid, set()).add(f)

orphan_hashes = [h for h, info in ptr.items()
                 if info.get("session_id") not in sess_files]

# Check Utility Belt
belt_files = set()
for f in UTIL.rglob("*"):
    if f.is_file():
        belt_files.add(f.name)

# Check export dirs
export_files = set()
for d in EXPORTS.iterdir():
    for mf in d.rglob("manifest.json"):
        try:
            blocks = json.loads(mf.read_text())
            for b in blocks:
                export_files.add(b.get("code_snippet","")[:50])
        except:
            pass

# Simple check: if any part of the orphan hash's snippet appears in belt or export files
still_orphan = 0
rescued = 0
for h in orphan_hashes[:1000]:  # limit for speed
    snippet = ptr[h].get("snippet","")[:80]
    if any(snippet in f for f in belt_files) or any(snippet in f for f in export_files):
        rescued += 1
    else:
        still_orphan += 1
print(f"Checked {min(1000, len(orphan_hashes))} orphans: {rescued} rescued, {still_orphan} still orphan")
