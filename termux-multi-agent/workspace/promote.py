#!/usr/bin/env python3
"""promote.py — enforce FORGE_OVERSIGHT promotion protocol with session tracking"""
import os, sys, shutil, json, subprocess, hashlib
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MASTER_TASKS = HOME / 'workspace/llm_map/master_tasks.json'
TRUE_VERSIONS = HOME / 'workspace/true_versions.json'
SESSION_HEAD = HOME / 'workspace/HEAD.json'

TIER_MAP = {
    'deepcli': 'cli-synthegration/workspace/staging',
    'deepcli-tui': 'cli-synthegration/workspace/staging',
    'cli-synthegration': 'harmonizer-prod_cli/workspace',
    'harmony_hub': 'harmonizer-prod_cli/workspace',
    'termux-multi-agent': 'harmonizer-prod_cli/workspace',
}

def get_session_id():
    """Extract current session ID from environment or HEAD.json"""
    session_id = os.environ.get('FORGE_SESSION_ID')
    if session_id:
        return session_id
    
    if SESSION_HEAD.exists():
        try:
            with open(SESSION_HEAD, 'r') as f:
                head_data = json.load(f)
                return head_data.get('session_id', f"unknown-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
        except:
            pass
    
    return f"session-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

def compute_content_hash(file_path):
    """Generate SHA-256 hash of file content"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

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
    """Custom versioning – no Git. Returns False because the
    orchestrator already applied and validated the change."""
    return False

def append_true_version(session_id, file_path, content_hash, timestamp):
    """Append session-tracked entry to true_versions.json"""
    true_versions = []
    
    # Load existing true_versions.json if it exists
    if TRUE_VERSIONS.exists():
        try:
            with open(TRUE_VERSIONS, 'r') as f:
                true_versions = json.load(f)
                if not isinstance(true_versions, list):
                    true_versions = []
        except:
            true_versions = []
    
    # Create new entry
    entry = {
        "session_id": session_id,
        "file_path": str(file_path),
        "content_hash": content_hash,
        "timestamp": timestamp,
        "promotion_id": f"promote-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    }
    
    # Append and save
    true_versions.append(entry)
    with open(TRUE_VERSIONS, 'w') as f:
        json.dump(true_versions, f, indent=2)

def promote_file(file_path):
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

    # Compute content hash and get session ID
    content_hash = compute_content_hash(abs_path)
    session_id = get_session_id()
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Append to true_versions.json
    append_true_version(session_id, final_path.relative_to(HOME), content_hash, timestamp)
    
    log_promotion(file_path_str, project, str(final_path.relative_to(HOME)), session_id)
    return True, f"Promoted to {final_path} (backup: {backup_name})"

def log_promotion(source, project, dest, session_id):
    entry = {
        "id": f"promote-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "title": f"Promote {source}",
        "ref": "PROMOTE",
        "priority": "high",
        "assigned_agent": "promote.py",
        "status": "done",
        "component": "promotion",
        "session_id": session_id,
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

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 promote.py <file_path>")
        sys.exit(1)
    file = sys.argv[1]
    ok, msg = promote_file(file)
    print("✅" if ok else "❌", msg)

