"""Command-line operations for the Codex bridge scaffold."""

import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import paths

# Working product title until TER-12 naming poll settles (PR #9).
PRODUCT = os.environ.get("CODEX_BRIDGE_NAME", "DeepForge")


class _IndexUnreadable(Exception):
    """The existing index cannot be safely merged."""


def _deepcli_importable() -> bool:
    package_root = str(paths.REPO_ROOT / "deepcli")
    if not (Path(package_root) / "deepcli" / "__init__.py").is_file():
        return False
    sys.path.insert(0, package_root)
    try:
        importlib.import_module("deepcli")
    except Exception:
        return False
    finally:
        sys.path.pop(0)
    return True


def _deepcli_launcher() -> Optional[Path]:
    """Locate a runnable deepcli entrypoint."""
    candidates = [
        paths.REPO_ROOT / "deepcli" / "deepcli.py",
        paths.home() / "deepcli" / "deepcli.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    which = __import__("shutil").which("deepcli")
    if which:
        return Path(which)
    return None


def _print_status(label: str, ok: bool, detail: str) -> bool:
    print(f"{'OK' if ok else 'MISSING'} {label}: {detail}")
    return ok


def _doctor(strict: bool) -> int:
    cargo_file = paths.CODEX_ROOT / "codex-rs" / "Cargo.toml"
    checks = [
        _print_status(
            "submodule",
            cargo_file.is_file(),
            str(cargo_file) if cargo_file.is_file() else f"{cargo_file} not found",
        ),
    ]
    binary = paths.codex_binary()
    checks.append(
        _print_status(
            "codex binary",
            binary is not None and binary.is_file(),
            str(binary) if binary else "build with: make build",
        )
    )
    deepcli_ok = _deepcli_importable()
    launcher = _deepcli_launcher()
    checks.append(
        _print_status(
            "deepcli",
            deepcli_ok or launcher is not None,
            str(launcher) if launcher else (
                str(paths.REPO_ROOT / "deepcli") if deepcli_ok else "package not found"
            ),
        )
    )
    checks.append(
        _print_status("deepcli store", paths.deepcli_store().is_dir(), str(paths.deepcli_store()))
    )
    checks.append(
        _print_status("codex index", paths.codex_index().is_file(), str(paths.codex_index()))
    )
    return 1 if strict and not all(checks) else 0


def _build() -> int:
    if not (paths.CODEX_ROOT / "codex-rs" / "Cargo.toml").is_file():
        print("MISSING submodule: run `make init` first", file=sys.stderr)
        return 1
    result = subprocess.run(
        ["cargo", "build", "-p", "codex-cli"],
        cwd=paths.CODEX_ROOT / "codex-rs",
        check=False,
    )
    return result.returncode


def _export_environment() -> Dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "CODEX_TERMUX_ROOT": str(paths.CODEX_ROOT),
            "DEEPCLI_STORE": str(paths.deepcli_store()),
            "SYNTHEGRATION_DIR": str(paths.synthegration_dir()),
            "CODEX_BRIDGE_NAME": PRODUCT,
        }
    )
    binary = paths.codex_binary()
    if binary:
        environment["TERMUX_CODEX_BIN"] = str(binary)
    return environment


def _run_deepcli(arguments: List[str]) -> int:
    launcher = _deepcli_launcher()
    if launcher is None:
        print(
            "deepcli launcher not found. Expected deepcli/deepcli.py in the monorepo "
            "or a `deepcli` binary on PATH.",
            file=sys.stderr,
        )
        return 1
    env = _export_environment()
    package_root = str(paths.REPO_ROOT / "deepcli")
    if (Path(package_root) / "deepcli" / "__init__.py").is_file():
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = package_root + (os.pathsep + existing if existing else "")
    os.execvpe(sys.executable, [sys.executable, str(launcher), *arguments], env)
    return 1


def _run_codex_native(arguments: List[str]) -> int:
    binary = paths.codex_binary()
    if binary is None or not binary.is_file():
        print("Codex binary missing; run `python -m codex_bridge build` first.", file=sys.stderr)
        return 1
    os.execvpe(str(binary), [str(binary), *arguments], _export_environment())
    return 1


def _run(arguments: List[str], force_native: bool = False) -> int:
    """Default entry: prefer deepcli; only hit stock Codex when forced or deepcli missing."""
    if force_native:
        return _run_codex_native(arguments)
    if _deepcli_launcher() is not None or _deepcli_importable():
        return _run_deepcli(arguments)
    print(
        "deepcli not available — falling back to native Codex binary.\n"
        "  Install/place deepcli to avoid the OpenAI sign-in gate.",
        file=sys.stderr,
    )
    return _run_codex_native(arguments)


