#!/usr/bin/env python3
"""🪄 FORGE — Caveman Ecosystem Command Centre"""

import sys, os, subprocess, json

HOME = os.path.expanduser("~")
LLM_MAP = os.path.join(HOME, "workspace/llm_map")
ARCHWIZ = os.path.join(HOME, "archwiz")

def run(cmd, cwd=None, shell=True):
    p = subprocess.run(cmd, shell=shell, cwd=cwd, capture_output=True, text=True)
    return p.stdout.strip(), p.stderr.strip(), p.returncode

def cmd_map(args):
    profile = os.environ.get("LLM_PROFILE", "default")
    print(f"⚡ Building map with profile [{profile}]...")
    out, err, rc = run("python3 build_final_all_profile.py", cwd=LLM_MAP)
    print(out)
    if rc != 0:
        print("❌ Map build failed:", err)
        return
    run("./generate_system_map.sh", cwd=LLM_MAP)
    print("🔬 Extracting functions...")
    run("python3 func_indexer.py", cwd=LLM_MAP)
    print("✅ Map + func index ready.")

def cmd_dep(args):
    if not args:
        print("Usage: forge dep <file>")
        return
    target = args[0]
    out, _, _ = run(f"bash {LLM_MAP}/depgraph.sh {target}")
    print(out)

def cmd_funcfind(args):
    if not args:
        print("Usage: forge funcfind <file_pattern>")
        return
    pattern = args[0]
    jq_cmd = f'''jq -r 'select(.file | test("{pattern}")) | "\\(.name) \t line \\(.line) \t \\(.sig[:60])"' {LLM_MAP}/func_index.jsonl'''
    out, _, _ = run(jq_cmd)
    print(out)

def cmd_dispatch(args):
    sys.path.insert(0, LLM_MAP)
    from dispatch_task import main as dm
    sys.argv = ["dispatch_task.py"] + args
    dm()

def cmd_promote(args):
    sys.path.insert(0, LLM_MAP)
    from promote import main as pm
    sys.argv = ["promote.py"] + args
    pm()

def cmd_archaeo(args):
    sys.path.insert(0, LLM_MAP)
    from archaeologist import main as am
    sys.argv = ["archaeologist.py"] + args
    am()

def cmd_oracle(args):
    sys.path.insert(0, LLM_MAP)
    from impact_oracle import main as om
    sys.argv = ["impact_oracle.py"] + args
    om()

def cmd_foresight(args):
    sys.path.insert(0, LLM_MAP)
    from foresight_collect import main as fm
    sys.argv = ["foresight_collect.py"] + args
    fm()

def cmd_tui(args):
    run("~/archwiz/archwiz.sh", cwd=ARCHWIZ)

def cmd_truth(args):
    sys.path.insert(0, LLM_MAP)
    from generate_diff_report import main as tm
    sys.argv = ["generate_diff_report.py"] + args
    tm()

def cmd_route(args):
    sys.path.insert(0, LLM_MAP)
    from router_agent import main as rm
    sys.argv = ["router_agent.py"] + args
    rm()

COMMANDS = {
    "map": cmd_map,
    "dep": cmd_dep,
    "funcfind": cmd_funcfind,
    "dispatch": cmd_dispatch,
    "promote": cmd_promote,
    "archaeo": cmd_archaeo,
    "oracle": cmd_oracle,
    "foresight": cmd_foresight,
    "fore": cmd_foresight,
    "tui": cmd_tui,
    "truth": cmd_truth,
    "route": cmd_route,
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("🪄 FORGE — Unified Caveman Ecosystem CLI")
        print("Usage: forge <command> [args...]")
        print("Commands:", ", ".join(sorted(COMMANDS.keys())))
        return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd in COMMANDS:
        COMMANDS[cmd](args)
    else:
        print(f"Unknown command: {cmd}. Run 'forge --help'.")

if __name__ == "__main__":
    main()
