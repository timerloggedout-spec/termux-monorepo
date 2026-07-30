import os, json, glob, collections, re
from pathlib import Path

HOME = os.path.expanduser("~")
OUT = os.path.join(HOME, "archwiz", "DATA_FLOW_MANIFEST.md")

# ------------------------------------------------------------
# 1. Load central index (JSONL)
# ------------------------------------------------------------
index_path = os.path.join(HOME, "central_index.jsonl")
central = {}  # path -> record
with open(index_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            path = rec.get("path", "")
            if path:
                central[path] = rec
        except:
            pass

# ------------------------------------------------------------
# 2. Load data‑flow mapping from trace script
# ------------------------------------------------------------
flow_map = collections.defaultdict(list)  # path -> list of source scripts
flow_file = os.path.join(HOME, "tmp", "data_flow_map.txt")
if os.path.exists(flow_file):
    current_path = None
    with open(flow_file) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("=== ") and line.endswith(" ==="):
                current_path = line[4:-4].strip()
            elif line.startswith("  -> "):
                src = line[4:].strip()
                if current_path:
                    flow_map[current_path].append(src)
else:
    # fallback: use data_files_list.txt without mapping
    pass

# ------------------------------------------------------------
# 3. Identify writers for common artefacts (JSONL, DB, etc.)
#    from earlier specialized runs
# ------------------------------------------------------------
# We'll extract them from the flow_map; missing ones will be "unknown"

# ------------------------------------------------------------
# 4. Helper: determine project from path
# ------------------------------------------------------------
def project_of(p):
    if p.startswith("workspace/llm_map"): return "llm_map"
    if p.startswith("cli-synthegration"): return "synthegration"
    if p.startswith("harmony_hub"): return "harmony_hub"
    if p.startswith("archwiz"): return "archwiz"
    if p.startswith("deepcli"): return "deepcli"
    if p.startswith("deepseek-cli"): return "deepseek_cli"
    if p.startswith("termux-multi-agent"): return "termux_multi_agent"
    if p.startswith("synthegration-cli"): return "synthegration_cli"
    if p.startswith("synthegration_exports"): return "exports"
    if p.startswith("storage/downloads/synthegration"): return "downloads_exports"
    if p.startswith("storage/downloads/_doing"): return "downloads_doing"
    if p.startswith("commingle-swarm"): return "commingle"
    if p.startswith("_1-Projects"): return "legacy_projects"
    return "other"

# ------------------------------------------------------------
# 5. Build manifest
# ------------------------------------------------------------
lines = []
lines.append("# 🗺️ Complete Data‑Flow Manifest")
lines.append("")
lines.append(f"**Generated:** {__import__('datetime').datetime.now().isoformat()}")
lines.append(f"**Data files indexed:** {len(central)} from central_index.jsonl")
lines.append("")

# Group by project
proj_files = collections.defaultdict(list)
for p in central:
    proj_files[project_of(p)].append(p)

for proj in sorted(proj_files.keys()):
    lines.append(f"## 📁 {proj}")
    lines.append("")
    lines.append("| File | Size | Writers | Duplicates / Notes |")
    lines.append("|------|------|---------|--------------------|")
    for path in sorted(proj_files[proj]):
        rec = central[path]
        size = rec.get("size", "?")
        if isinstance(size, int):
            if size > 1024*1024:
                size_str = f"{size/1024/1024:.1f} MB"
            elif size > 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size} B"
        else:
            size_str = str(size)

        writers = flow_map.get(path, [])
        if not writers:
            # Try to infer from basename
            base = os.path.basename(path)
            for src in flow_map.keys():
                if base in flow_map[src]:
                    writers = flow_map[src]
                    break
        if writers:
            # shorten paths
            writer_list = ", ".join(sorted(set(
                re.sub(r'^' + HOME + '/', '~/', w) for w in writers
            )))[:200]
        else:
            writer_list = "*unknown*"

        # Detect duplicates: same basename in different paths
        base = os.path.basename(path)
        dups = [p2 for p2 in central if p2 != path and os.path.basename(p2) == base]
        dup_note = ""
        if dups:
            dup_note = f"Duplicate(s): {', '.join(dups[:3])}"[:150]

        lines.append(f"| `{path}` | {size_str} | {writer_list} | {dup_note} |")
    lines.append("")

# ------------------------------------------------------------
# 6. Add known directories not in index (browser caches, export dirs)
# ------------------------------------------------------------
extra_dirs = [
    ("deepcli/browser-data", "Chromium cache for deepcli"),
    ("deepseek-cli/browser-data", "Chromium cache for deepseek-cli"),
    ("deepseek-cli/browser-data-account2", "Duplicate browser cache"),
    ("deepseek-cli/browser-data-account2-clean", "Duplicate browser cache"),
    ("deepseek-cli/browser-data-account2-fresh", "Duplicate browser cache"),
    ("deepseek-cli/browser-data-account2-v2", "Duplicate browser cache"),
    ("storage/downloads/synthegration_exports", "UUID‑based blobs (batch_export_all.py)"),
    ("storage/downloads/synthegration_batch_export", "Subset of canonical exports (human names)"),
    ("storage/downloads/_doing/Tallah", "70 MB mixed content"),
    ("storage/downloads/_doing/__1-resources", "740 MB mixed content"),
    ("storage/downloads/_doing/downloads2sort", "792 MB mixed; one file matched true_versions hash"),
    ("storage/downloads/_doing/referenceTemplates", "21 MB; likely duplicate templates"),
    ("cli-synthegration/conv_repo/sessions", "Content‑addressed session store (752 KB)"),
]

lines.append("## 📦 Large Directories (not fully indexed)")
lines.append("")
for dirpath, note in extra_dirs:
    full = os.path.join(HOME, dirpath)
    if os.path.exists(full):
        size = sum(os.path.getsize(p) for root, _, files in os.walk(full) for f in files if os.path.isfile(p := os.path.join(root, f)))
        if size > 1024*1024:
            size_str = f"{size/1024/1024:.1f} MB"
        elif size > 1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size} B"
        lines.append(f"- `{dirpath}` — {size_str} — {note}")
    else:
        lines.append(f"- `{dirpath}` — (not present) — {note}")

# ------------------------------------------------------------
# 7. Write manifest
# ------------------------------------------------------------
with open(OUT, "w") as f:
    f.write("\n".join(lines))

print(f"✅ Manifest written to {OUT}")
