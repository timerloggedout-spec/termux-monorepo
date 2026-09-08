import json
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
from archwiz.providers.base import BaseProvider, ProviderConfig
from archwiz.config import DEEPCLI_DIR

class DeepSeekProvider(BaseProvider):
    """
    DeepSeek provider that wraps the existing deepcli tool.
    """

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            config = ProviderConfig(name="deepseek", model="deepseek-chat")
        super().__init__(config)
        self.cli_path = DEEPCLI_DIR / "deepcli.py"

    def _run_cli(self, args: List[str]) -> Dict[str, Any]:
        if not self.cli_path.exists():
            raise FileNotFoundError(f"deepcli not found at {self.cli_path}")

        cmd = ["python3", str(self.cli_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": result.stderr, "status": "failed"}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"output": result.stdout, "status": "ok"}

    def send_message(self, message: str, session_id: Optional[str] = None) -> str:
        args = ["send", message]
        if session_id:
            args.extend(["--session", session_id])

        res = self._run_cli(args)
        return res.get("response", res.get("output", ""))

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        res = self._run_cli(["history", session_id])
        return res.get("messages", [])

    def list_sessions(self) -> List[Dict[str, Any]]:
        res = self._run_cli(["list"])
        return res.get("sessions", [])

    def new_session(self) -> str:
        res = self._run_cli(["new"])
        return res.get("session_id", "")
