#!/usr/bin/env python3
"""
🪄 ArchW1z Graph & Tensor Visualizer — Codex, AST, File Deps
Reads the ecosystem's core indices and produces:
  1. Directed file dependency graph (adjacency matrix + Graphviz PNG)
  2. File‑file AST similarity matrix (Jaccard on snippet hashes)
  3. Session‑code block incidence matrix
All outputs go to:
  ~/storage/downloads/_doing/_1-build/DeepSeek/exports/archwiz_graphs/
(creates the directory automatically)
"""

import json, os, sys, itertools, subprocess, tempfile
from pathlib import Path

HOME = Path(os.environ["HOME"])

# --- Data source paths -------------------------------------------------
FILE_GRAPH      = HOME / "workspace/llm_map/file_graph.json"
FUNC_INDEX      = HOME / "workspace/llm_map/func_index.jsonl"
AST_SNIPPETS    = HOME / "workspace/llm_map/ast_snippets.json"
CODEX_INDEX     = HOME / "cli-synthegration/codex/codex_index.json"

# Output directory – visible in Android Gallery via Downloads
OUT_DIR = HOME / "storage/downloads/_doing/_1-build/DeepSeek/exports/archwiz_graphs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
def load_json(path):
    if not path.exists():
        print(f"⚠️  Missing: {path}")
        return None
    with open(path) as f:
        return json.load(f)

def load_jsonl(path):
    if not path.exists():
        print(f"⚠️  Missing: {path}")
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

# ======================================================================
# 1. FILE DEPENDENCY GRAPH → adjacency matrix + Graphviz PNG
# ======================================================================
print("=" * 60)
print("1. FILE DEPENDENCY GRAPH")
print("=" * 60)

fg = load_json(FILE_GRAPH)
if fg is None:
    sys.exit(1)

# Auto‑detect format: dict {file: [imports]} or list of {file, imports}
if isinstance(fg, dict):
    file_deps = fg
elif isinstance(fg, list):
    file_deps = {}
    for item in fg:
        file_deps[item["file"]] = item.get("imports", [])
else:
    print("❌ Unknown file_graph.json format")
    sys.exit(1)

files = set(file_deps.keys())
for imports in file_deps.values():
    files.update(imports)
files = sorted(files)
n_files = len(files)
file2idx = {f: i for i, f in enumerate(files)}

adj = [[0] * n_files for _ in range(n_files)]
edges = []
for src, imports in file_deps.items():
    s_idx = file2idx[src]
    for tgt in imports:
        if tgt in file2idx:
            adj[s_idx][file2idx[tgt]] = 1
            edges.append((src, tgt))

print(f"Nodes: {n_files} files")
print(f"Edges: {len(edges)} dependencies")

# Save adjacency matrix
try:
    import numpy as np
    mat = np.array(adj, dtype=np.uint8)
    np.savez_compressed(OUT_DIR / "file_deps_adj.npz", matrix=mat, files=files)
    print("✓ Saved compressed matrix → file_deps_adj.npz")
except ImportError:
    pass

with open(OUT_DIR / "file_deps_adj.csv", "w") as f:
    f.write("," + ",".join(f'"{fn}"' for fn in files) + "\n")
    for i, row in enumerate(adj):
        f.write(f'"{files[i]}",' + ",".join(str(x) for x in row) + "\n")
print("✓ Saved CSV matrix → file_deps_adj.csv")

# Generate Graphviz PNG (top 50 files by degree)
try:
    import networkx as nx
    from networkx.drawing.nx_pydot import write_dot

    G = nx.DiGraph()
    G.add_nodes_from(files)
    G.add_edges_from(edges)
    top_nodes = sorted(files, key=lambda f: G.degree(f), reverse=True)[:50]
    H = G.subgraph(top_nodes)

    dot_path = OUT_DIR / "file_deps_graph.dot"
    png_path = OUT_DIR / "file_deps_graph.png"
    write_dot(H, str(dot_path))
    subprocess.run(["dot", "-Kfdp", "-Tpng", f"-Gdpi=150", "-o", str(png_path), str(dot_path)], check=True)
    print("✓ Saved graph plot → file_deps_graph.png (Graphviz)")
except ImportError:
    print("⚠️  networkx not available, skipping graph plot")
