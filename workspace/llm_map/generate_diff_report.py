#!/usr/bin/env python3
"""Generate a truth report: proposed vs actual files, fragment matcher status, session‑to‑file matching."""
import json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MAP = HOME / 'workspace/llm_map'
REPORT = []

def check_file(path, description):
    f = Path(path).expanduser()
    exists = f.exists()
    size = f.stat().st_size if exists else 0
    mtime = datetime.fromtimestamp(f.stat().st_mtime).isoformat() if exists else 'N/A'
    REPORT.append(f"| {description} | {'✅' if exists else '❌'} | {size} bytes | {mtime} |")

REPORT.append("# 🧬 Truth Report — Proposed vs. Actual\n")
REPORT.append(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
REPORT.append("## Scripts & Tools\n")
REPORT.append("| Tool | Exists | Size | Last Modified |")
REPORT.append("|------|--------|------|---------------|")
for desc, fpath in [
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
]:
    check_file(fpath, desc)
REPORT.append("")

# Fragment matcher
REPORT.append("## Fragment Matcher & Versioning\n")
fm_path = HOME / 'cli-synthegration/workspace/provenance/fragment_matcher.py'
if fm_path.exists():
    content = fm_path.read_text()
    REPORT.append(f"- fragment_matcher.py exists ✅  ({fm_path.stat().st_size} bytes)")
    REPORT.append(f"- Has compute_similarity: {'✅' if 'compute_similarity' in content else '❌'}")
else:
    REPORT.append("- fragment_matcher.py not found ❌")
tv_path = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'
if tv_path.exists():
    tv = json.loads(tv_path.read_text())
    total = len(tv)
    with_session = sum(1 for k,v in tv.items() for e in (v if isinstance(v,list) else [v]) if e.get('session'))
    today = sum(1 for k,v in tv.items() for e in (v if isinstance(v,list) else [v]) if e.get('timestamp_utc','') >= '2026-06-08')
    REPORT.append(f"- true_versions.json: {total} entries, {with_session} with session IDs, {today} from 2026-06-08+")
REPORT.append("")

# Session bridge
REPORT.append("## Session‑to‑File Bridge\n")
ci_path = HOME / 'cli-synthegration/workspace/correlation/correlation_index.json'
if ci_path.exists():
    size_mb = ci_path.stat().st_size / (1024*1024)
    r = subprocess.run(['jq','-r','to_entries | map(select(.value[]? | test("[0-9a-f]{8}-"))) | length', str(ci_path)], capture_output=True, text=True)
    uuid_count = int(r.stdout.strip() or 0)
    REPORT.append(f"- correlation_index.json: {size_mb:.1f} MB, {uuid_count} entries with UUID values")
REPORT.append("")

# Promotion metadata
REPORT.append("## Promotion Metadata\n")
rh = HOME / 'termux-multi-agent/run_history.jsonl'
if rh.exists():
    with open(rh) as f:
        verdicts = [json.loads(l) for l in f if l.strip()]
    promoted = set(v['target_file'] for v in verdicts if 'task:' not in v['target_file'])
    REPORT.append(f"- Files with verdicts: {len(promoted)}")
master = json.loads(MAP.joinpath('master_tasks.json').read_text())
promotes = [t for t in master if t.get('ref')=='PROMOTE']
REPORT.append(f"- Promotions logged: {len(promotes)}")
for p in promotes:
    sid = '✅' if p.get('session_id') else '❌'
    REPORT.append(f"  - {p['title']} (has session_id: {sid})")
REPORT.append("")

# Pending tasks
pending = [t for t in master if t['status']=='pending']
done = [t for t in master if t['status']=='done']
failed = [t for t in master if t['status']=='failed']
REPORT.append(f"## Task Queue: {len(done)} done / {len(pending)} pending / {len(failed)} failed")
if pending:
    REPORT.append("\nPending:")
    for t in pending:
        REPORT.append(f"- {t['id']}: {t['title']}")

report_text = '\n'.join(REPORT)
print(report_text)
(MAP / 'TRUTH_REPORT.md').write_text(report_text)
print("\n✅ TRUTH_REPORT.md written")
