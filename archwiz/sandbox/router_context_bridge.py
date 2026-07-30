#!/usr/bin/env python3
"""
🪄 Router‑Context Bridge
    --query "text" [--session <id>] [--new-session]

1. Uses provenance to find working files for the session.
2. Weights query tokens by those files.
3. Calls router_agent.score_projects() to find the best project/agent.
4. If --new-session, generates a complete new‑session prompt:
   - working files + dependency neighbourhood (file_graph)
   - token‑similar files (Jaccard)
   - multi‑session timeline for each file (all provenance entries)
   - code blocks from reference session(s)
5. Outputs the prompt ready to paste into deepcli.
"""

import json, sys, os, re, argparse, hashlib
from pathlib import Path
from collections import Counter

HOME = Path.home()

# ------------------------------------------------------------
# Lightweight imports – everything is already in the ecosystem
# ------------------------------------------------------------
sys.path.insert(0, str(HOME / "cli-synthegration/workspace/provenance"))
from provenance_api import _load, search, all_files as prov_all_files     # noqa: E402

sys.path.insert(0, str(HOME / "workspace/llm_map"))
from router_agent import score_projects, load_index, load_funcs, suggest_agent  # noqa: E402

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def load_dependency_graph():
    fg = HOME / "workspace/llm_map/file_graph.json"
    if fg.exists():
        return json.loads(fg.read_text())
    return {}

def expand_deps(files, dep_graph, hops=1):
    expanded = set(files)
    queue = list(files)
    for _ in range(hops):
        new_neighbors = set()
        for f in queue:
            if f in dep_graph:
                new_neighbors.update(dep_graph[f])
            for src, imports in dep_graph.items():
                if f in imports:
                    new_neighbors.add(src)
        expanded.update(new_neighbors)
        queue = list(new_neighbors)
    return sorted(expanded)

def token_jaccard(text1, text2):
    t1 = set(text1[:3000].split())
    t2 = set(text2[:3000].split())
    union = len(t1 | t2)
    return len(t1 & t2) / union if union > 0 else 0.0

def find_similar(target_path, candidates, top_n=3, threshold=0.03):
    try:
        target_text = (HOME / target_path).read_text()
    except:
        return []
    scores = []
    for c in candidates:
        if c == target_path:
            continue
        try:
            c_text = (HOME / c).read_text()
        except:
            continue
        sim = token_jaccard(target_text, c_text)
        if sim >= threshold:
            scores.append((c, sim))
    scores.sort(key=lambda x: -x[1])
    return scores[:top_n]

def get_multi_session_timeline(file_path):
    """Return all provenance entries for a file, sorted by timestamp."""
    prov = {}
    prov_file = HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json"
    if prov_file.exists():
        prov = json.loads(prov_file.read_text())
    entries = prov.get(file_path, [])
    entries.sort(key=lambda e: e.get("timestamp_utc", ""))
    return entries

def extract_code_blocks_from_session(sid, max_blocks=5):
    """Get first N code blocks from session store."""
    msgs = []
    for p in [HOME / ".deepcli/session_store" / f"{sid}.json",
              HOME / ".deepcli/session_store/primary" / f"{sid}.json"]:
        if p.exists():
            msgs = json.loads(p.read_text())
            break
    blocks = []
    if isinstance(msgs, list):
        for mi, m in enumerate(msgs):
            content = m.get("content", "") or ""
            for bi, match in enumerate(re.finditer(r"```(?:\w+)?\n(.*?)\n```", content, re.DOTALL)):
                code = match.group(1).strip()
                blocks.append({"msg_idx": mi, "block_idx": bi,
                               "hash": hashlib.sha256(code.encode()).hexdigest()[:16],
                               "code": code[:500], "role": m.get("role","?")})
    return blocks[:max_blocks]

# ------------------------------------------------------------
# Main bridge logic
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Router‑Context Bridge")
    parser.add_argument("--query", required=True, help="The task/question to route")
    parser.add_argument("--session", help="Reference session ID (for working files)")
    parser.add_argument("--new-session", action="store_true",
                        help="Generate a full new‑session prompt")
    parser.add_argument("--similar", type=int, default=3,
                        help="Top‑N similar files to include")
    args = parser.parse_args()

    query = args.query
    sid = args.session

    # 1. Get working files for this session
    working_files = []
    if sid:
        _load()  # initialise provenance data
        results = search(sid)  # returns list of (file, entry)
        working_files = [f for f, _ in results]

    # 2. Weight query tokens by working files
    tokens = re.findall(r"[a-zA-Z0-9_/.-]+", query.lower())
    for f in working_files:
        # add filename tokens as extra query weight
        tokens.extend(re.findall(r"[a-zA-Z0-9_/.-]+", f.lower()))

    # 3. Route to best project/agent
    entries = load_index()
    funcs = load_funcs()
    scores = score_projects(query, entries, funcs)
    if not scores or max(scores.values()) == 0:
        print("No matching project found.")
        return
    best_project, score = scores.most_common(1)[0]
    agent_name, agent_cmd = suggest_agent(best_project)

    print(f"# 🧭 Route for: {query}")
    print(f"## Best Project: {best_project} (score {score})")
    print(f"## Suggested Agent: {agent_name}")
    print(f"## Command: {agent_cmd}\n")

    if not args.new_session:
        return

    # 4. Build new‑session prompt
    dep_graph = load_dependency_graph()
    prov_files = prov_all_files() if callable(prov_all_files) else []; all_known = list(dep_graph.keys()) + prov_files

    # Expand working files by dependencies
    expanded = expand_deps(working_files, dep_graph, hops=1)

    # Find token‑similar files for each working file
    similar_set = set()
    for wf in working_files[:5]:  # limit to avoid too many
        sims = find_similar(wf, all_known, top_n=args.similar)
        for f, _ in sims:
            similar_set.add(f)

    all_files = sorted(set(expanded).union(similar_set))

    # Build the prompt
    prompt = f"System: You are a l33T 🪄 ArchWizard coder.\n"
    prompt += f"Task: {query}\n\n"

    prompt += "## Context Files\n"
    for f in all_files[:20]:
        prompt += f"- {f}\n"
        # Show multi‑session timeline for key files
        if f in working_files:
            timeline = get_multi_session_timeline(f)
            if len(timeline) > 1:
                prompt += f"  (touched by {len(timeline)} sessions: "
                prompt += ", ".join(e.get("session","")[:8]+"..." for e in timeline[:4])
                prompt += ")\n"
    prompt += "\n"

    # Include code blocks from the reference session
    if sid:
        blocks = extract_code_blocks_from_session(sid, max_blocks=3)
        if blocks:
            prompt += "## Reference Code Blocks\n"
            for b in blocks:
                prompt += f"```\n{b['code']}\n```\n"

    prompt += f"\n# Task\n{query}\n\n# Response\n"

    print("## Generated New‑Session Prompt:\n")
    print(prompt)

if __name__ == "__main__":
    main()
