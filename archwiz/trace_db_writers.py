import os

HOME = os.path.expanduser("~")
DBS = [
    "workspace/local_repo.db",
    "workspace/llm_map/local_repo.db",
    "workspace/llm_map/reliability.db",
    "termux-multi-agent/local_repo.db",
    "harmony_hub/registry.db",
    "synthegration-cli/local_repo.db",
    "archwiz/lexicon.db",
]
SRC_DIRS = [
    "workspace", "cli-synthegration", "harmony_hub", "archwiz",
    "termux-multi-agent", "synthegration-cli", "deepcli", "deepseek-cli"
]
EXCLUDE = {'.git','node_modules','__pycache__','.hermes','browser-data','Cache','GPUCache','chunks','.cache'}
SRC_EXTS = {'.py','.sh','.js'}

src_files = []
for d in SRC_DIRS:
    dp = os.path.join(HOME, d)
    if not os.path.isdir(dp):
        continue
    for root, dirs, files in os.walk(dp, followlinks=False):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith('.')]
        for f in files:
            if os.path.splitext(f)[1].lower() in SRC_EXTS:
                fp = os.path.join(root, f)
                try:
                    if os.path.getsize(fp) > 500_000:
                        continue
                except:
                    continue
                src_files.append(fp)

for db_rel in DBS:
    db_full = os.path.join(HOME, db_rel)
    if not os.path.exists(db_full):
        continue
    bn = os.path.basename(db_rel)
    print(f"\n=== {db_rel} ===")
    found = False
    for src in src_files:
        try:
            with open(src, 'r', errors='ignore') as f:
                content = f.read()
            if bn in content or db_rel in content:
                print(f"  -> {os.path.relpath(src, HOME)}")
                found = True
        except:
            pass
    if not found:
        print("  (no source references found)")
