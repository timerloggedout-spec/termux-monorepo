import os, sys

HOME = os.path.expanduser("~")
SRC_DIRS = [
    HOME + "/workspace",
    HOME + "/cli-synthegration",
    HOME + "/harmony_hub",
    HOME + "/archwiz",
    HOME + "/deepcli",
    HOME + "/deepseek-cli",
    HOME + "/termux-multi-agent",
    HOME + "/synthegration-cli",
    HOME + "/commingle-swarm",
    HOME + "/_1-Projects",
]
# Excluded subdirectories
EXCLUDE = {'.git','node_modules','__pycache__','.hermes','browser-data','Cache','GPUCache','chunks','.cache'}

# Read data file paths
with open(HOME + "/tmp/data_files_list.txt") as f:
    data_paths = [line.strip() for line in f if line.strip()]

# Only search source files (limit to common extensions to speed up)
SRC_EXTS = {'.py','.sh','.js','.ts','.rs','.toml','.yaml','.yml','.json','.md','.txt'}

# Build a mapping: relative_data_path -> list of source files that mention it
flow = {}  # path -> list of source files

# Walk source dirs
src_files = []
for d in SRC_DIRS:
    if not os.path.isdir(d):
        continue
    for root, dirs, files in os.walk(d):
        # Prune excluded dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SRC_EXTS:
                src_files.append(os.path.join(root, f))

print(f"Scanning {len(src_files)} source files...")
# For performance, we'll read each source file once and check against all data paths.
# To avoid O(N*M), we'll use a simpler method: search each source file for any occurence of the data path basename.
# But for full path matching, we can check substring.
# We'll do: for each source file, read content, then for each data path, if path in content, add to flow.
# This is M*N but for 2390 paths and maybe 2000 source files, it's okay (4.8M checks, each a string 'in' check).

for i, src in enumerate(src_files):
    if i % 500 == 0:
        print(f"  {i}/{len(src_files)}...")
    try:
        with open(src, 'r', errors='ignore') as f:
            content = f.read()
    except:
        continue
    for dp in data_paths:
        # Check full path (e.g., "synthegration_exports/...") or just basename
        if dp in content:
            flow.setdefault(dp, []).append(src)

# Write mapping
out_path = HOME + "/tmp/data_flow_map.txt"
with open(out_path, 'w') as f:
    for dp in sorted(flow.keys()):
        f.write(f"\n=== {dp} ===\n")
        for src in sorted(set(flow[dp])):
            f.write(f"  -> {src}\n")
print(f"Done. Found {len(flow)} data files referenced in source. Output: {out_path}")
