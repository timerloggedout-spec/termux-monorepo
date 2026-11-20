#!/usr/bin/env python3
"""🪄 AETHER — ArchWiz Ecosystem Command Engine"""

import sys, os, subprocess, json

HOME = os.path.expanduser("~")
LLM_MAP = os.path.join(HOME, "workspace/llm_map")
ARCHWIZ = os.path.join(HOME, "archwiz")

def run(cmd, cwd=None):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return p.stdout.strip(), p.stderr.strip(), p.returncode

# ── Core commands (unchanged) ──
def cmd_map(args):
    profile = os.environ.get("LLM_PROFILE", "default")
    print(f"⚡ Building map with profile [{profile}]...")
    out, err, rc = run("python3 build_final_all_profile.py", cwd=LLM_MAP)
    if rc != 0: print("❌ Map build failed:", err); return
    run("./generate_system_map.sh", cwd=LLM_MAP)
    run("python3 func_indexer.py", cwd=LLM_MAP)
    print("✅ Map + func index ready.")

def cmd_dep(args):
    if not args: print("Usage: aether dep <file>"); return
    out, _, _ = run(f"bash {LLM_MAP}/depgraph.sh {args[0]}")
    print(out)

def cmd_funcfind(args):
    if not args: print("Usage: aether funcfind <pattern>"); return
    pattern = args[0]
    jq = f'''jq -r 'select(.file | test("{pattern}")) | "\\(.name) \t line \\(.line) \t \\(.sig[:60])"' {LLM_MAP}/func_index.jsonl'''
    out, _, _ = run(jq)
    print(out)

def cmd_dispatch(args):
    sys.path.insert(0, LLM_MAP)
    from dispatch_task import main as dm
    sys.argv = ["dispatch_task.py"] + args; dm()

def cmd_promote(args):
    sys.path.insert(0, LLM_MAP)
    from promote import main as pm
    sys.argv = ["promote.py"] + args; pm()

def cmd_archaeo(args):
    sys.path.insert(0, LLM_MAP)
    from archaeologist import main as am
    sys.argv = ["archaeologist.py"] + args; am()

def cmd_oracle(args):
    sys.path.insert(0, LLM_MAP)
    from impact_oracle import main as om
    sys.argv = ["impact_oracle.py"] + args; om()

def cmd_foresight(args):
    sys.path.insert(0, LLM_MAP)
    from foresight_collect import main as fm
    sys.argv = ["foresight_collect.py"] + args; fm()

def cmd_tui(args): run("~/archwiz/archwiz.sh", cwd=ARCHWIZ)

def cmd_truth(args):
    sys.path.insert(0, LLM_MAP)
    from generate_diff_report import main as tm
    sys.argv = ["generate_diff_report.py"] + args; tm()

def cmd_route(args):
    sys.path.insert(0, LLM_MAP)
    from router_agent import main as rm
    sys.argv = ["router_agent.py"] + args; rm()

def cmd_manifest(args):
    run(f"python3 {ARCHWIZ}/build_data_flow_manifest.py")

def cmd_rw(args):
    if not args: print("Usage: aether rw <data_file>"); return
    rw_map = os.path.join(HOME, "tmp/rw_map_v2.json")
    if not os.path.exists(rw_map): print("Run aether manifest first."); return
    with open(rw_map) as f: data = json.load(f)
    target = args[0]
    if target in data:
        for src, flag in data[target]: print(f"{flag}  {src}")
    else:
        for k in data:
            if target in k:
                for src, flag in data[k]: print(f"{flag}  {src}  (from {k})")
                return
        print("No RW data found.")

def cmd_duplicates(args):
    manifest = os.path.join(ARCHWIZ, "DATA_FLOW_MANIFEST.md")
    if not os.path.exists(manifest): print("Run aether manifest first."); return
    with open(manifest) as f:
        for line in f:
            if "Duplicate(s):" in line: print(line.strip())

