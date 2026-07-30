"""Reindex pipeline: bloat → map → func → manifest → tools → fts"""

import subprocess, sys, os
HOME = os.path.expanduser("~")
ARCHWIZ = os.path.join(HOME, "archwiz")
LLM_MAP = os.path.join(HOME, "workspace/llm_map")

def run(cmd, cwd=None):
    print(f"⚡ {cmd}")
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr[-200:])
    else:
        print(p.stdout[:200])
    return p.returncode

def step_bloat():
    # Run discover_bloat.sh if exists
    script = os.path.join(LLM_MAP, "discover_bloat.sh")
    if os.path.exists(script):
        return run(f"bash {script}", cwd=LLM_MAP)
    else:
        print("⚠️ discover_bloat.sh not found, skipping.")
        return 0

def step_map():
    return run("python3 build_final_all_profile.py", cwd=LLM_MAP)

def step_func():
    return run("python3 func_indexer.py", cwd=LLM_MAP)

def step_manifest():
    return run(f"python3 {ARCHWIZ}/build_data_flow_manifest.py", cwd=ARCHWIZ)

def step_tools():
    return run(f"python3 {ARCHWIZ}/build_tool_index.py", cwd=ARCHWIZ)

def step_fts():
    db = os.path.join(HOME, "termux-multi-agent/local_repo.db")
    if os.path.exists(db):
        return run(f"sqlite3 {db} \"INSERT INTO messages_fts(messages_fts) VALUES('rebuild');\"")
    else:
        print("⚠️ DB not found.")
        return 0

STEPS = {
    "bloat": step_bloat,
    "map": step_map,
    "func": step_func,
    "manifest": step_manifest,
    "tools": step_tools,
    "fts": step_fts,
}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in STEPS:
        STEPS[sys.argv[1]]()
    else:
        for name, step in STEPS.items():
            rc = step()
            if rc != 0 and name != "bloat":
                print(f"❌ Stopped at {name}")
                break
        print("✅ Reindex complete.")
