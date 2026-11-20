import subprocess
import os

def execute_concurrent_tmux_job(target_file, command_string, workspace_path):
    clean_id = target_file.replace('.', '_').replace('/', '_')
    session_name = f"agent_job_{clean_id}"
    log_path = os.path.join(workspace_path, f"temp_{clean_id}_run.log")
    subprocess.run(["tmux", "kill-session", "-t", session_name], capture_output=True)
    full_cmd = f"cd {workspace_path} && {command_string} > {log_path} 2>&1"
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name, full_cmd])
    return session_name, log_path

def check_job_status(session_name):
    check = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    return check.returncode == 0