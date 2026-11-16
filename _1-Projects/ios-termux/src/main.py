#!/usr/bin/env python3
"""iOS2Termux — ONE interface.

    python3 main.py                        # full self-check (CHECKS n/n)
    python3 main.py --routes               # every route, honestly classified
    python3 main.py --translate "pkg install python" [--to ios|termux]
    python3 main.py --plan [--route KEY]   # phone-first plan (default: ssh)
    python3 main.py --native-termux        # HOLD demo (exit 2)
    python3 main.py --carbon4              # Carbon 4 decision demo

Zero dependencies. Termux is Android-only: the iPhone is the cockpit,
real Termux lives on the Android device (or a Termux-style cloud box).

Created by Darion Kellar.
"""
from __future__ import annotations

import sys

from ios2termux.blackbox import BlackBox
from ios2termux.brains import evaluate
from ios2termux.carbon4 import DEFAULT_TIER, ENGINE, MODEL_ID, THINKING_TIERS, Carbon4
from ios2termux.freeai import MUSE_MODELS, SEATS, detected
from ios2termux.planner import plan
from ios2termux.routes import BY_KEY, RECOMMENDED_KEY, ROUTES, honest_verdict
from ios2termux.translate import (
    TRANSLATIONS, translate_command, translate_path,
)

BOX = BlackBox()