def cmd_aliases(args):
    run(f"python3 {ARCHWIZ}/audit_aliases.py")

def cmd_xref(args):
    run(f"python3 {ARCHWIZ}/xref_exports.py")

def cmd_bookmark(args):
    run(f"python3 {ARCHWIZ}/lexicon_mark.py " + " ".join(args))

def cmd_timeline(args):
    run(f"python3 {ARCHWIZ}/timeline_editor.py")

def cmd_lexicon(args):
    run(f"python3 {HOME}/workspace/compression_sandbox/cedrlang/cid.py " + " ".join(args))

# ── NEW: Reindex pipeline ──
def cmd_reindex(args):
    steps = ["bloat", "map", "func", "manifest", "tools", "fts"]
    if args and args[0] in steps:
        steps = [args[0]]
    for s in steps:
        rc = 0
        if s == "bloat":
            script = os.path.join(LLM_MAP, "discover_bloat.sh")
            if os.path.exists(script):
                _, _, rc = run(f"bash {script}", cwd=LLM_MAP)
            else:
                print("⚠️ discover_bloat.sh missing, skipping.")
        elif s == "map":
            cmd_map([])
        elif s == "func":
            _, _, rc = run("python3 func_indexer.py", cwd=LLM_MAP)
        elif s == "manifest":
            run(f"python3 {ARCHWIZ}/build_data_flow_manifest.py")
        elif s == "tools":
            run(f"python3 {ARCHWIZ}/build_tool_index.py")
        elif s == "fts":
            db = os.path.join(HOME, "termux-multi-agent/local_repo.db")
            if os.path.exists(db):
                _, _, rc = run(f"sqlite3 {db} \"INSERT INTO messages_fts(messages_fts) VALUES('rebuild');\"")
        if rc != 0 and s != "bloat":
            print(f"❌ Stopped at {s}")
            return
    run(f"python3 {ARCHWIZ}/build_reference_hub.py")
    print("✅ Full reindex complete. Reference Hub updated.")

# ── Main ──
HELP = """🪄 AETHER — ArchWiz Ecosystem Command Engine
Commands:
  map           Rebuild master index + functions
  dep <file>    Dependency tree
  funcfind <p>  Function search
  dispatch [t]  Execute autonomous task
  promote <f>   FORGE_OVERSIGHT promotion
  archaeo <f>   Full lifecycle timeline
  oracle <f>    Impact analysis
  foresight     Aggregate metrics
  tui           Launch dashboard
  truth         Diff report
  route <q>     Route to agent
  manifest      Rebuild data‑flow manifest
  rw <file>     Read/write references
  duplicates    List duplicate files
  aliases       Audit .zshrc
  xref          Cross‑reference exports
  bookmark      Scan keywords/milestones
  timeline      Interactive timeline editor
  lexicon       CID pointer lookup
  reindex [bloat|map|func|manifest|tools|fts]   Run full reindex pipeline
"""

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(HELP); return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    cmds = {
        "map": cmd_map, "dep": cmd_dep, "funcfind": cmd_funcfind,
        "dispatch": cmd_dispatch, "promote": cmd_promote,
        "archaeo": cmd_archaeo, "oracle": cmd_oracle,
        "foresight": cmd_foresight, "fore": cmd_foresight,
        "tui": cmd_tui, "truth": cmd_truth, "route": cmd_route,
        "manifest": cmd_manifest, "rw": cmd_rw,
        "duplicates": cmd_duplicates, "aliases": cmd_aliases,
        "xref": cmd_xref, "bookmark": cmd_bookmark,
        "timeline": cmd_timeline, "lexicon": cmd_lexicon,
        "reindex": cmd_reindex,
    }
    if cmd in cmds:
        cmds[cmd](args)
    else:
        print(f"Unknown command: {cmd}. Run 'aether --help'.")

if __name__ == "__main__":
    main()
