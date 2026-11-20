import json, os, hashlib, sys

HOME = os.path.expanduser("~")
tv_path = os.path.join(HOME, "cli-synthegration/workspace/provenance/true_versions.json")
if not os.path.exists(tv_path):
    print("true_versions.json not found.")
    sys.exit(1)

with open(tv_path) as f:
    tv = json.load(f)

# Build hash index from true_versions (key is hash, value is list of known paths)
hash_ref = {}  # hash -> list of {"path", "session", "node"}
for path, entries in tv.items():
    for e in entries:
        h = e.get("hash")
        if h:
            # Normalize hash (some might be truncated, some full)
            h = h.strip().lower()
            hash_ref.setdefault(h, []).append({"path": path, "session": e.get("session"), "node": e.get("node_id")})

# Scan target directories
targets = [
    os.path.join(HOME, "synthegration_exports"),
    os.path.join(HOME, "storage/downloads/synthegration_exports"),
    os.path.join(HOME, "storage/downloads/synthegration_batch_export"),
]
# Also include the _doing subdirectories if they contain session exports
doing = os.path.join(HOME, "storage/downloads/_doing")
for sub in ["_1-build/DeepSeek/exports", "downloads2sort", "referenceTemplates"]:
    path = os.path.join(doing, sub)
    if os.path.isdir(path):
        targets.append(path)

for target in targets:
    if not os.path.isdir(target):
        continue
    print(f"\n=== {target} ===")
    for root, dirs, files in os.walk(target):
        for fn in files:
            fpath = os.path.join(root, fn)
            # Compute a quick sha256 of the file content
            try:
                size = os.path.getsize(fpath)
                if size > 5 * 1024 * 1024:  # skip large >5MB
                    continue
                with open(fpath, "rb") as fh:
                    content = fh.read()
                h = hashlib.sha256(content).hexdigest()
                # Check exact full hash match
                if h in hash_ref:
                    refs = hash_ref[h]
                    print(f"  MATCH: {fpath}")
                    for ref in refs:
                        print(f"    -> known as: {ref['path']}  (session {ref['session']})")
                # Also check truncated? We'll skip for now.
            except Exception as e:
                pass
