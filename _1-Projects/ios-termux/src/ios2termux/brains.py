"""Brains — HOLD gates. The advisor (incl. the freeai Muse seat) and
Gemini Carbon 4 can recommend, they can NEVER override a HOLD."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Gate:
    trigger: str
    reason: str


def _command_of(request: dict) -> str:
    return str(request.get("command", "") or "")


def evaluate(request: dict) -> list[Gate]:
    """Return HOLD gates for a request; empty list = clear."""
    gates: list[Gate] = []
    cmd = _command_of(request)
    route = request.get("route") or request.get("platform") or ""

    if (request.get("claim_native_termux") or request.get("native_termux")
            or route == "termux_on_ios"):
        gates.append(Gate(
            "native_termux_claim",
            "There is no Termux for iOS. Termux is Android-only; route to "
            "real Termux on Android over SSH, a cloud box, or translate "
            "the commands for iSH instead.",
        ))
    if request.get("install_apk_on_ios") or route == "apk_on_ios":
        gates.append(Gate(
            "apk_install_on_ios",
            "iOS cannot install a Termux APK or .deb — those are Android "
            "packages and an iPhone has no runtime for them.",
        ))
    if request.get("requires_jailbreak") or request.get("jailbreak"):
        gates.append(Gate(
            "jailbreak_required",
            "This plan requires a jailbreak. iOS2Termux offers no jailbreak "
            "route and none is needed for any working route.",
        ))
    public = (request.get("expose_sshd_public") or request.get("sshd_public")
              or request.get("public_internet"))
    has_auth = (request.get("auth") or request.get("key_auth")
                or request.get("use_key") or request.get("password_auth"))
    if public and not has_auth:
        gates.append(Gate(
            "sshd_public_no_auth",
            "Exposing sshd to the public internet with no auth / no key "
            "hands the shell to the whole internet. Keep sshd on LAN or "
            "Tailscale, or require key auth.",
        ))
    elif public and request.get("password_auth_only"):
        gates.append(Gate(
            "sshd_public_no_auth",
            "Password-only sshd on the public internet is brute-force "
            "bait. Require key auth, or keep sshd on LAN / Tailscale.",
        ))
    if (request.get("secret_in_command") or request.get("secrets_in_history")
            or request.get("pass_secrets_as_args")):
        gates.append(Gate(
            "secrets_in_command_history",
            "An API key pasted as a plain command argument lands in shell "
            "history and process lists. Use an environment variable set "
            "from a file, never a literal key in a command.",
        ))
    if (request.get("rm_rf_storage") or "rm -rf ~/storage" in cmd
            or "rm -rf /" in cmd or "rm -rf ~/" in cmd and "storage" in cmd):
        gates.append(Gate(
            "rm_rf_storage",
            "rm -rf against ~/storage (or /) wipes the SHARED phone "
            "storage, not just Termux files. Refused.",
        ))
    if (request.get("run_from_zip") or request.get("unextracted_archive")
            or (".zip" in cmd and "python" in cmd
                and "unzip" not in cmd)):
        gates.append(Gate(
            "unextracted_archive_run",
            "Python cannot run a project from inside a .zip in shared "
            "storage. Extract it first (unzip), then run the .py files.",
        ))
    target = str(request.get("target_path", "") or request.get("path", "") or "")
    expects_shared = (request.get("expect_shared")
                      or request.get("shared_files")
                      or request.get("use_private_downloads_for_shared"))
    if expects_shared and (target.rstrip("/") == "~/downloads"
                           or request.get("use_private_downloads_for_shared")):
        gates.append(Gate(
            "private_downloads_confusion",
            "~/downloads is Termux's PRIVATE folder — iOS Files cannot "
            "see it and shared files never arrive there. Shared files "
            "belong in ~/storage/downloads (termux-setup-storage + Allow).",
        ))
    return gates