except Exception as e:
    print(f"⚠️  Graphviz rendering failed: {e}")

# ======================================================================
# 2. AST SNIPPET SIMILARITY (Jaccard) → matrix only
# ======================================================================
print("\n" + "=" * 60)
print("2. AST SNIPPET SIMILARITY (Jaccard on hashes)")
print("=" * 60)

ast_data = load_json(AST_SNIPPETS)
if ast_data and isinstance(ast_data, dict):
    file_sets = {}
    for fpath, snippets in ast_data.items():
        if isinstance(snippets, list):
            file_sets[fpath] = set(s["hash"] for s in snippets if "hash" in s)
        else:
            file_sets[fpath] = set()

    paths = sorted(file_sets.keys())
    if len(paths) >= 2:
        m = len(paths)
        jaccard = [[0.0]*m for _ in range(m)]
        for i, j in itertools.combinations_with_replacement(range(m), 2):
            si = file_sets[paths[i]]
            sj = file_sets[paths[j]]
            inter = len(si & sj)
            union = len(si | sj)
            val = inter / union if union > 0 else 0.0
            jaccard[i][j] = val
            jaccard[j][i] = val

        print(f"Files with AST snippets: {m}")
        try:
            import numpy as np
            mat = np.array(jaccard)
            np.savez_compressed(OUT_DIR / "ast_sim_matrix.npz", matrix=mat, files=paths)
            print("✓ Saved similarity matrix → ast_sim_matrix.npz")
        except ImportError:
            pass
        with open(OUT_DIR / "ast_sim_matrix.csv", "w") as f:
            f.write("," + ",".join(f'"{p}"' for p in paths) + "\n")
            for i, row in enumerate(jaccard):
                f.write(f'"{paths[i]}",' + ",".join(f"{v:.4f}" for v in row) + "\n")
        print("✓ Saved CSV matrix → ast_sim_matrix.csv")
    else:
        print(f"⚠️  Need at least 2 files for similarity, got {len(paths)}")
else:
    print("⚠️  No AST snippets found, skipping.")

# ======================================================================
# 3. SESSION‑CODE BLOCK INCIDENCE MATRIX
# ======================================================================
print("\n" + "=" * 60)
print("3. SESSION‑CODE BLOCK INCIDENCE MATRIX")
print("=" * 60)

codex = load_json(CODEX_INDEX)
if codex:
    pointers = codex.get("pointers", [])
    if not pointers:
        print("⚠️  codex_index.json has no pointers")
    else:
        # The pointer keys are: 'sid', 'ch'
        sessions = sorted(set(p["sid"] for p in pointers))
        hashes   = sorted(set(p["ch"] for p in pointers))
        ns = len(sessions)
        nh = len(hashes)
        print(f"Sessions: {ns}, unique code hashes: {nh}")
        if ns > 0 and nh > 0:
            s2i = {s: i for i, s in enumerate(sessions)}
            h2i = {h: i for i, h in enumerate(hashes)}
            inc = [[0]*nh for _ in range(ns)]
            for p in pointers:
                inc[s2i[p["sid"]]][h2i[p["ch"]]] = 1
            try:
                import numpy as np
                mat = np.array(inc, dtype=np.uint8)
                np.savez_compressed(OUT_DIR / "session_codex_inc.npz",
                                    matrix=mat, sessions=sessions, hashes=hashes)
                print("✓ Saved compressed incidence matrix → session_codex_inc.npz")
            except ImportError:
                pass
            # Sparse CSV for portability
            with open(OUT_DIR / "session_codex_inc.csv", "w") as f:
                f.write("session_id,code_hash\n")
                for p in pointers:
                    f.write(f"{p['sid']},{p['ch']}\n")
            print("✓ Saved sparse CSV → session_codex_inc.csv")
else:
    print("⚠️  codex_index.json missing, skipping.")

# ======================================================================
# 4. FUNCTION INDEX SUMMARY
# ======================================================================
print("\n" + "=" * 60)
print("4. FUNCTION INDEX SUMMARY")
print("=" * 60)

func_count = 0
file_set = set()
for entry in load_jsonl(FUNC_INDEX):
    func_count += 1
    file_set.add(entry["file"])
print(f"Total definitions: {func_count}  |  unique files: {len(file_set)}")

print(f"\n✅ All outputs saved in: {OUT_DIR}")
