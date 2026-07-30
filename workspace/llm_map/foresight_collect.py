#!/usr/bin/env python3
"""foresight_collect.py — aggregate all data for 4πG_451GH7 (Forge ForeSight)"""
import json, re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter
from batch_resumer import BatchResumer

HOME = Path.home()
MAP = HOME / 'workspace/llm_map'

# Inputs
RUN_HISTORY    = HOME / 'termux-multi-agent/run_history.jsonl'
SPRINTS        = HOME / 'cli-synthegration/metrics/sprints.json'
DEPS           = MAP / 'deps.jsonl'
MASTER_TASKS   = MAP / 'master_tasks.json'
FORGE_MD       = HOME / 'workspace/FORGE_OVERSIGHT.md'
FUNC_INDEX     = MAP / 'func_index.jsonl'
LLM_INDEX      = MAP / 'llm_index_compact.jsonl'

# Output
FORESIGHT_OUT  = MAP / 'foresight_state.json'

def load_jsonl(path):
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f]

def load_json(path):
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)

def load_llm_index():
    if not LLM_INDEX.exists():
        return {}
    entries = {}
    with open(LLM_INDEX) as f:
        for line in f:
            e = json.loads(line)
            entries[e['p']] = e
    return entries

# --- 1. Run History Metrics ---
run_history = load_jsonl(RUN_HISTORY)
pass_count = sum(1 for e in run_history if e.get('verdict','').upper() == 'PASS')
fail_count = sum(1 for e in run_history if e.get('verdict','').upper() == 'FAIL')
total_runs = len(run_history)

# --- 2. Sprint Analysis ---
sprints = load_json(SPRINTS) if SPRINTS.exists() else []
blocked = [s for s in sprints if s.get('status') == 'blocked']
active  = [s for s in sprints if s.get('status') in ('active', 'in-progress')]
resolved = [s for s in sprints if s.get('status') in ('resolved', 'done', 'closing')]

# --- 3. Dependency Stats ---
deps = load_jsonl(DEPS)
# map resolved edges from file_graph.json if newer
file_graph = load_json(MAP / 'file_graph.json') if (MAP / 'file_graph.json').exists() else {}
resolved_edge_count = sum(len(v) for v in file_graph.values()) if isinstance(file_graph, dict) else 0
raw_edge_count = len(deps)

# --- 4. Promotion Logs ---
master = load_json(MASTER_TASKS)
promotions = [t for t in master if t.get('ref') == 'PROMOTE']
recent_promotes = promotions[-10:] if len(promotions) > 10 else promotions

