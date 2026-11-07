"""Translate route  Termux commands/paths <-> iOS shell (iSH) equivalents.

iSH is Alpine: `apk`, not `pkg`. Many Termux tools (termux-*) have NO iOS
equivalent at all; those translate to None with the note preserved in the
table, never to a made-up command.

Hostile input is refused outright: anything carrying shell injection
(`;`, `$(...)`, backticks, pipes, `&&`, `||`) raises ValueError before it
can ever become a command in a plan.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Translation:
    termux: str
    ios: str          # "" means: no iOS equivalent
    note: str


TRANSLATIONS: list[Translation] = [
    Translation("pkg install {pkg}", "apk add {pkg}",
                "install a package: Termux pkg wraps apt; iSH uses Alpine apk"),
    Translation("pkg update", "apk update",
                "refresh the package index"),
    Translation("apt update", "apk update",
                "Termux also ships apt; on iSH the index refresh is apk update"),
    Translation("apt upgrade", "apk upgrade",
                "upgrade installed packages"),
    Translation("pkg upgrade", "apk upgrade",
                "Termux pkg upgrade -> Alpine apk upgrade"),
    Translation("pkg uninstall {pkg}", "apk del {pkg}",
                "remove a package"),
    Translation("pkg remove {pkg}", "apk del {pkg}",
                "Termux pkg remove -> Alpine apk del"),
    Translation("pkg search {pkg}", "apk search {pkg}",
                "search for a package in the repository"),
    Translation("apt search {pkg}", "apk search {pkg}",
                "apt search -> apk search"),
    Translation("pkg list-installed", "apk info -v",
                "list installed packages"),
    Translation("dpkg -l", "apk info -v",
                "list installed packages (dpkg -> apk)"),
    Translation("termux-open {file}", "open {file}",
                "open a file with the default app"),
    Translation("xdg-open {file}", "open {file}",
                "xdg-open -> open on iOS"),
    Translation("termux-clipboard-set", "pbcopy",
                "copy stdin to the clipboard"),
    Translation("termux-clipboard-get", "pbpaste",
                "print the clipboard contents"),
    Translation("termux-clipboard-set {text}", "echo {text} | pbcopy",
                "copy text to clipboard with echo"),
    Translation("termux-tts-speak {text}", "say {text}",
                "text to speech"),
    Translation("termux-tts-stop", "killall say 2>/dev/null; echo 'TTS stopped'",
                "stop text to speech"),
    Translation("termux-setup-storage", "",
                "NO iOS equivalent: storage permission is a Termux/Android "
                "concept; iOS grants file access per app in Files"),
    Translation("termux-wake-lock", "",
                "NO iOS equivalent: keep the iPhone awake from Settings "
                "or by keeping the shell app in front"),
    Translation("sshd", "ssh",
                "Termux can HOST sshd (port 8022); iOS shells are ssh "
                "CLIENTS only \u2014 there is no sshd server on iOS"),
    Translation("ssh {host}", "ssh {host}",
                "SSH client command (works on both, but Termux can also host)"),
    Translation("scp {file} {host}:{path}", "scp {file} {host}:{path}",
                "SCP file transfer (client-side works on both)"),
    Translation("termux-info", "uname -a",
                "system info (closest equivalent, not identical output)"),
    Translation("termux-battery-status", "",
                "NO iOS shell equivalent: battery APIs are Android-only"),
    Translation("termux-toast {text}", "echo {text}",
                "closest equivalent: print the text (no toast UI on iOS)"),
    Translation("termux-share {file}", "open {file}",
                "share-sheet maps closest to opening the file"),
    Translation("termux-wake-unlock", "",
                "NO iOS equivalent (pairs with termux-wake-lock)"),
    Translation("termux-vibrate", "",
                "NO iOS shell equivalent: vibration APIs are Android-only"),
    Translation("termux-notification", "echo 'Notification: {text}'",
                "closest equivalent: print notification (no system notification on iOS)"),
    Translation("termux-camera-photo", "",
                "NO iOS shell equivalent: camera APIs are Android-only"),
    Translation("termux-sensor", "",
                "NO iOS shell equivalent: Android sensors not available on iOS"),
    Translation("termux-download {url}", "curl -LO {url}",
                "download a file (termux-download -> curl)"),
    Translation("termux-download --timeout {sec} {url}", "curl --max-time {sec} -LO {url}",
                "download with timeout"),
]


@dataclass(frozen=True)
class PathTranslation:
    termux: str
    ios: str          # "" means: no shared equivalent
    note: str


PATH_TRANSLATIONS: list[PathTranslation] = [
    PathTranslation(
        "~/storage/downloads", "On My iPhone/Downloads",
        "the SHARED Download folder: files you can see in iOS Files and "
        "in Termux. Requires termux-setup-storage + the Allow tap."),
    PathTranslation(
        "~/downloads", "",
        "WARNING: ~/downloads is Termux's PRIVATE folder \u2014 files there are "
        "NOT the shared phone Download folder and iOS Files cannot see "
        "them. Shared files belong in ~/storage/downloads."),
    PathTranslation(
        "/data/data/com.termux/files/home", "~",
        "Termux $HOME lives under its Android app sandbox; in iSH the "
        "home directory is simply ~"),
    PathTranslation(
        "/data/data/com.termux/files/usr", "/usr",
        "Termux $PREFIX is /data/data/com.termux/files/usr; iSH uses the "
        "normal Alpine /usr"),
    PathTranslation(
        "~/storage/shared", "On My iPhone",
        "the root of shared storage maps to the iOS Files locations root"),
    PathTranslation(
        "~/storage/external-1", "On My iPhone",
        "external storage typically maps to iOS Files root"),
    PathTranslation(
        "/sdcard", "On My iPhone",
        "Android sdcard path -> iOS Files root"),
    PathTranslation(
        "/storage/emulated/0", "On My iPhone",
        "Android emulated storage -> iOS Files root"),
    PathTranslation(
        "/storage/emulated/0/Download", "On My iPhone/Downloads",
        "Android Download folder -> iOS Downloads"),
]

PRIVATE_DOWNLOADS_WARNING = (
    "~/downloads is Termux's PRIVATE folder, not the shared phone "
    "Download folder. Shared files live in ~/storage/downloads "
    "(termux-setup-storage + Allow required)."
)

_HOSTILE_MARKERS = ("$(", "`", ";", "&&", "||", "|", "\n", "\r")


def _reject_hostile(text: str) -> None:
    if any(m in text for m in _HOSTILE_MARKERS):
        raise ValueError(f"hostile shell input rejected: {text!r}")


def _norm_direction(direction: str) -> str:
    d = direction.strip().lower().replace("-", "_")
    if d in ("to_ios", "ios", "termux_to_ios"):
        return "to_ios"
    if d in ("to_termux", "termux", "ios_to_termux"):
        return "to_termux"
    raise ValueError(f"unknown direction: {direction!r}")


def _apply(template: str, captured: str) -> str:
    if "{" in template:
        head = template.split("{", 1)[0]
        name = template.split("{", 1)[1].split("}", 1)[0]
        return template.replace("{" + name + "}", captured)
    return template


def _match(template: str, cmd: str) -> str | None:
    """Return the captured placeholder value, '' for exact, None no match."""
    if "{" not in template:
        return "" if cmd == template else None
    head = template.split("{", 1)[0]
    if cmd.startswith(head) and len(cmd) > len(head):
        return cmd[len(head):].strip()
    return None


def translate_command(cmd: str, direction: str = "to_ios") -> str | None:
    """Translate one command between Termux and iOS (iSH).

    Returns the translated command, or None when there is no equivalent
    (or no known translation). Raises ValueError on hostile input.
    """
    _reject_hostile(cmd)
    cmd = " ".join(cmd.split())
    d = _norm_direction(direction)
    for t in TRANSLATIONS:
        src, dst = (t.termux, t.ios) if d == "to_ios" else (t.ios, t.termux)
        if not src:
            continue
        captured = _match(src, cmd)
        if captured is not None:
            if not dst:
                return None
            return _apply(dst, captured)
    return None


def translate_path(path: str, direction: str = "to_ios") -> str | None:
    """Translate one path between Termux and iOS Files / iSH.

    Returns the translated path, or None when there is no shared
    equivalent (notably ~/downloads, Termux's private folder).
    Raises ValueError on hostile input.
    """
    _reject_hostile(path)
    path = path.strip()
    d = _norm_direction(direction)
    for p in PATH_TRANSLATIONS:
        src, dst = (p.termux, p.ios) if d == "to_ios" else (p.ios, p.termux)
        if not src:
            continue
        if path == src:
            return dst if dst else None
        if path.startswith(src + "/"):
            if not dst:
                return None
            return dst + path[len(src):]
    return None
