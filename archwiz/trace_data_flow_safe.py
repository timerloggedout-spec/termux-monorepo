import os, sys, time

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
EXCLUDE = {'.git','node_modules','__pycache__','.hermes','browser-data','Cache','GPUCache','chunks','.cache','storage','synthegration_exports','sandbox'}
SRC_EXTS = {'.py','.sh','.js','.ts','.rs','.toml','.yaml','.yml','.json','.md','.txt'}

with open(HOME + "/tmp/data_files_list.txt") as f:
    data_paths = [line.strip() for line in f if line.strip()]

# Only search within source directories, no symlink follow
src_files = []
for d in SRC_DIRS:
    if not os.path.isdir(d):
        continue
    for root, dirs, files in os.walk(d, followlinks=False):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith('.')]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SRC_EXTS:
                fp = os.path.join(root, f)
                try:
                    if os.path.getsize(fp) > 500_000:
                        continue
                except:
                    continue
                src_files.append(fp)

flow = {}
print(f"Scanning {len(src_files)} source files (max 500KB each) for {len(data_paths)} data paths...")
for i, src in enumerate(src_files):
    print(f"\r  {i+1}/{len(src_files)} {os.path.basename(src)[:50]}", end='', flush=True)
    try:
        with open(src, 'r', errors='ignore') as f:
            content = f.read()
    except:
        continue
    for dp in data_paths:
        if dp in content:
            flow.setdefault(dp, []).append(src)

print("\nWriting results...")
with open(HOME + "/tmp/data_flow_map.txt", 'w') as f:
    for dp in sorted(flow.keys()):
        f.write(f"\n=== {dp} ===\n")
        for s in sorted(set(flow[dp])):
            f.write(f"  -> {s}\n")
print(f"Done: {len(flow)} data files matched. Output -> tmp/data_flow_map.txt")
