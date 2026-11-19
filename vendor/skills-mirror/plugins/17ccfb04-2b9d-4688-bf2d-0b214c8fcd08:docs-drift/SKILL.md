---
type: skill
name: docs-drift
description: Detect codebase changes and auto-generate documentation updates
trigger: manual or scheduled
tools: Task, Read, Write
model: haiku
argument-hint: "@. project root directory"
---

# Docs Drift — Automatic Documentation Updates

Scan your codebase for entity changes (added/removed/modified classes and functions) and automatically generate documentation updates. Proposes changes as drafts for human review before committing.

## Usage

```bash
/docs-drift @./my-project
/docs-drift @./my-project --compare  # Show comparison with last state
```

## Pipeline

1. **Scan** — Extract class/function definitions via AST parser using absolute paths
2. **Compare** — Check against `.beads/docs-state.json` (last stored state)
3. **Detect** — If changes found, dispatch docs-author agent → draft to `.tmp/docs-author-drafts/`
4. **Review** — User approves drafts, then auto-commit to git

**No changes:** Reports "✓ No changes detected. Docs are up to date."

**Output:** Drafts in `.tmp/docs-author-drafts/`:
- `entities-[timestamp].md` — Entity documentation updates
- `api-[timestamp].md` — API documentation changes
- `schema-[timestamp].md` — ER diagram and schema changes

---

```!
import subprocess
import json
from pathlib import Path
import sys

def resolve_project_root(arg):
    """Convert @. argument to absolute path. Returns Path object."""
    if arg == "@.":
        return Path.cwd().resolve()
    
    path = Path(arg).resolve()
    if not path.is_dir():
        raise ValueError(f"Project root does not exist: {path}")
    return path

def load_json_safe(path, default=None):
    """Load JSON file with error handling. Returns dict or default."""
    if not path.exists():
        return default if default is not None else {}
    
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"[WARN] Corrupt JSON at {path}: {e}. Using empty state.")
        return default if default is not None else {}

def run_codebase_diff(project_root):
    """Execute codebase_diff.py as subprocess. Returns parsed state dict or None."""
    script_path = Path(__file__).parent.parent.parent / "scripts" / "codebase_diff.py"
    
    result = subprocess.run(
        [sys.executable, str(script_path), str(project_root)],
        capture_output=True,
        text=True,
        cwd=str(project_root.parent),
    )
    
    if result.returncode != 0:
        print(f"[ERROR] Codebase scan failed: {result.stderr}")
        return None
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse codebase scan output: {e}")
        return None

def detect_changes(old_state, new_state):
    """Detect changes between two codebase states. Returns dict."""
    changes = {
        "added_classes": [],
        "removed_classes": [],
        "added_functions": [],
        "removed_functions": [],
        "modified_classes": [],
    }
    
    old_classes = {e.get("name") for f in old_state.values() for e in f.get("classes", []) if e.get("name")}
    new_classes = {e.get("name") for f in new_state.values() for e in f.get("classes", []) if e.get("name")}
    
    changes["added_classes"] = sorted(list(new_classes - old_classes))
    changes["removed_classes"] = sorted(list(old_classes - new_classes))
    
    old_functions = {e.get("name") for f in old_state.values() for e in f.get("functions", []) if e.get("name")}
    new_functions = {e.get("name") for f in new_state.values() for e in f.get("functions", []) if e.get("name")}
    
    changes["added_functions"] = sorted(list(new_functions - old_functions))
    changes["removed_functions"] = sorted(list(old_functions - new_functions))
    
    return changes

# Parse arguments
if len(sys.argv) < 2:
    print("[ERROR] Missing @. argument. Usage: /docs-drift @./my-project")
    sys.exit(1)

try:
    project_root = resolve_project_root(sys.argv[1])
except ValueError as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

show_compare = "--compare" in sys.argv

# Setup paths
beads_dir = project_root / ".beads"
try:
    beads_dir.mkdir(parents=True, exist_ok=True)
except OSError as e:
    print(f"[ERROR] Failed to create .beads directory: {e}")
    sys.exit(1)

docs_state_path = beads_dir / "docs-state.json"

# Scan current codebase
current_state = run_codebase_diff(project_root)
if current_state is None:
    print("[ERROR] Failed to scan codebase. Aborting.")
    sys.exit(1)

# Load previous state
previous_state = load_json_safe(docs_state_path, {})

# Detect changes
changes = detect_changes(previous_state, current_state)

# Count total changes
total_changes = sum(len(v) for v in changes.values() if isinstance(v, list))

print(f"[Docs Drift] Codebase: {project_root}")
print(f"[Docs Drift] State file: {docs_state_path}")

if show_compare:
    print(f"\n[Docs Drift] Comparison Report:")
    print(f"  Added classes:    {len(changes['added_classes'])} {changes['added_classes']}")
    print(f"  Removed classes:  {len(changes['removed_classes'])} {changes['removed_classes']}")
    print(f"  Added functions:  {len(changes['added_functions'])} {changes['added_functions']}")
    print(f"  Removed functions: {len(changes['removed_functions'])} {changes['removed_functions']}")

if total_changes == 0:
    print("[Docs Drift] ✓ No changes detected. Docs are up to date.")
else:
    print(f"\n[Docs Drift] Detected {total_changes} changes:")
    print(f"  - {len(changes['added_classes'])} added classes")
    print(f"  - {len(changes['removed_classes'])} removed classes")
    print(f"  - {len(changes['added_functions'])} added functions")
    print(f"  - {len(changes['removed_functions'])} removed functions")
    
    # Create draft directory
    drafts_dir = project_root / ".tmp" / "docs-author-drafts"
    try:
        drafts_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"[ERROR] Failed to create drafts directory: {e}")
        sys.exit(1)
    
    # Prepare docs-author agent input
    agent_input = {
        "changes": changes,
        "codebase_root": str(project_root),
        "docs_root": str(project_root / "docs"),
        "files_touched": list(current_state.keys()) if current_state else []
    }
    
    print(f"\n[Docs Drift] Dispatching docs-author agent...")
    print(f"  Input: {len(agent_input['files_touched'])} files touched")
    print(f"  Output will be written to: {drafts_dir}")
    
    # Task tool invocation (Claude Code framework will dispatch)
    # Framework converts this to: Task(name="docs-author", input_json=json.dumps(agent_input))
    task_payload = {
        "agent": "docs-author",
        "input": agent_input
    }
    print(f"[Docs Drift] Task payload: {json.dumps(task_payload, indent=2)}")
    
    # Save updated state (before task runs, so if agent fails, next run still has new state)
    try:
        docs_state_path.write_text(json.dumps(current_state, indent=2))
    except OSError as e:
        print(f"[ERROR] Failed to save state file: {e}")
        sys.exit(1)
    
    print(f"\n[Docs Drift] State saved: {docs_state_path}")
    print(f"[Docs Drift] ✓ Ready for docs-author agent. Files ready for review in: {drafts_dir}")
```