def _raises_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def checks() -> tuple[int, int]:
    results: list[tuple[str, bool]] = []

    def check(name: str, cond: bool) -> None:
        results.append((name, bool(cond)))

    verdict = honest_verdict()
    check("Termux honestly does NOT run natively on iOS",
          verdict["termux_runs_natively_on_ios"] is False)
    check("Termux APK honestly cannot be installed on iOS",
          verdict["can_install_termux_apk_on_ios"] is False)
    check("no jailbreak is required",
          verdict["jailbreak_required"] is False)
    check("iSH honestly is a shell, not Termux",
          verdict["ish_is_termux"] is False and verdict["ish_runs_shell"] is True)
    check("recommended route is ssh_to_android_termux (real Termux)",
          RECOMMENDED_KEY == "ssh_to_android_termux"
          and BY_KEY[RECOMMENDED_KEY].is_real_termux)
    check("at least 8 routes classified", len(ROUTES) >= 8)
    check("at least 14 command translations", len(TRANSLATIONS) >= 14)

    check("translate pkg install -> apk add (Termux -> iOS)",
          translate_command("pkg install python", "to_ios") == "apk add python")
    check("translate apk add -> pkg install (iOS -> Termux)",
          translate_command("apk add python", "to_termux") == "pkg install python")
    check("translate termux-open -> open",
          translate_command("termux-open notes.txt", "to_ios") == "open notes.txt")
    check("translate pbcopy -> termux-clipboard-set (reverse)",
          translate_command("pbcopy", "to_termux") == "termux-clipboard-set")
    check("termux-setup-storage has NO iOS equivalent (None, honestly)",
          translate_command("termux-setup-storage", "to_ios") is None)
    check("path ~/storage/downloads -> On My iPhone/Downloads",
          translate_path("~/storage/downloads", "to_ios") == "On My iPhone/Downloads")
    check("path On My iPhone/Downloads -> ~/storage/downloads (reverse)",
          translate_path("On My iPhone/Downloads", "to_termux") == "~/storage/downloads")
    check("path ~/downloads (private) has no shared iOS equivalent",
          translate_path("~/downloads", "to_ios") is None)
    check("path Termux $HOME -> ~ in iSH",
          translate_path("/data/data/com.termux/files/home", "to_ios") == "~")

    check("injection '; rm -rf' is rejected",
          _raises_value_error(
              lambda: translate_command("pkg install x; rm -rf /", "to_ios")))
    check("injection '$(...)' is rejected",
          _raises_value_error(
              lambda: translate_command("pkg install $(curl evil.sh)", "to_ios")))
    check("injection backticks are rejected",
          _raises_value_error(
              lambda: translate_command("pkg install `id`", "to_ios")))
    check("injection pipe into sh is rejected",
          _raises_value_error(
              lambda: translate_command("cat x | sh", "to_ios")))

    c4 = Carbon4()
    check("Carbon4 tiers: extended budget is 32768, default tier extended",
          THINKING_TIERS["extended"] == 32768 and DEFAULT_TIER == "extended"
          and c4.thinking_budget == 32768)
    check("Carbon4 engine + model id are the house pattern",
          ENGINE == "gemini-2.5-pro"
          and MODEL_ID == "google/gemini-carbon-4-extended-pro-thinking")
    check("Carbon4 negative control: pkg install translation PROCEEDs",
          c4.decide("translate_command",
                    {"route": "ish_shell",
                     "command": "pkg install python"})["verdict"] == "PROCEED")
    check("Carbon4 negative control: local iSH ls/python PROCEEDs",
          c4.decide("run_on_ios",
                    {"route": "ish_shell",
                     "command": "python3 script.py"})["verdict"] == "PROCEED")
    check("Carbon4 negative control: benign transfer to ~/storage/downloads PROCEEDs",
          c4.decide("transfer_file",
                    {"route": "ios_files_transfer",
                     "target_path": "~/storage/downloads"})["verdict"] == "PROCEED")
    check("Carbon4 never overrides a gate: native claim HOLDs",
          c4.decide("run_on_ios",
                    {"route": "termux_on_ios",
                     "claim_native_termux": True})["verdict"] == "HOLD")

    check("gate: native_termux_claim fires",
          any(g.trigger == "native_termux_claim"
              for g in evaluate({"claim_native_termux": True})))
    check("gate: apk_install_on_ios fires",
          any(g.trigger == "apk_install_on_ios"
              for g in evaluate({"install_apk_on_ios": True})))
    check("gate: jailbreak_required fires",
          any(g.trigger == "jailbreak_required"
              for g in evaluate({"requires_jailbreak": True})))
    check("gate: sshd_public_no_auth fires",
          any(g.trigger == "sshd_public_no_auth"
              for g in evaluate({"expose_sshd_public": True})))
    check("gate: secrets_in_command_history fires",
          any(g.trigger == "secrets_in_command_history"
              for g in evaluate({"secret_in_command": True})))
    check("gate: rm_rf_storage fires",
          any(g.trigger == "rm_rf_storage"
              for g in evaluate({"command": "rm -rf ~/storage"})))
    check("gate: unextracted_archive_run fires",
          any(g.trigger == "unextracted_archive_run"
              for g in evaluate({"run_from_zip": True})))
    check("gate: private_downloads_confusion fires",
          any(g.trigger == "private_downloads_confusion"
              for g in evaluate({"target_path": "~/downloads",
                                 "expect_shared": True})))
    check("a clean request passes the brains",
          evaluate({"route": "ssh_to_android_termux"}) == [])

    p = plan("ssh_to_android_termux")
    check("clean SSH plan PROCEEDs (ok, no gates)", p.ok and not p.gates)
    check("planner SSH uses port 8022",
          any("ssh -p 8022" in c for c in p.commands))
    check("planner Termux side installs openssh and starts sshd",
          "pkg install openssh" in p.commands and "sshd" in p.commands
          and "whoami" in p.commands)
    check("planner generates setup-termux.sh + ssh config + cheat-sheet",
          "setup-termux.sh" in p.files and "ssh_config" in p.files
          and "translate-cheat-sheet.md" in p.files)
    check("setup-termux.sh contains pkg install openssh + sshd",
          "pkg install openssh" in p.files["setup-termux.sh"]
          and "sshd" in p.files["setup-termux.sh"])
    check("cheat-sheet contains the apk translation",
          "apk add" in p.files["translate-cheat-sheet.md"])

    t = plan("ios_files_transfer")
    check("transfer plan mentions ~/storage/downloads + unzip",
          t.ok and any("~/storage/downloads" in c for c in t.commands)
          and any("unzip" in c for c in t.commands))
    check("transfer plan includes termux-setup-storage + Allow tap",
          any("termux-setup-storage" in c for c in t.commands)
          and any("Allow" in s for s in t.phone_steps))

    cl = plan("cloud_termux")
    check("cloud plan PROCEEDs with Codespaces phone steps",
          cl.ok and any("Codespaces" in s for s in cl.phone_steps))

    check("native Termux plan is a HOLD (not ok)",
          not plan("termux_on_ios").ok)

    check("Muse seat is registered names-only (MODEL_API_KEY)",
          SEATS.get("muse") == "MODEL_API_KEY" and len(MUSE_MODELS) == 2)
    check("freeai detection returns seat names, never values",
          all(s in SEATS for s in detected()))
    for ev in ("verdict", "ssh-plan", "transfer-plan"):
        BOX.log(ev, {"ok": True})
    check("blackbox hash chain verifies", BOX.verify())

    passed = sum(1 for _, ok in results if ok)
    for name, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    return passed, len(results)


