#!/usr/bin/env python3
"""Termux-first ArchWiz Hyper-Forge cockpit.

Dependency-free ANSI/TUI surface over existing ArchWiz tools. The UI is an
operator surface: canonical state remains in repository files, protocol
objects, GitHub, and the existing validation gates.
"""
from __future__ import annotations
import os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHWIZ = ROOT / "archwiz"
LLM_MAP = ROOT / "workspace" / "llm_map"

ESC = "\033["
RESET = ESC + "0m"
BOLD = ESC + "1m"
CYAN = ESC + "96m"
GREEN = ESC + "92m"
AMBER = ESC + "93m"
MAGENTA = ESC + "95m"
RED = ESC + "91m"
DIM = ESC + "2m"
TRON = os.environ.get("ARCHWIZ_THEME", "tron").lower() == "tron"

def c(code: str, value: object) -> str:
    return f"{code}{value}{RESET}" if TRON else str(value)

def clear() -> None:
    print("\033[2J\033[H", end="")

def run(path: Path, *args: str, cwd: Path | None = None) -> int:
    cmd = [sys.executable, str(path), *args]
    try:
        return subprocess.run(cmd, cwd=str(cwd or ROOT), check=False).returncode
    except OSError as exc:
        print(c(RED, f"execution failed: {exc}"))
        return 1

def run_optional(target: Path) -> bool:
    if not target.exists():
        print(c(AMBER, f"not installed: {target}"))
        return True
    return run(target) == 0

def gate(command: list[str]) -> int:
    try:
        return subprocess.run(command, cwd=str(ROOT), check=False).returncode
    except OSError as exc:
        print(c(RED, f"gate unavailable: {exc}"))
        return 1

def panel(title: str, rows: list[str], width: int | None = None) -> None:
    if width is None:
        term_cols = shutil.get_terminal_size((80, 24)).columns
        width = min(80, max(36, term_cols - 2))
    print(c(CYAN, "+" + "-" * width + "+"))
    print(c(BOLD + CYAN, f"| {title:<{width - 2}}|"))
    print(c(CYAN, "+" + "-" * width + "+"))
    for row in rows:
        print(c(CYAN, f"| {row[: width - 2]:<{width - 2}}|"))
    print(c(CYAN, "+" + "-" * width + "+"))

def banner() -> None:
    clear()
    print(c(BOLD + GREEN, "⚡ ARCHWIZ // TERMUX HYPER-FORGE ⚡"))
    print(c(DIM, "  Tron-inspired display layer • dependency-free • operator-first"))
    print()
    panel("TERMUX EXECUTION SURFACE", [
        "TARGET     : Android / Termux",
        f"THEME      : {'TRON' if TRON else 'PLAIN'}",
        "FORESIGHT  : workspace/llm_map/foresight_collect.py",
        "CHRONO     : harmony_hub/workspace/agent/chronomancer.py",
        "GOVERNANCE : CLAUDE.md → proposals → dual gates",
        'INPUT      : Ask && U $h411 π3c31ve',
    ])

def menu() -> None:
    panel("COCKPIT MATRIX", [
        "[1]  Autonomous Dispatch       [2]  Deep RECON / Archaeology",
        "[3]  Agent Shell               [4]  Live Metrics",
        "[5]  Backup State              [6]  Rebuild + Foresight",
        "[7]  Profile Surface           [8]  Workflow / Task Builder",
        "[9]  ChronoMancer Timeline     [10] Health / Dangle Scan",
        "[11] Session Pipeline          [12] Activity / Narrative",
        "[13] Lexicon / AST Harvest     [14] Forensic Toolchain",
        "[15] Live View                  [16] Documentation Refresh",
        "[17] Promote Sandbox            [18] Dual-Gate Validation",
        "[19] Foresight Snapshot         [20] Hyper-Forge Status",
        "[a] Auto mode                  [r] Review mode",
        "[q] Quit",
    ])

