"""Planner — turn a route key into a phone-first plan: the exact taps on
the phone, the exact commands on each side, and the generated files
(ssh config snippet, Android-side setup-termux.sh, translate cheat-sheet)
as data strings the user can paste/save.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .brains import Gate, evaluate
from .routes import BY_KEY
from .translate import TRANSLATIONS

DEFAULT_HOST = "192.168.1.50"
DEFAULT_USER = "u0_a123"
SSH_PORT = 8022


@dataclass
class RunPlan:
    route_key: str
    route: str
    ok: bool
    gates: list[Gate] = field(default_factory=list)
    phone_steps: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)

    @property
    def platform(self) -> str:
        return self.route_key


def ssh_config_snippet(host: str = DEFAULT_HOST, user: str = DEFAULT_USER) -> str:
    return (
        "# iOS2Termux — ssh config snippet (iSH / Blink: ~/.ssh/config)\n"
        "Host termux\n"
        f"    HostName {host}\n"
        f"    Port {SSH_PORT}\n"
        f"    User {user}\n"
    )


def setup_termux_sh() -> str:
    """The Android-side setup script: run INSIDE real Termux once."""
    return (
        "#!/data/data/com.termux/files/usr/bin/bash\n"
        "# iOS2Termux — one-time setup INSIDE real Termux on the Android device\n"
        "set -e\n"
        "pkg update\n"
        "pkg install openssh\n"
        "termux-setup-storage\n"
        "passwd\n"
        "sshd\n"
        "whoami\n"
        "ip addr\n"
        f"echo \"Termux sshd is up on port {SSH_PORT} — ssh in from the iPhone\"\n"
    )


def cloud_setup_sh() -> str:
    """Termux-style setup for a cloud Linux box: a pkg-like wrapper."""
    return (
        "#!/usr/bin/env bash\n"
        "# iOS2Termux — Termux-style setup on a cloud Linux box (Codespaces)\n"
        "set -e\n"
        "sudo apt update\n"
        "cat >> ~/.bashrc <<'EOF'\n"
        "pkg() {\n"
        "  if [ \"$1\" = install ]; then shift; sudo apt install -y \"$@\";\n"
        "  elif [ \"$1\" = update ]; then sudo apt update;\n"
        "  elif [ \"$1\" = uninstall ]; then shift; sudo apt remove -y \"$@\";\n"
        "  else echo \"pkg wrapper: install|update|uninstall\"; fi\n"
        "}\n"
        "EOF\n"
        "echo \"pkg wrapper installed — this box now feels Termux-style\"\n"
    )


def cheat_sheet_md() -> str:
    lines = [
        "# iOS2Termux — Translate Cheat-Sheet\n",
        "\n",
        "Termux (Android) <-> iSH (iOS, Alpine). Empty iOS cell = no equivalent.\n",
        "\n",
        "| Termux | iOS (iSH) | Note |\n",
        "|---|---|---|\n",
    ]
    for t in TRANSLATIONS:
        ios = t.ios if t.ios else "— (none)"
        lines.append(f"| `{t.termux}` | `{ios}` | {t.note} |\n")
    lines.append(
        "\nPaths: `~/storage/downloads` <-> iOS Files `On My iPhone/Downloads` "
        "(shared). `~/downloads` is Termux PRIVATE — never use it for shared "
        "files. Extract archives before running them.\n")
    return "".join(lines)


_PHONE_STEPS = {
    "ssh_to_android_termux": [
        "On the ANDROID device: open Termux (install it from F-Droid / Play Store first)",
        "In Termux, run the Android-side commands below (setup-termux.sh does them all)",
        "When Termux asks for storage permission, tap Allow",
        "Note the username (whoami) and the IP (ip addr) Termux prints",
        "On the iPHONE: open iSH (or Blink / Termius)",
        "Run the ssh command below in iSH — you are now inside REAL Termux",
        "Same LAN works out of the box; across networks, put both devices on Tailscale",
    ],
    "cloud_termux": [
        "On the iPhone, open Chrome (Desktop site ON) and go to github.com",
        "Open any of your repos > green Code button > Codespaces tab > Create codespace on main",
        "Wait for the browser VS Code to load, open its terminal",
        "Run the cloud setup below — the pkg wrapper makes the box feel Termux-style",
        "Work in the browser terminal; stop the codespace when done (stops the meter)",
    ],
    "ios_files_transfer": [
        "On the iPhone, save / AirDrop / download the file into Files > Downloads",
        "On the ANDROID device, open Termux and run: termux-setup-storage",
        "Tap Allow on the Android storage-permission prompt",
        "In Termux, the file is now visible at ~/storage/downloads (NOT ~/downloads)",
        "Extract archives in Termux BEFORE running anything (unzip step below)",
        "Run the extracted project from Termux home, not from inside the zip",
    ],
    "ish_shell": [
        "On the iPhone, open iSH",
        "Work locally with TRANSLATED commands (pkg -> apk) — see the cheat-sheet file",
        "Termux-only tools (termux-*) have no equivalent: use the ssh route for those",
    ],
    "a_shell": [
        "On the iPhone, open a-Shell",
        "Work locally with a-Shell's own commands; translate Termux steps first",
        "For real Termux, switch to the ssh route from a-Shell's ssh client",
    ],
    "blink_ssh": [
        "On the iPhone, open Blink Shell",
        "Add a host for the Android device (or use the ssh config snippet file)",
        "Connect — Blink is the cockpit, the Android device runs real Termux",
    ],
}


def plan(route_key: str, host: str = DEFAULT_HOST, user: str = DEFAULT_USER,
         **flags) -> RunPlan:
    if route_key not in BY_KEY:
        raise ValueError(f"unknown route: {route_key!r}")
    request = {"route": route_key, **flags}
    gates = evaluate(request)
    route = BY_KEY[route_key]
    p = RunPlan(route_key=route_key, route=route_key, ok=not gates, gates=gates)
    if gates:
        return p
    p.phone_steps = _PHONE_STEPS.get(route_key, [
        f"Open {route.name} on the phone",
        "Follow the commands below",
    ])
    if route_key == "ssh_to_android_termux":
        p.commands = [
            "pkg update",
            "pkg install openssh",
            "termux-setup-storage",
            "passwd",
            "sshd",
            "whoami",
            "ip addr",
            f"ssh -p {SSH_PORT} {user}@{host}",
        ]
        p.files["setup-termux.sh"] = setup_termux_sh()
        p.files["ssh_config"] = ssh_config_snippet(host, user)
        p.files["translate-cheat-sheet.md"] = cheat_sheet_md()
    elif route_key == "cloud_termux":
        p.commands = [
            "sudo apt update",
            "bash setup-cloud-termux.sh",
            "pkg install python",
            "python3 --version",
        ]
        p.files["setup-cloud-termux.sh"] = cloud_setup_sh()
        p.files["translate-cheat-sheet.md"] = cheat_sheet_md()
    elif route_key == "ios_files_transfer":
        p.commands = [
            "termux-setup-storage",
            "ls ~/storage/downloads",
            "unzip ~/storage/downloads/project.zip -d ~/project",
            "cd ~/project && ls",
            "python3 main.py",
        ]
        p.files["translate-cheat-sheet.md"] = cheat_sheet_md()
    elif route_key in ("ish_shell", "a_shell"):
        p.commands = [
            "apk update",
            "apk add python3",
            "python3 --version",
        ]
        p.files["translate-cheat-sheet.md"] = cheat_sheet_md()
    elif route_key == "blink_ssh":
        p.commands = [f"ssh -p {SSH_PORT} {user}@{host}"]
        p.files["ssh_config"] = ssh_config_snippet(host, user)
        p.files["translate-cheat-sheet.md"] = cheat_sheet_md()
    return p