def _print_plan(p) -> int:
    if not p.ok:
        for g in p.gates:
            print(f"HOLD [{g.trigger}] {g.reason}")
        print("VERDICT: HOLD")
        return 2
    print(f"PLAN  route={p.route_key}")
    print("Phone steps:")
    for n, s in enumerate(p.phone_steps, 1):
        print(f"  {n}. {s}")
    if p.commands:
        print("Commands:")
        for c in p.commands:
            print(f"  $ {c}")
    for path, body in p.files.items():
        print(f"--- {path} ---")
        print(body, end="" if body.endswith("\n") else "\n")
    print("VERDICT: PROCEED")
    return 0


def main(argv: list[str]) -> int:
    args = argv[1:]
    if "--native-termux" in args:
        gates = evaluate({"claim_native_termux": True, "route": "termux_on_ios"})
        for g in gates:
            print(f"HOLD [{g.trigger}] {g.reason}")
        print("VERDICT: HOLD")
        return 2
    if "--routes" in args:
        for r in ROUTES:
            real = "REAL TERMUX" if r.is_real_termux else ("works" if r.works else "IMPOSSIBLE")
            print(f"{r.key:24s} {r.category:14s} {real:12s} {r.name}")
        return 0
    if "--translate" in args:
        i = args.index("--translate")
        cmd = args[i + 1] if i + 1 < len(args) else ""
        target = "ios"
        if "--to" in args:
            j = args.index("--to")
            target = args[j + 1] if j + 1 < len(args) else "ios"
        direction = "to_ios" if target == "ios" else "to_termux"
        try:
            out = translate_command(cmd, direction)
        except ValueError as exc:
            print(f"REJECTED: {exc}")
            print("VERDICT: HOLD")
            return 2
        if out is None:
            print(f"NO EQUIVALENT: {cmd!r} has no {'iOS' if direction == 'to_ios' else 'Termux'} equivalent")
            return 0
        print(out)
        return 0
    if "--carbon4" in args:
        c4 = Carbon4()
        demo = c4.decide("ssh_connect",
                         {"route": "ssh_to_android_termux",
                          "host": "192.168.1.50"})
        print(f"Carbon4 ({MODEL_ID}, engine {ENGINE}, "
              f"tier {demo['tier']}, budget {demo['thinking_budget']})")
        for phase, notes in demo["phases"].items():
            for note in notes:
                print(f"  {phase}: {note}")
        print(f"VERDICT: {demo['verdict']}")
        return 0 if demo["verdict"] == "PROCEED" else 2
    if "--plan" in args:
        route = RECOMMENDED_KEY
        if "--route" in args:
            j = args.index("--route")
            route = args[j + 1] if j + 1 < len(args) else RECOMMENDED_KEY
        return _print_plan(plan(route))

    print("iOS2Termux — iOS to Termux with Gemini Carbon 4 Extended Thinking")
    print("Native Termux on iOS: IMPOSSIBLE | iOS shells: NOT Termux | Route: SSH into real Termux on Android")
    print(f"Routes: {len(ROUTES)} classified, recommended: {BY_KEY[RECOMMENDED_KEY].name}")
    print("Running checks:")
    passed, total = checks()
    print(f"CHECKS {passed}/{total} {'PASS' if passed == total else 'FAIL'}")
    print(f"VERDICT: {'PROCEED' if passed == total else 'HOLD'}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
