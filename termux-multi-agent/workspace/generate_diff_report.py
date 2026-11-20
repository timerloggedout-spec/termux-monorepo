#!/usr/bin/env python3
"""Generate a truth report: proposed vs actual files, fragment matcher status, session‑to‑file matching."""
import json
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Any, Optional

HOME = Path.home()
MAP = HOME / 'workspace/llm_map'
REPORT = []

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate truth report with optional session filtering'
    )
    parser.add_argument(
        '--session',
        type=str,
        help='Filter output to only files/tasks associated with the given session UUID'
    )
    return parser.parse_args()

def load_true_versions() -> Optional[Dict]:
    """Load true_versions.json if it exists."""
    tv_path = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'
    if tv_path.exists():
        return json.loads(tv_path.read_text())
    return None

def load_promotion_log() -> List[Dict]:
    """Load promotion log from master_tasks.json."""
    master_path = MAP.joinpath('master_tasks.json')
    if master_path.exists():
        master = json.loads(master_path.read_text())
        return [t for t in master if t.get('ref') == 'PROMOTE']
    return []

def get_files_for_session(session_id: str, true_versions: Optional[Dict], promotions: List[Dict]) -> Set[str]:
    """Get set of files/tasks associated with a session ID."""
    associated = set()
    
    # Check true_versions.json
    if true_versions:
        for key, value in true_versions.items():
            entries = value if isinstance(value, list) else [value]
            for entry in entries:
                if isinstance(entry, dict) and entry.get('session') == session_id:
                    associated.add(key)
                    if 'file' in entry:
                        associated.add(entry['file'])
    
    # Check promotion log
    for promo in promotions:
        if promo.get('session_id') == session_id:
            if 'target_file' in promo:
                associated.add(promo['target_file'])
            if 'title' in promo:
                associated.add(promo['title'])
            if 'id' in promo:
                associated.add(promo['id'])
    
    return associated

def check_file(path, description, session_files: Optional[Set[str]] = None):
    """Check file existence and add to report, optionally filtered by session."""
    f = Path(path).expanduser()
    exists = f.exists()
    
    # If session filtering is active, only include files in the session set
    if session_files is not None:
        if description not in session_files and str(f) not in session_files:
            return False
    
    size = f.stat().st_size if exists else 0
    mtime = datetime.fromtimestamp(f.stat().st_mtime).isoformat() if exists else 'N/A'
    REPORT.append(f"| {description} | {'✅' if exists else '❌'} | {size} bytes | {mtime} |")
    return True

