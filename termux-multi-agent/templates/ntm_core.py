import subprocess
from typing import Optional

def tmux_new_session(session_name: str, command: str, detach: bool = True) -> bool:
    cmd = ["tmux", "new-session", "-d" if detach else "", "-s", session_name, command]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0

def tmux_send_keys(session_name: str, keys: str, target_pane: Optional[str] = None) -> bool:
    cmd = ["tmux", "send-keys"]
    if target_pane:
        cmd.extend(["-t", f"{session_name}:{target_pane}"])
    else:
        cmd.extend(["-t", session_name])
    cmd.append(keys)
    cmd.append("C-m")
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0

def tmux_kill_session(session_name: str) -> bool:
    result = subprocess.run(["tmux", "kill-session", "-t", session_name], capture_output=True)
    return result.returncode == 0

def tmux_list_sessions() -> list:
    result = subprocess.run(["tmux", "list-sessions"], capture_output=True, text=True)
    return [line.split(":")[0] for line in result.stdout.splitlines() if ":" in line]
