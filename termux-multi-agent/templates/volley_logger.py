import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

VOLLEY_LOG = Path("~/termux-multi-agent/workspace/volley_log.jsonl").expanduser()

def log_volley(
    volley_id: str,
    from_agent: str,
    to_agent: str,
    status: str,
    volley_type: str,
    file: str,
    strategy: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    success: Optional[bool] = None,
    error: Optional[str] = None,
    dependencies: Optional[list] = None,
    priority: str = "efficiency",
    cedar_script: bool = False,
    cid_py: bool = False,
    **kwargs
) -> None:
    log_entry = {
        "volley_id": volley_id,
        "from_agent": from_agent,
        "to_agent": to_agent,
        "status": status,
        "type": volley_type,
        "file": file,
        "strategy": strategy,
        "start_time": start_time or datetime.now().isoformat() + "Z",
        "end_time": end_time,
        "duration_sec": kwargs.get("duration_sec"),
        "success": success,
        "error": error,
        "dependencies": dependencies or [],
        "priority": priority,
        "cedar_script": cedar_script,
        "cid_py": cid_py,
        **kwargs
    }
    with open(VOLLEY_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
