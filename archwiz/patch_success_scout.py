#!/usr/bin/env python3
"""Scout: For a given file or session, list:
   - working files (exist on disk, last provenance match)
   - PASS/FAIL verdict from run_history
   - whether current file matches last known good version
   - orphan commands (not in any file)
"""
import json, sys, os, hashlib, argparse
from pathlib import Path
from collections import defaultdict
HOME = Path.home()
PROV = HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json"
TRUE_VER = HOME / "cli-synthegration/workspace/provenance/true_versions.json"
RUN_HIST = HOME / "termux-multi-agent/run_history.jsonl"
EXPORT_DIR = HOME / "synthegration_exports"
def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}
def load_run_history():
    entries = []
    if RUN_HIST.exists():
        with open(RUN_HIST) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    return entries
def file_hash(path):
    try:
        return hashlib.sha256(Path(HOME/path).read_bytes()).hexdigest()
    except:
        return None
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--session")
    parser.add_argument("--orphans", action="store_true", help="Show orphan commands for session")
    args = parser.parse_args()
    prov = load_json(PROV)
    true_ver = load_json(TRUE_VER)
    rh = load_run_history()
    if args.file:
        target = args.file
        if target not in prov:
            print(f"No provenance for {target}")
            return
        # Working? (exists on disk)
        working = (HOME / target).exists()
        print(f"File: {target}")
        print(f"Exists on disk: {'YES' if working else 'NO'}")
        # Latest provenance entry
        entries = prov[target]
        last = entries[-1] if entries else {}
        print(f"Last session: {last.get('session','?')} strategy={last.get('strategy','?')}")
        # True versions
        tv_entries = true_ver.get(target, [])
        if tv_entries:
            last_good_hash = tv_entries[-1].get("hash")
            current_hash = file_hash(target)
            match = current_hash == last_good_hash if current_hash and last_good_hash else None
            print(f"Matches last known good version: {match}")
        # Run history verdicts
        file_rh = [e for e in rh if e.get("target_file") == target]
        passes = [e for e in file_rh if e.get("verdict","").upper() == "PASS"]
        fails = [e for e in file_rh if e.get("verdict","").upper() == "FAIL"]
        print(f"PASS verdicts: {len(passes)}, FAIL: {len(fails)}")
        if file_rh:
            latest_verdict = file_rh[-1].get("verdict","?")
            print(f"Latest verdict: {latest_verdict}")
    elif args.session:
        sid = args.session
        # Find all files for this session
        files = [f for f, entries in prov.items()
                 if any(e.get("session") == sid for e in entries)]
        working_files = [f for f in files if (HOME/f).exists()]
        print(f"Session {sid}:")
        print(f"Total files in provenance: {len(files)}")
        print(f"Working files (exist on disk): {len(working_files)}")
        if args.orphans:
            # Orphan commands: code blocks from session exports not in any file
            # Simplified: compare hashes from manifest.json against file hashes
            # Export directories are named like "Title_SESSIONID" or just "SESSIONID"
            sess_dir = None
            for d in EXPORT_DIR.iterdir():
                if d.is_dir() and (d.name == sid or d.name.endswith('_' + sid)):
                    sess_dir = d
                    break
            if sess_dir is None:
                sess_dir = EXPORT_DIR / sid  # fallback (won't exist but prevents crash)
            if sess_dir.exists():
                manifest = sess_dir / "manifest.json"
                if manifest.exists():
                    blocks = json.loads(manifest.read_text())
                    orphan_cmds = []
                    for b in blocks:
                        code = b.get("code","") or b.get("code_snippet","")
                        if not code:
                            continue
                        # Check if any working file contains this code (crude substring)
                        found = False
                        for f in working_files:
                            try:
                                content = (HOME/f).read_text()
                                if code in content:
                                    found = True
                                    break
                            except:
                                pass
                        if not found:
                            orphan_cmds.append(code[:120])
                    if orphan_cmds:
                        print(f"Orphan commands (not in any working file): {len(orphan_cmds)}")
                        for cmd in orphan_cmds[:10]:
                            print(f"  {cmd}")
                    else:
                        print("No orphan commands found (all code appears in working files)")
            else:
                print("Export directory not found for this session.")
        else:
            for f in working_files[:20]:
                print(f"  {f}")
            if len(working_files) > 20:
                print(f"  ... and {len(working_files)-20} more")
    else:
        parser.print_help()
if __name__ == "__main__":
    main()