def _menu() -> int:
    """Native-style numbered picker (no CLI subcommand jargon)."""
    deepcli_ready = _deepcli_launcher() is not None or _deepcli_importable()
    native_ready = paths.codex_binary() is not None

    print()
    print(f"  {PRODUCT}")
    print("  ────────────────────────────────────────")
    print("  1. deepcli          custom wrapper" + (" ✓" if deepcli_ready else " (missing)"))
    print("  2. Codex native     stock binary" + (" ✓" if native_ready else " (missing)"))
    print("  3. Doctor           check prerequisites")
    print("  4. Reconcile        sync session pointers")
    print("  5. Quit")
    print("  ────────────────────────────────────────")
    try:
        choice = input("  Select [1]: ").strip() or "1"
    except (EOFError, KeyboardInterrupt):
        print()
        return 0

    if choice in ("1", "deepcli", "d"):
        if not deepcli_ready:
            print("deepcli is not available on this device.", file=sys.stderr)
            return 1
        return _run_deepcli([])
    if choice in ("2", "native", "codex", "n"):
        if not native_ready:
            print("Codex binary not found; try build first.", file=sys.stderr)
            return 1
        return _run_codex_native([])
    if choice in ("3", "doctor"):
        return _doctor(strict=False)
    if choice in ("4", "reconcile"):
        return _reconcile()
    if choice in ("5", "q", "quit", "exit"):
        return 0
    print(f"Unknown selection: {choice}", file=sys.stderr)
    return 1


def _load_index(index_path: Path) -> Dict[str, Any]:
    if not index_path.is_file():
        return {"pointers": []}
    try:
        data = json.loads(index_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise _IndexUnreadable(f"cannot read {index_path}: {error}") from error
    if not isinstance(data, dict):
        raise _IndexUnreadable(f"{index_path} must contain a JSON object")
    pointers = data.get("pointers")
    if not isinstance(pointers, list):
        raise _IndexUnreadable(f"{index_path} must contain a list at `pointers`")
    return data


def _reconcile() -> int:
    store = paths.deepcli_store()
    index_path = paths.codex_index()
    store.mkdir(parents=True, exist_ok=True)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        index = _load_index(index_path)
    except _IndexUnreadable as error:
        print(f"Reconcile aborted: {error}", file=sys.stderr)
        return 1
    pointers = index["pointers"]
    existing_sids = {
        pointer.get("sid")
        for pointer in pointers
        if isinstance(pointer, dict) and pointer.get("sid")
    }
    added = 0
    for session_file in sorted(store.glob("**/*.json")):
        sid = session_file.stem
        if sid in existing_sids:
            continue
        content_hash = hashlib.sha256(session_file.read_bytes()).hexdigest()
        pointers.append(
            {
                "sid": sid,
                "mi": 0,
                "bi": 0,
                "ch": content_hash,
                "path": ["deepcli", sid[:8]],
                "source": "deepcli",
                "file": str(session_file),
            }
        )
        existing_sids.add(sid)
        added += 1
    index_path.write_text(json.dumps(index, indent=2) + "\n")
    print(f"Reconciled {added} deepcli pointer(s) into {index_path}")
    return 0


def main(argv: List[str] = None) -> int:
    # Bare invocation → native menu (no subcommand required).
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        return _menu()

    parser = argparse.ArgumentParser(
        description=f"{PRODUCT} bridge: deepcli sessions ↔ Termux Codex"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="check bridge prerequisites")
    doctor.add_argument("--strict", action="store_true", help="exit 1 if any check is missing")

    subparsers.add_parser("build", help="build codex-cli with Cargo")
    subparsers.add_parser("menu", help="show native-style entry menu")

    run = subparsers.add_parser(
        "run",
        help="run preferred frontend (deepcli if available, else native Codex)",
    )
    run.add_argument(
        "--codex-native",
        action="store_true",
        help="force the stock OpenAI Codex binary (may require ChatGPT / API key)",
    )
    run.add_argument("args", nargs=argparse.REMAINDER)

    deepcli_p = subparsers.add_parser("deepcli", help="launch deepcli")
    deepcli_p.add_argument("args", nargs=argparse.REMAINDER)

    native = subparsers.add_parser("codex-native", help="launch stock OpenAI Codex binary")
    native.add_argument("args", nargs=argparse.REMAINDER)

    subparsers.add_parser("reconcile", help="merge deepcli sessions into codex_index.json")

    args = parser.parse_args(argv)
    if args.command == "doctor":
        return _doctor(args.strict)
    if args.command == "build":
        return _build()
    if args.command == "menu":
        return _menu()
    if args.command == "run":
        run_args = args.args
        if run_args and run_args[0] == "--":
            run_args = run_args[1:]
        return _run(run_args, force_native=args.codex_native)
    if args.command == "deepcli":
        run_args = args.args
        if run_args and run_args[0] == "--":
            run_args = run_args[1:]
        return _run_deepcli(run_args)
    if args.command == "codex-native":
        run_args = args.args
        if run_args and run_args[0] == "--":
            run_args = run_args[1:]
        return _run_codex_native(run_args)
    return _reconcile()


if __name__ == "__main__":
    raise SystemExit(main())
