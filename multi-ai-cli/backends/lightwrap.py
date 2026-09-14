"""Python adapter for the parent-owned lightweight browser-wrapper runner.

The adapter transports only the prompt and normalized runner result. Browser profiles,
cookies, local storage, headers, endpoint bodies, and screenshots remain inaccessible
behind the runner boundary.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from .base import ChatBackend


class LightwrapError(RuntimeError):
    """A normalized lightwrap runner failure."""


class LightwrapBackend(ChatBackend):
    """A browser-wrapper provider adapter backed by ``wrapper/lightwrap.mjs``."""

    def __init__(
        self,
        session_manager=None,
        *,
        provider: str,
        account: str = "default",
        profile_root: str | Path | None = None,
        node_bin: str = "node",
        runner_path: str | Path | None = None,
    ):
        self.session_manager = session_manager
        self.provider = provider
        self.account = account
        self.profile_root = Path(profile_root).expanduser() if profile_root else None
        self.node_bin = node_bin
        self.runner_path = Path(runner_path) if runner_path else Path(__file__).parent.parent / "wrapper" / "lightwrap.mjs"

    def _command(self, action: str, *, prompt: str | None = None) -> list[str]:
        command = [
            self.node_bin,
            str(self.runner_path),
            "--action",
            action,
            "--provider",
            self.provider,
            "--account",
            self.account,
        ]
        if self.profile_root:
            command.extend(["--profile-root", str(self.profile_root)])
        if prompt is not None:
            command.extend(["--prompt", prompt])
        return command

    def _local_config_path(self) -> Path:
        root = self.profile_root or (Path.home() / ".multi-ai-cli" / "wrappers")
        safe_provider = "".join(char if char.isalnum() or char in "_-" else "_" for char in self.provider)
        safe_account = "".join(char if char.isalnum() or char in "_-" else "_" for char in self.account)
        directory = root / "status" / safe_provider / safe_account
        directory.mkdir(parents=True, exist_ok=True)
        try:
            directory.chmod(0o700)
        except OSError:
            pass
        return directory / "profile.json"

    @staticmethod
    def _selector_values(values: tuple[str, ...] | list[str], label: str) -> list[str]:
        if not values or any(not isinstance(value, str) or not value or len(value) > 512 for value in values):
            raise LightwrapError(f"Provide one or more valid {label} selector values.")
        return list(values)

    def configure_profile(
        self,
        *,
        url: str,
        input_mode: str,
        input_selectors: tuple[str, ...] | list[str],
        submit_selectors: tuple[str, ...] | list[str],
        response_selectors: tuple[str, ...] | list[str],
        ready_selectors: tuple[str, ...] | list[str],
        login_selectors: tuple[str, ...] | list[str] = (),
    ) -> Path:
        """Save non-secret, user-validated local selector metadata for one provider/account."""

        if not isinstance(url, str) or not url.startswith(("https://", "http://")) or len(url) > 2048:
            raise LightwrapError("Provide a valid http(s) browser URL for the local selector profile.")
        if input_mode not in {"textarea", "react-textarea", "contenteditable"}:
            raise LightwrapError("Input mode must be textarea, react-textarea, or contenteditable.")
        payload = {
            "url": url,
            "state": "probe-required",
            "allow_send_after_probe": True,
            "input": {"mode": input_mode, "candidates": self._selector_values(input_selectors, "input")},
            "submit": {"candidates": self._selector_values(submit_selectors, "submit")},
            "response": {"candidates": self._selector_values(response_selectors, "response")},
            "ready": {"candidates": self._selector_values(ready_selectors, "ready")},
            "login": {"candidates": list(login_selectors)},
        }
        path = self._local_config_path()
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            temporary.chmod(0o600)
        except OSError:
            pass
        temporary.replace(path)
        return path

    @staticmethod
    def _parse_result(stdout: str) -> dict[str, Any]:
        candidates = [line.strip() for line in stdout.splitlines() if line.strip()]
        if not candidates:
            raise LightwrapError("Lightweight wrapper returned no normalized result.")
        try:
            payload = json.loads(candidates[-1])
        except json.JSONDecodeError as exc:
            raise LightwrapError("Lightweight wrapper returned invalid normalized output.") from exc
        if not isinstance(payload, dict):
            raise LightwrapError("Lightweight wrapper result must be an object.")
        if payload.get("observed_state") == "error":
            raise LightwrapError(str(payload.get("error") or "Lightweight wrapper failed."))
        return payload

    def run_action(self, action: str, *, prompt: str | None = None) -> dict[str, Any]:
        """Run one generic wrapper action and parse its final JSON line only."""

        if not self.runner_path.is_file():
            raise LightwrapError("Lightweight wrapper runner is unavailable in this checkout.")
        try:
            completed = subprocess.run(
                self._command(action, prompt=prompt),
                check=False,
                capture_output=True,
                text=True,
                timeout=150 if action == "send" else 75,
                env={**os.environ, "NO_COLOR": "1"},
            )
        except FileNotFoundError as exc:
            raise LightwrapError("Node.js is required for the lightweight wrapper runner.") from exc
        except subprocess.TimeoutExpired as exc:
            raise LightwrapError(f"Lightweight wrapper {action} timed out.") from exc

        payload = self._parse_result(completed.stdout)
        if completed.returncode != 0:
            raise LightwrapError(str(payload.get("error") or f"Lightweight wrapper {action} failed."))
        return payload

    def capabilities(self) -> dict[str, Any]:
        """Return non-secret descriptor and local readiness metadata."""

        return self.run_action("capabilities")

    def connect(self) -> dict[str, Any]:
        """Start a visible, user-mediated provider sign-in session."""

        return self.run_action("connect")

    def probe(self) -> dict[str, Any]:
        """Perform a redacted local selector/readiness probe."""

        return self.run_action("probe")

    def is_available(self) -> bool:
        try:
            result = self.capabilities()
        except LightwrapError:
            return False
        status = result.get("status") or {}
        return bool(result.get("allow_send_after_probe") and status.get("observed_state") == "send-ready")

    def send_message(self, message: str, context: list[dict], **kwargs) -> str:
        """Send through a previously verified provider browser profile."""
        result = self.run_action("send", prompt=message)
        text = result.get("text")
        if not isinstance(text, str) or not text.strip():
            raise LightwrapError("Lightweight wrapper completed without normalized response text.")
        return text
