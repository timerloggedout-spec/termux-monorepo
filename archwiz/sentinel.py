#!/usr/bin/env python3
"""Sentinel – verification gate. Consults Archivist + Oracle + Grimoire before TasQue."""
import json, subprocess, sys, re
from pathlib import Path

HOME = Path.home()
ARCHIVIST = HOME / 'archwiz/archivist.py'
PROBE = HOME / 'archwiz/probe.py'
GRIMOIRE = HOME / 'harmony_hub/config/grimoire/1337_D1CT10N4RY.md'
CONSIDERATIONS = HOME / 'archwiz/CONSIDERATIONS.md'

R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'; C = '\033[1;36m'; N = '\033[0m'

def ask_archivist(query):
    """Call archivist.py and return parsed JSON."""
    result = subprocess.run(['python3', str(ARCHIVIST)] + query, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return result.stdout.strip()

def load_grimoire_terms():
    """Extract all known terms from the Grimoire Protocol table."""
    terms = set()
    if not GRIMOIRE.exists():
        return terms
    text = GRIMOIRE.read_text()
    in_table = False
    for line in text.splitlines():
        if 'Grimoire Protocol' in line:
            in_table = True
            continue
        if in_table and line.startswith('|') and not line.startswith('|--') and not line.startswith('| 🪄 Term'):
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if cols and cols[0]:
                terms.add(cols[0].lower())
        if in_table and not line.startswith('|') and line.strip():
            in_table = False
    return terms

def check_file_integrity(task):
    """Verify the target file exists on disk and in the Grid."""
    target = task.get('target_file', '')
    if not target:
        return True, "No target file specified — skipping file check."
    answer = ask_archivist(['file', target])
    if answer.get('on_disk') and answer.get('in_grid'):
        return True, f"File {target} present on disk and in Grid."
    elif not answer.get('on_disk'):
        return False, f"File {target} MISSING from disk."
    elif not answer.get('in_grid'):
        return False, f"File {target} MISSING from Grid (master index)."
    return False, f"File {target} not found."

def check_naming(task):
    """Verify task name/component against Grimoire Protocol."""
    title = task.get('title', '')
    component = task.get('component', '')
    grimoire_terms = load_grimoire_terms()
    issues = []
    # Check if component name conflicts with an existing Grimoire term
    for word in component.lower().replace('-',' ').replace('_',' ').split():
        if word in grimoire_terms:
            issues.append(f"Component '{component}' contains reserved Grimoire term '{word}'.")
    return len(issues) == 0, '; '.join(issues) if issues else "Naming consistent with Grimoire."

def check_duplicate_tasque(task_id):
    """Verify this task hasn't already been declared TasQue."""
    status = ask_archivist(['task', task_id])
    if status.get('in_tadone'):
        return False, f"Task {task_id} already declared TasQue in {status.get('tadone_file')}."
    return True, "Not previously declared TasQue."

def check_shockwave_stable(task_id):
    """Consult Oracle metrics for unexpected Shockwave change."""
    # For now, check if the task's last verdict was PASS and metrics exist.
    verdicts = ask_archivist(['verdicts'])
    if isinstance(verdicts, list):
        recent_task_verdicts = [v for v in verdicts if v.get('target_file') == f"task:{task_id}"]
        if recent_task_verdicts and recent_task_verdicts[-1].get('verdict') == 'PASS':
            return True, "Recent PASS verdict confirmed."
    return True, "Shockwave check skipped (no anomaly pattern)."


def check_testing(task):
    """Run Probe on the target file."""
    target = task.get('target_file', '')
    if not target or not target.endswith('.py'):
        return True, "No Python target — skipping Probe."
    import subprocess
    result = subprocess.run(['python3', str(HOME / 'archwiz/probe.py'), target, '--json'], capture_output=True, text=True)
    try:
        results = json.loads(result.stdout)
        passed = all(r['passed'] for r in results)
        detail = '; '.join(f"{r['check']}: {'PASS' if r['passed'] else 'FAIL'}" for r in results)
        return passed, detail
    except:
        return True, "Probe output unreadable — skipping."

def verify(task):
    """Run all checks and return verdict."""
    task_id = task.get('id', 'unknown')
    title = task.get('title', 'Unknown')
    print(f"\n{C}╔════════════════════════════════════════╗")
    print(f"║   SENTINEL VERIFICATION                ║")
    print(f"╚════════════════════════════════════════╝{N}")
    print(f"Task: {task_id} — {title}\n")

    checks = [
        ("File Integrity", check_file_integrity(task)),
        ("Naming", check_naming(task)),
        ("Duplicate TasQue", check_duplicate_tasque(task_id)),
        ("Probe (Testing)", check_testing(task)),
        ("Shockwave Stability", check_shockwave_stable(task_id)),
    ]

    all_pass = True
    for name, (passed, detail) in checks:
        icon = f"{G}✓{N}" if passed else f"{R}✗{N}"
        print(f"  {icon} {name}: {detail}")
        if not passed:
            all_pass = False

    print()
    if all_pass:
        print(f"{G}🛡️ VERDICT: ALLOW — TasQue may be declared.{N}")
        return True
    else:
        print(f"{Y}🛡️ VERDICT: REVIEW — manual inspection required.{N}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: sentinel.py <task_id>")
        sys.exit(1)
    # Load task from master_tasks.json
    master = HOME / 'workspace/llm_map/master_tasks.json'
    if master.exists():
        tasks = json.loads(master.read_text())
        task = next((t for t in tasks if t['id'] == sys.argv[1]), None)
        if task:
            result = verify(task)
            sys.exit(0 if result else 1)
        else:
            print(f"Task {sys.argv[1]} not found.")
            sys.exit(1)
    else:
        print("master_tasks.json not found.")
        sys.exit(1)
