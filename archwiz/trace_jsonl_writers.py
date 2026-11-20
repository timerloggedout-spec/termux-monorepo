import os, glob

HOME = os.path.expanduser("~")
LLM_MAP = os.path.join(HOME, "workspace/llm_map")
SRC_DIRS = [
    os.path.join(HOME, "workspace"),
    os.path.join(HOME, "cli-synthegration"),
]
EXCLUDE = {'.git','node_modules','__pycache__','.hermes','browser-data','Cache','GPUCache'}
SRC_EXTS = {'.py','.sh'}

src_files = []
for d in SRC_DIRS:
    if not os.path.isdir(d):
        continue
    for root, dirs, files in os.walk(d, followlinks=False):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for f in files:
            if os.path.splitext(f)[1].lower() in SRC_EXTS:
                fp = os.path.join(root, f)
                try:
                    if os.path.getsize(fp) > 500_000:
                        continue
                except:
                    continue
                src_files.append(fp)

jsonl_files = glob.glob(os.path.join(LLM_MAP, "*.jsonl"))
for jf in jsonl_files:
    bn = os.path.basename(jf)
    print(f"\n=== {bn} ===")
    found = False
    for src in src_files:
        try:
            with open(src, 'r', errors='ignore') as f:
                if bn in f.read():
                    print(f"  -> {os.path.relpath(src, HOME)}")
                    found = True
        except:
            pass
    if not found:
        print("  (no reference found)")