# --- 5. FORGE Oversight Delegations ---
delegations = []
if FORGE_MD.exists():
    forge_text = FORGE_MD.read_text()
    in_table = False
    for line in forge_text.split('\n'):
        if '## Active Delegations' in line:
            in_table = True
            continue
        if in_table and line.startswith('|') and not line.startswith('| Task'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                delegations.append({
                    'task': parts[0],
                    'agent': parts[1],
                    'account': parts[2],
                    'status': parts[3],
                    'sandbox': parts[4] if len(parts) > 4 else ''
                })
        if in_table and not line.startswith('|'):
            break

# --- 6. Readiness Scores (for staged files) ---
entries = load_llm_index()
funcs = load_jsonl(FUNC_INDEX)

# Determine "staged" files: those in cli-synthegration/workspace/staging/ or harmonizer-prod_cli/workspace/
staged_files = [p for p, e in entries.items() if 'workspace/staging/' in p or 'harmonizer-prod_cli/workspace/' in p]

def compute_readiness(file_path):
    """Score 0-100 based on run_history, deps, and recency."""
    score = 50  # baseline
    # Bump for each PASS verdict on this file
    passes = [e for e in run_history if e.get('target_file') == file_path and e.get('verdict','').upper() == 'PASS']
    fails  = [e for e in run_history if e.get('target_file') == file_path and e.get('verdict','').upper() == 'FAIL']
    score += len(passes) * 10
    score -= len(fails) * 15
    # Bump for high 'by' count (many dependents → more critical, but riskier if changed)
    by = entries.get(file_path, {}).get('by', 0)
    if by > 5: score += 10
    if by > 10: score += 5
    # Clamp
    return max(0, min(100, score))

readiness_scores = {}
for f in staged_files:
    readiness_scores[f] = compute_readiness(f)
ripe_files = [f for f, s in readiness_scores.items() if s >= 80]

# --- 6b. Impact Scores (from file_graph.json) ---
impact_scores = {}
if file_graph:
    reverse_graph = defaultdict(set)
    for src, targets in file_graph.items():
        for tgt in targets:
            reverse_graph[tgt].add(src)
    state_file = MAP / 'foresight_impact_checkpoint.state'
    br = BatchResumer(state_file, len(staged_files), flush_every=50)
    for f, i, is_checkpoint in br.process(staged_files):
        # Count direct + transitive dependents (BFS up to 3 hops)
        visited = set()
        queue = [(f, 0)]
        count = 0
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > 3:
                continue
            visited.add(current)
            if current != f:
                count += 1
            for dep in reverse_graph.get(current, []):
                if dep not in visited:
                    queue.append((dep, depth + 1))
        impact_scores[f] = count
        if is_checkpoint:
            br.checkpoint()
    br.finalize()

# --- 7. Bottleneck Analysis ---
# Find blocked sprints with the most files/agents waiting
bottlenecks = []
for s in blocked:
    # Count how many other sprints or tasks depend on this (via master_tasks.json deps)
    # For now, simple heuristic: if blocker contains "header gate" or "threshold", it's a tech bottleneck
    impact = 'high' if any(w in s.get('blocker','').lower() for w in ['gate', 'auth', 'token', 'threshold']) else 'medium'
    bottlenecks.append({
        'id': s['id'],
        'name': s['name'],
        'blocker': s.get('blocker',''),
        'impact': impact
    })

# --- 8. Agent Workload ---
agent_tasks = Counter()
for d in delegations:
    if d['status'] not in ('⚪ Queued', '🟡 Spec drafted', '🟢 Ready'):
        agent_tasks[d['agent']] += 1
# Also count from master_tasks
for t in master:
    if t.get('status') in ('pending', 'in-progress'):
        agent = t.get('assigned_agent','')
        if agent:
            agent_tasks[agent] += 1

# Standard deviation of workloads
counts = list(agent_tasks.values())
if counts:
    mean = sum(counts) / len(counts)
    variance = sum((c - mean)**2 for c in counts) / len(counts)
    workload_std = round(variance ** 0.5, 2)
else:
    workload_std = 0

# --- Assemble Output ---
foresight = {
    "generated": datetime.now(timezone.utc).isoformat(),
    "router_agent_hook": "python3 ~/workspace/llm_map/router_agent.py --foresight",
    "run_history": {
        "total": total_runs,
        "pass": pass_count,
        "fail": fail_count,
        "pass_rate": round(pass_count / total_runs * 100, 1) if total_runs else 0
    },
    "sprints": {
        "total": len(sprints),
        "blocked": len(blocked),
        "active": len(active),
        "resolved": len(resolved),
        "bottlenecks": bottlenecks
    },
    "dependencies": {
        "raw_edges": raw_edge_count,
        "resolved_edges": resolved_edge_count,
        "resolution_rate": round(resolved_edge_count / raw_edge_count * 100, 1) if raw_edge_count else 0
    },
    "promotions": {
        "total": len(promotions),
        "recent": recent_promotes
    },
    "delegations": delegations,
    "impact": {
        "blast_radii": impact_scores,
        "max_blast": max(impact_scores.values()) if impact_scores else 0
    },
    "readiness": {
        "staged_files_count": len(staged_files),
        "scores": readiness_scores,
        "ripe_for_promotion": ripe_files
    },
    "agent_workload": {
        "per_agent": dict(agent_tasks),
        "std_dev": workload_std,
        "balanced": workload_std < 1.5
    },
    "effectiveness_baseline": {
        "router_query_count": 0,          # will be incremented by router_agent.py --foresight
        "promotion_success_rate": 0,
        "impact_prediction_accuracy": 0,
        "bloat_predetection_rate": 0,
        "bottleneck_resolution_hours": 0
    }
}

with open(FORESIGHT_OUT, 'w') as f:
    json.dump(foresight, f, indent=2)

print("✅ foresight_state.json written.")
print(f"   Staged files: {len(staged_files)}")
print(f"   Ripe for promotion: {len(ripe_files)}")
print(f"   Bottlenecks: {len(bottlenecks)}")
print(f"   Agent workload std dev: {workload_std}")
