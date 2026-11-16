"""Route registry — every way to get a Termux-like workflow when your
phone is an iPhone, classified honestly.

The truth this whole project is built on:
  * Termux is ANDROID-ONLY. There is no Termux for iOS, you cannot install
    a Termux APK / .deb on an iPhone, and no jailbreak is offered or
    required by this tool.
  * iOS shells are NOT Termux: iSH (Alpine, apk), a-Shell and Blink Shell
    are cockpits / clients, not Termux. They run a shell, they translate,
    they ssh — they never become Termux.
  * What works: (1) SSH from the iPhone into a REAL Termux running sshd on
    an Android device, (2) a cloud Linux box set up Termux-style,
    (3) translating Termux commands to iOS-shell equivalents, and
    (4) moving files through iOS Files into Termux shared storage.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    key: str
    name: str
    category: str          # impossible | shell-only | ssh-client | real-termux | cloud | transfer-only
    works: bool            # the route does what it claims to do
    is_real_termux: bool   # you end up inside an actual Termux
    needs_android: bool
    needs_jailbreak: bool
    best_for: str
    note: str


ROUTES: tuple[Route, ...] = (
    Route(
        "termux_on_ios", "Termux app running natively on iOS", "impossible",
        False, False, False, False,
        "nothing — it does not exist",
        "Termux is built for Android (its packages, paths and .deb/APK "
        "format are Android). There is no iOS build and no way to sideload "
        "one. Verdict: HOLD, do not chase it.",
    ),
    Route(
        "apk_on_ios", "Install the Termux APK / .deb on an iPhone", "impossible",
        False, False, False, False,
        "nothing — iOS cannot read Android packages",
        "iOS does not install .apk or Termux .deb files at all. An APK is "
        "an Android package; an iPhone has no runtime for it. Verdict: HOLD.",
    ),
    Route(
        "ish_shell", "iSH app (Alpine shell on iOS)", "shell-only",
        True, False, False, False,
        "running shell/Python locally with translated commands, and ssh out",
        "iSH is Alpine Linux emulated in user mode: apk packages, a real "
        "shell, Python — but it is NOT Termux. Termux commands translate "
        "(pkg -> apk); Termux-only tools have no equivalent.",
    ),
    Route(
        "a_shell", "a-Shell app (native iOS shell)", "shell-only",
        True, False, False, False,
        "quick local shell, Python and file work on the iPhone itself",
        "A native iOS shell with its own command set. Useful cockpit, "
        "still not Termux: no pkg, no $PREFIX, no sshd server.",
    ),
    Route(
        "blink_ssh", "Blink Shell (ssh / mosh client)", "ssh-client",
        True, False, False, False,
        "a polished ssh cockpit into a real Termux or a cloud box",
        "Blink is a client, not a shell host and not Termux. It shines at "
        "connecting the iPhone to a machine that IS Termux (or Linux).",
    ),
    Route(
        "ssh_to_android_termux", "SSH from iPhone into real Termux on Android",
        "real-termux", True, True, True, False,
        "RECOMMENDED: the real Termux — every pkg, path and tool, from your iPhone",
        "Run Termux on an Android device, start sshd (port 8022), then ssh "
        "in from iSH / Blink / Termius on the iPhone over LAN or Tailscale. "
        "The iPhone is the cockpit; the Android device runs real Termux.",
    ),
    Route(
        "cloud_termux", "Cloud Linux box, Termux-style (e.g. Codespaces)", "cloud",
        True, False, False, False,
        "a Termux-style environment with no Android device at hand",
        "A cloud Linux VM driven from the phone browser, with a pkg-like "
        "wrapper over apt so the workflow feels like Termux. Not literal "
        "Termux, but a full Linux that runs your tools.",
    ),
    Route(
        "ios_files_transfer", "iOS Files / Drive -> Termux shared storage",
        "transfer-only", True, False, True, False,
        "moving projects from the iPhone into Termux ~/storage/downloads",
        "Files land in the shared Download folder, which Termux sees as "
        "~/storage/downloads (after termux-setup-storage + Allow). NOT "
        "~/downloads — that is Termux's private folder. Archives must be "
        "extracted before Python can use the files.",
    ),
)

BY_KEY = {r.key: r for r in ROUTES}

RECOMMENDED_KEY = "ssh_to_android_termux"


def working_routes() -> list[Route]:
    return [r for r in ROUTES if r.works]


def real_termux_routes() -> list[Route]:
    return [r for r in ROUTES if r.is_real_termux]


def honest_verdict() -> dict:
    return {
        "termux_runs_natively_on_ios": False,
        "can_install_termux_apk_on_ios": False,
        "jailbreak_required": False,
        "ish_is_termux": False,
        "ish_runs_shell": True,
        "a_shell_is_termux": False,
        "blink_is_termux": False,
        "working_route": "ssh from iPhone into real Termux on Android",
        "recommended_route": RECOMMENDED_KEY,
        "routes_total": len(ROUTES),
        "routes_that_work": len(working_routes()),
        "real_termux_routes": len(real_termux_routes()),
    }