def action(choice: str) -> bool:
    if choice == "1":
        args = ("--auto-approve",) if os.environ.get("ARCHWIZ_MODE") == "auto" else ()
        return run(ARCHWIZ / "autonomous_runner.py", *args) == 0
    if choice == "2": return run(ARCHWIZ / "archaeo_sweep.py") == 0
    if choice == "3": return run(ARCHWIZ / "agent_shell.py") == 0
    if choice == "4": return run(ARCHWIZ / "metrics_viewer.py") == 0
    if choice == "5":
        ts = time.strftime("%Y%m%d_%H%M%S")
        out = ARCHWIZ / f"ecosystem_backup_{ts}.tar.gz"
        wanted = ["HANDOFF.json", "master_tasks.json", "metrics_log.jsonl", "foresight_state.json"]
        existing = [p for p in wanted if (ARCHWIZ / p).exists()]
        return subprocess.run(["tar", "czf", str(out), *existing], cwd=str(ARCHWIZ), check=False).returncode == 0
    if choice == "6":
        for target in ("build_final_all_profile.py", "func_indexer.py", "foresight_collect.py"):
            if run(LLM_MAP / target) != 0: return False
        return run(ARCHWIZ / "archaeo_sweep.py", "--max", "15") == 0
    if choice == "7":
        prof = Path.home() / ".config" / "llm_map" / "profiles"
        print("\n".join(f"  {p.stem}" for p in sorted(prof.glob("*.json"))) or "No profiles found.")
        return True
    if choice == "8": return run(ARCHWIZ / "task_builder.py") == 0
    if choice == "9": return run(ARCHWIZ / "timeline_editor.py") == 0
    if choice == "10": return run(ARCHWIZ / "dangle_detector.py") == 0 and run(ARCHWIZ / "mirror.py") == 0
    if choice == "11": return run(ARCHWIZ / "import_session.py") == 0
    if choice == "12":
        target = LLM_MAP / "narrative.py"
        return run_optional(target)
    if choice == "13":
        target = ARCHWIZ / "lexicon_harvest.py"
        return run_optional(target)
    if choice == "14":
        target = ARCHWIZ / "forensic_toolchain.py"
        return run_optional(target)
    if choice == "15":
        target = ARCHWIZ / "live_view.py"
        return run_optional(target)
    if choice == "16":
        target = ARCHWIZ / "documentation_refresh.py"
        return run_optional(target)
    if choice == "17": return run(LLM_MAP / "promote_workspace.py") == 0
    if choice == "18":
        a = gate(["python3", "scripts/ci/repo_gate.py", "--base", "origin/master"])
        b = gate(["python3", "scripts/ci/termux_smoke.py"])
        print(c(GREEN if a == 0 else RED, f"repo-gate={'PASS' if a == 0 else 'FAIL'}"))
        print(c(GREEN if b == 0 else RED, f"termux-smoke={'PASS' if b == 0 else 'FAIL'}"))
        return a == 0 and b == 0
    if choice == "19": return run(LLM_MAP / "foresight_collect.py") == 0
    if choice == "20":
        state = ARCHWIZ / "foresight_state.json"
        print(c(GREEN, "HYPER-FORGE ONLINE"))
        print(f"  foresight_state : {'present' if state.exists() else 'missing'}")
        print(f"  termux          : {os.environ.get('PREFIX', 'unknown')}")
        print(f"  python          : {sys.version.split()[0]}")
        print("  canonical state : repository / protocol / GitHub evidence")
        return True
    if choice in {"a", "r"}:
        os.environ["ARCHWIZ_MODE"] = "auto" if choice == "a" else "review"
        print(c(GREEN, f"mode={os.environ['ARCHWIZ_MODE']}"))
        return True
    if choice in {"q", "0"}: return False
    print(c(AMBER, f"Unknown selection: {choice}"))
    return True

def main() -> int:
    while True:
        banner()
        menu()
        try:
            choice = input(c(BOLD + MAGENTA, "  >> ")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if choice in {"q", "0"}: return 0
        if not action(choice):
            print(c(RED, f"Action {choice} failed."))
        input(c(DIM, "\n  press ENTER to return to the matrix…"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
