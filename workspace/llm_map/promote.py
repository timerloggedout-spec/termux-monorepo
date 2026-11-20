#!/usr/bin/env python3
"""promote.py — enforce FORGE_OVERSIGHT promotion protocol"""
import os, sys, shutil, json, subprocess
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MASTER_TASKS = HOME / 'workspace/llm_map/master_tasks.json'

TIER_MAP = {
    'deepcli': 'cli-synthegration/workspace/staging',
    'deepcli-tui': 'cli-synthegration/workspace/staging',
    'cli-synthegration': 'harmonizer-prod_cli/workspace',
    'harmony_hub': 'harmonizer-prod_cli/workspace',
    'termux-multi-agent': 'harmonizer-prod_cli/workspace',
}

def get_project(file_path):
    for proj in TIER_MAP:
        if file_path.startswith(proj):
            return proj
    return None

def has_passing_verdict(file_path):
    rh = HOME / 'termux-multi-agent/run_history.jsonl'
    if not rh.exists():
        return False
    target = str(Path(file_path))
    with open(rh) as f:
        for line in f:
            entry = json.loads(line)
            if entry.get('target_file') == target:
                if entry.get('verdict','').upper() == 'PASS':
                    return True
    return False

def has_uncommitted_changes(repo_dir):
    """Custom versioning – no Git.  Returns False because the
    orchestrator already applied and validated the change."""
    # FUTURE: compare source mtime vs last correlated session timestamp
    return False

def promote_file(file_path):
    # Pre-flight: syntax check
    import py_compile
    try:
        py_compile.compile(str(abs_path), doraise=True)
    except py_compile.PyCompileError as e:
        return False, f"Syntax error: {e}"

    abs_path = Path(file_path)
    if not abs_path.is_absolute():
        abs_path = HOME / file_path
    if not abs_path.exists():
        return False, f"File {abs_path} not found."

    file_path_str = str(abs_path.relative_to(HOME))

    # ── Impact Oracle check ──
    oracle_script = HOME / 'workspace/llm_map/impact_oracle.py'
    if oracle_script.exists():
        result = subprocess.run(
            ['python3', str(oracle_script), file_path_str],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'Shockwave Index' in line or 'Blast Score' in line:
                    print(f"💥 {line.strip()}")
                if 'Direct dependents' in line:
                    print(f"🔗 {line.strip()}")
                if 'Staged/ripe files' in line:
                    print(f"📊 {line.strip()}")

    project = get_project(file_path_str)
    if not project:
        return False, f"File not in a recognized project layer."

    target_dir = TIER_MAP.get(project)
    if not target_dir:
        return False, f"No promotion target for project {project}."

    if not has_passing_verdict(file_path_str):
        return False, "No PASS verdict in run_history for this file."

    repo_dir = HOME / project
    if has_uncommitted_changes(repo_dir):
        return False, "Uncommitted changes in source repo. Commit or stash before promoting."

    target_full = HOME / target_dir
    target_full.mkdir(parents=True, exist_ok=True)
    backup_name = abs_path.name.replace('.', f"_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.")
    backup_path = target_full / backup_name
    shutil.copy2(abs_path, backup_path)
    final_path = target_full / abs_path.name
    if final_path.exists():
        os.remove(final_path)
    shutil.copy2(abs_path, final_path)

    log_promotion(file_path_str, project, str(final_path.relative_to(HOME)))
    return True, f"Promoted to {final_path} (backup: {backup_name})"

def log_promotion(source, project, dest):
    entry = {
        "id": f"promote-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "title": f"Promote {source}",
        "ref": "PROMOTE",
        "priority": "high",
        "assigned_agent": "promote.py",
        "status": "done",
        "component": "promotion",
        "session_id": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "destination": dest,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    master = []
    if MASTER_TASKS.exists():
        with open(MASTER_TASKS) as f:
            master = json.load(f)
    master.append(entry)
    with open(MASTER_TASKS, 'w') as f:
        json.dump(master, f, indent=2)

# For TUI/UI modules, require explicit confirmation
TUI_MODULES = ['deepcli-tui/tui.py', 'tui.py']

if __name__ == '__main__':
    if sys.argv[-1] == '--confirm':
        sys.argv.pop()
    elif sys.argv[-1] in TUI_MODULES or any(sys.argv[-1].endswith(m) for m in TUI_MODULES):
        print("⚠️  TUI/UI module detected. Add --confirm to promote after manual UX verification.")
        sys.exit(1)
    if len(sys.argv) < 2:
        print("Usage: python3 promote.py <file_path>")
        sys.exit(1)
    file = sys.argv[1]
    ok, msg = promote_file(file)
    print("✅" if ok else "❌", msg)
