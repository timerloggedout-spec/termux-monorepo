#!/usr/bin/env python3
"""
taxdiff – meaningful delta between two taxonomy snapshots.
Outputs a JSON diff only if something changed.
Usage: python3 taxdiff.py [--role ROLE_NAME] [--output DELTA_FILE]
"""
import json, os, sys, argparse
from collections import defaultdict

TAXDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALL_TOOLS = os.path.join(TAXDIR, "all_tools.jsonl")
SNAPSHOT = os.path.join(TAXDIR, "state", "tool_snapshot.json")
DELTA_DIR = os.path.join(TAXDIR, "delta")
os.makedirs(DELTA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)

def load_current_tools():
    tools = []
    with open(ALL_TOOLS) as f:
        for line in f:
            tools.append(json.loads(line))
    return tools

def load_previous_snapshot():
    if os.path.exists(SNAPSHOT):
        with open(SNAPSHOT) as f:
            return json.load(f)
    return {}

def save_snapshot(tools):
    # Save minimal representation: name->{tags, description, package, version?}
    snap = {}
    for t in tools:
        snap[t['name']] = {
            'tags': t.get('tags', []),
            'description': t.get('description', ''),
            'package': t.get('package', ''),
            'source': t.get('source', ''),
            'path': t.get('path', '')
        }
    with open(SNAPSHOT, 'w') as f:
        json.dump(snap, f, indent=2)

def diff_snapshots(current, previous):
    added = {}
    removed = {}
    changed = []

    curr_names = set(current.keys())
    prev_names = set(previous.keys())

    for name in curr_names - prev_names:
        added[name] = current[name]

    for name in prev_names - curr_names:
        removed[name] = previous[name]

    for name in curr_names & prev_names:
        if current[name] != previous[name]:
            changed.append({
                'name': name,
                'before': previous[name],
                'after': current[name]
            })

    return added, removed, changed

def filter_by_role(tools, role_name):
    # Load roles index
    role_file = os.path.join(TAXDIR, "roles", f"{role_name}.json")
    if not os.path.exists(role_file):
        print(f"Role '{role_name}' not found", file=sys.stderr)
        sys.exit(1)
    with open(role_file) as f:
        role_data = json.load(f)
    role_tool_names = {t['name'] for t in role_data.get('tools', [])}
    return {name: snap for name, snap in tools.items() if name in role_tool_names}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', help='Scope diff to a specific role')
    parser.add_argument('--output', help='Delta output file (default: delta/<timestamp>.json)')
    args = parser.parse_args()

    current_tools = load_current_tools()
    current_snap = {t['name']: {
        'tags': t.get('tags', []),
        'description': t.get('description', ''),
        'package': t.get('package', ''),
        'source': t.get('source', ''),
        'path': t.get('path', '')
    } for t in current_tools}

    previous_snap = load_previous_snapshot()

    if args.role:
        current_snap = filter_by_role(current_snap, args.role)
        previous_snap = filter_by_role(previous_snap, args.role) if previous_snap else {}

    added, removed, changed = diff_snapshots(current_snap, previous_snap)

    if not added and not removed and not changed:
        print("No changes detected.")
        # Still update snapshot to current state
        save_snapshot(current_tools)
        return

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat() + 'Z'
    delta = {
        'timestamp': now,
        'added': added,
        'removed': removed,
        'changed': changed
    }
    delta_path = args.output or os.path.join(DELTA_DIR, f"{now}.json")
    with open(delta_path, 'w') as f:
        json.dump(delta, f, indent=2)
    # Update latest symlink
    latest = os.path.join(DELTA_DIR, "latest.json")
    if os.path.exists(latest):
        os.remove(latest)
    os.symlink(delta_path, latest)
    # Save new snapshot
    save_snapshot(current_tools)
    print(f"Delta written to {delta_path}")
    print(f"  Added: {len(added)}, Removed: {len(removed)}, Changed: {len(changed)}")

if __name__ == "__main__":
    main()