def main():
    args = parse_args()
    session_id = args.session
    
    # Load data for session filtering
    true_versions = load_true_versions() if session_id else None
    promotions = load_promotion_log() if session_id else []
    session_files = None
    
    if session_id:
        session_files = get_files_for_session(session_id, true_versions, promotions)
        if not session_files:
            REPORT.append(f"# ⚠️ Session Filter Warning\n")
            REPORT.append(f"No files or tasks found for session ID: {session_id}\n")
            REPORT.append(f"Report will show empty results or only items explicitly matching this session.\n")
    
    # Header
    REPORT.append("# 🧬 Truth Report — Proposed vs. Actual\n")
    if session_id:
        REPORT.append(f"## 🔍 Filtered by Session: `{session_id}`\n")
    REPORT.append(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
    
    # Scripts & Tools section
    REPORT.append("## Scripts & Tools\n")
    REPORT.append("| Tool | Exists | Size | Last Modified |")
    REPORT.append("|------|--------|------|---------------|")
    
    tools = [
        ("Router Agent", "~/workspace/llm_map/router_agent.py"),
        ("Impact Oracle", "~/workspace/llm_map/impact_oracle.py"),
        ("Promote Script", "~/workspace/llm_map/promote.py"),
        ("Foresight Collector", "~/workspace/llm_map/foresight_collect.py"),
        ("Dispatch Task", "~/workspace/llm_map/dispatch_task.py"),
        ("Dispatch Adaptive", "~/workspace/llm_map/dispatch_adaptive.sh"),
        ("Agent Shell", "~/workspace/llm_map/agent_shell.py"),
        ("Task Watcher", "~/workspace/llm_map/task_watcher.sh"),
        ("Validate Promotion", "~/workspace/llm_map/validate_promotion.py"),
        ("Archaeologist", "~/workspace/llm_map/archaeologist.py"),
        ("Session Associate", "~/workspace/llm_map/session_associate.py"),
        ("Find Stale Files", "~/workspace/llm_map/find_stale_files.py"),
        ("Reliability Scan", "~/workspace/llm_map/reliability_scan.py"),
        ("Expand Sig Map", "~/workspace/llm_map/expand_sig_map.sh"),
        ("Inject AST Hashes", "~/workspace/llm_map/inject_ast_hashes.py"),
        ("Chunked Reader", "~/workspace/llm_map/chunked_reader.py"),
        ("Context Cache", "~/workspace/llm_map/context_cache.py"),
        ("Estimate Mem", "~/workspace/llm_map/estimate_mem.py"),
        ("Ecosystem Prompt", "~/workspace/llm_map/ecosystem_prompt.sh"),
        ("Diagnose Memory", "~/workspace/llm_map/diagnose_memory.sh"),
        ("DeepCLI Send", "~/workspace/llm_map/deepcli_send.py"),
        ("Session Title Refiner", "~/workspace/llm_map/session_title_refiner.py"),
        ("Simple Agent", "~/workspace/llm_map/simple_agent.py"),
        ("Batch Resumer", "~/workspace/llm_map/batch_resumer.py"),
        ("Forensic Query", "~/harmony_hub/utility_belt/forensic-query"),
        ("Workflow Reference", "~/harmony_hub/utility_belt/workflow"),
        ("Map Query", "~/harmony_hub/utility_belt/map-query.sh"),
        ("Tool Index", "~/workspace/llm_map/TOOL_INDEX.md"),
        ("Reference Doc", "~/workspace/llm_map/REFERENCE.md"),
        ("Changelog", "~/workspace/llm_map/CHANGELOG.md"),
        ("TUI Archaeology Report", "~/workspace/llm_map/TUI_ARCHAEOLOGY.md"),
        ("Access Policy", "~/workspace/llm_map/access_policy.json"),
    ]
    
    included_count = 0
    for desc, fpath in tools:
        if check_file(fpath, desc, session_files):
            included_count += 1
    
    if session_files and included_count == 0:
        REPORT.append("| *No tools match this session* | ❌ | 0 bytes | N/A |")
    
    REPORT.append("")
    
    # Fragment matcher section
    REPORT.append("## Fragment Matcher & Versioning\n")
    fm_path = HOME / 'cli-synthegration/workspace/provenance/fragment_matcher.py'
    
    if session_files is None or 'fragment_matcher.py' in session_files or str(fm_path) in session_files:
        if fm_path.exists():
            content = fm_path.read_text()
            REPORT.append(f"- fragment_matcher.py exists ✅  ({fm_path.stat().st_size} bytes)")
            REPORT.append(f"- Has compute_similarity: {'✅' if 'compute_similarity' in content else '❌'}")
        else:
            REPORT.append("- fragment_matcher.py not found ❌")
    
    tv_path = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'
    if tv_path.exists() and (session_files is None or 'true_versions.json' in session_files or str(tv_path) in session_files):
        tv = json.loads(tv_path.read_text())
        
        # Apply session filtering to true_versions data if needed
        if session_id:
            filtered_tv = {}
            for k, v in tv.items():
                entries = v if isinstance(v, list) else [v]
                filtered_entries = []
                for entry in entries:
                    if isinstance(entry, dict) and entry.get('session') == session_id:
                        filtered_entries.append(entry)
                if filtered_entries:
                    filtered_tv[k] = filtered_entries if isinstance(v, list) else filtered_entries[0]
            tv = filtered_tv
        
        total = len(tv)
        with_session = sum(1 for k, v in tv.items() for e in (v if isinstance(v, list) else [v]) if isinstance(e, dict) and e.get('session'))
        today = sum(1 for k, v in tv.items() for e in (v if isinstance(v, list) else [v]) if isinstance(e, dict) and e.get('timestamp_utc', '') >= '2026-06-08')
        REPORT.append(f"- true_versions.json: {total} entries, {with_session} with session IDs, {today} from 2026-06-08+")
    
    REPORT.append("")
    
    # Session bridge section
    REPORT.append("## Session‑to‑File Bridge\n")
    ci_path = HOME / 'cli-synthegration/workspace/correlation/correlation_index.json'
    if ci_path.exists() and (session_files is None or 'correlation_index.json' in session_files or str(ci_path) in session_files):
        size_mb = ci_path.stat().st_size / (1024 * 1024)
        try:
            r = subprocess.run(['jq', '-r', 'to_entries | map(select(.value[]? | test("[0-9a-f]{8}-"))) | length', str(ci_path)], 
                             capture_output=True, text=True, timeout=5)
            uuid_count = int(r.stdout.strip() or 0)
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            uuid_count = 0
        REPORT.append(f"- correlation_index.json: {size_mb:.1f} MB, {uuid_count} entries with UUID values")
    REPORT.append("")
    
    # Promotion metadata section
    REPORT.append("## Promotion Metadata\n")
    rh = HOME / 'termux-multi-agent/run_history.jsonl'
    if rh.exists() and (session_files is None or 'run_history.jsonl' in session_files or str(rh) in session_files):
        with open(rh) as f:
            verdicts = [json.loads(l) for l in f if l.strip()]
        
        # Filter by session if needed
        if session_id:
            verdicts = [v for v in verdicts if v.get('session_id') == session_id or v.get('session') == session_id]
        
        promoted = set(v['target_file'] for v in verdicts if 'task:' not in v['target_file'])
        REPORT.append(f"- Files with verdicts: {len(promoted)}")
    
    master_path = MAP.joinpath('master_tasks.json')
    if master_path.exists():
        master = json.loads(master_path.read_text())
        
        # Filter promotions by session if needed
        if session_id:
            promotes = [t for t in master if t.get('ref') == 'PROMOTE' and t.get('session_id') == session_id]
        else:
            promotes = [t for t in master if t.get('ref') == 'PROMOTE']
        
        REPORT.append(f"- Promotions logged: {len(promotes)}")
        for p in promotes:
            sid = '✅' if p.get('session_id') else '❌'
            REPORT.append(f"  - {p['title']} (has session_id: {sid})")
    REPORT.append("")
    
    # Pending tasks section
    if master_path.exists():
        master = json.loads(master_path.read_text())
        
        # Filter tasks by session if needed
        if session_id:
            tasks = [t for t in master if t.get('session_id') == session_id]
        else:
            tasks = master
        
        pending = [t for t in tasks if t.get('status') == 'pending']
        done = [t for t in tasks if t.get('status') == 'done']
        failed = [t for t in tasks if t.get('status') == 'failed']
        
        REPORT.append(f"## Task Queue: {len(done)} done / {len(pending)} pending / {len(failed)} failed")
        if pending:
            REPORT.append("\nPending:")
            for t in pending:
                REPORT.append(f"- {t['id']}: {t['title']}")
    
    # Write report
    report_text = '\n'.join(REPORT)
    print(report_text)
    
    # Output filename with session suffix if needed
    output_path = MAP / 'TRUTH_REPORT.md'
    if session_id:
        output_path = MAP / f'TRUTH_REPORT_{session_id[:8]}.md'
    
    output_path.write_text(report_text)
    print(f"\n✅ {output_path.name} written")

if __name__ == "__main__":
    main()
