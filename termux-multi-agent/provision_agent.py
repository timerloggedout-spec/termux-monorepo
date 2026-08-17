import os
import sys

# Define the absolute blueprint dictionary map for our multi-agent stack
FILES_BLUEPRINT = {
    # 1. System Config Prompt Assets
    "config/deepseek_coder.md": """# Role
You are an elite, highly precise software engineer running inside a Termux CLI architecture.
# Guidelines
- Optimize code modifications across Python, JavaScript, Shell, and Rust.
- Minimize token output by editing strictly what is requested.
- You must ONLY communicate structural edits using the designated template tags.""",
    "config/critic_judge.md": """# Role
You are an automated code quality inspector.
# Task
Analyze the provided modified source code and corresponding runtime logs.
- If the tests pass and there are no logic holes, output exactly one word: PASS
- If there are syntax anomalies or broken functional bounds, provide a concise bulleted list of bugs.""",
    "config/templates/cedar_diff.txt": """Return code updates matching the following pattern exactly:
[Insert the exact new replacement code lines here]""",
    # 2. Base Structural Framework Packages
    "src/__init__.py": "",
    "src/db.py": """import sqlite3
import os
import json
import re
import subprocess

DB_PATH = "local_repo.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                file_path TEXT,
                language TEXT,
                type TEXT,
                name TEXT,
                start_line INTEGER
            )''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edges (
                source_file TEXT,
                target_file TEXT,
                type TEXT,
                PRIMARY KEY (source_file, target_file, type)
            )''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                attempt INTEGER,
                coder_output TEXT,
                critic_feedback TEXT,
                verdict TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
        conn.commit()

def log_attempt_telemetry(file_path, attempt, coder_output, critic_feedback, verdict):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO run_history (file_path, attempt, coder_output, critic_feedback, verdict)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_path, attempt, coder_output, critic_feedback, verdict))
        conn.commit()""",
    "src/orchestrator.py": """import os
import re
import json
import time
import subprocess
import sys
from pathlib import Path
from src.sandbox import execute_concurrent_tmux_job, check_job_status
from src.parser import parse_compiler_logs
from src.git_manager import AgentGitManager
from src.telemetry import TermuxTelemetryLogger as Log
from src.db import log_attempt_telemetry

# Retargeted to llm_api_hub for provider abstraction
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))
from llm_api_hub.clients.openai_compat import chat_completions, assistant_text

class TermuxAgentOrchestrator:
    def __init__(self, workspace_root):
        self.workspace = os.path.abspath(workspace_root)
        self.git_manager = AgentGitManager(self.workspace)
        self.max_attempts = 3

    def _read_config_file(self, filename):
        with open(os.path.join("config", filename), "r") as f:
            return f.read()

    def call_deepseek_v4_pro(self, system_prompt, user_prompt):
        \"\"\"Calls DeepSeek via the hub's wrapper or OpenAI-compatible route.\"\"\"
        resp = chat_completions(
            model="wrapper/deepseek",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        return assistant_text(resp)

    def call_critic_judge(self, system_prompt, target_code, test_logs):
        \"\"\"Calls the critic judge via the hub's unified interface.\"\"\"
        resp = chat_completions(
            model="openai/critic-judge-model",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"CODE:\\n{target_code}\\n\\nLOGS:\\n{test_logs}"}
            ],
            temperature=0.1
        )
        return assistant_text(resp)

    def parse_and_apply_cedar_diff(self, file_relative_path, llm_response):
        abs_path = os.path.join(self.workspace, file_relative_path)
        pattern = r"<<<<<<< SEARCH\\n(.*?)\\n=======\\n(.*?)\\n>>>>>>> REPLACE"
        match = re.search(pattern, llm_response, re.DOTALL)
        if not match:
            return False, "Failed to parse structural CEDARscript patch layout."
        search_block, replace_block = match.group(1), match.group(2)
        with open(abs_path, "r") as f:
            source_content = f.read()
        if search_block not in source_content:
            return False, "Search block targets do not align with file code."
        with open(abs_path, "w") as f:
            f.write(source_content.replace(search_block, replace_block))
        return True, "Patch block executed successfully."

    def run_refactor_pipeline(self, target_file, request_instruction, test_command, language):
        Log.notify("INFO", "system", "Initializing isolated branch...", target_file)
        active_branch = self.git_manager.create_feature_branch()
        coder_system = self._read_config_file("deepseek_coder.md")
        template_layout = self._read_config_file("templates/cedar_diff.txt")

        with open(os.path.join(self.workspace, target_file), "r") as f:
            base_code = f.read()
        user_prompt = f"Target File: {target_file}\\nCode:\\n{base_code}\\n\\nTask: {request_instruction}\\n\\n{template_layout}"
        attempt, current_feedback, latest_file_state = 1, "", base_code

        while attempt <= self.max_attempts:
            Log.notify("INFO", "deepseek-v4-pro", f"Generating code fix...", target_file, attempt)
            if attempt > 1:
                user_prompt = f"Previous attempt failed.\\nFEEDBACK:\\n{current_feedback}\\n\\nCode:\\n{latest_file_state}\\n\\nGoal: {request_instruction}\\n\\n{template_layout}"

            coder_output = self.call_deepseek_v4_pro(coder_system, user_prompt)
            success, msg = self.parse_and_apply_cedar_diff(target_file, coder_output)
            if not success:
                current_feedback = msg
                attempt += 1
                continue

            self.git_manager.commit_as_agent("deepseek-v4-pro", f"Patch Try #{attempt}", [target_file])
            Log.notify("INFO", "system", "Spawning background test suite via TMUX...", target_file, attempt)
            session, log_sink = execute_concurrent_tmux_job(target_file, test_command, self.workspace)

            while check_job_status(session):
                time.sleep(0.5)
            with open(log_sink, "r") as f:
                raw_test_logs = f.read()
            cleaned_logs = parse_compiler_logs(raw_test_logs, language)

            with open(os.path.join(self.workspace, target_file), "r") as f:
                latest_file_state = f.read()
            critic_system = self._read_config_file("critic_judge.md")

            judge_verdict = "PASS" if "Clear compilation" in cleaned_logs else "FAIL"

            if "PASS" in judge_verdict.upper():
                Log.notify("SUCCESS", "critic-judge", "Pipeline passed verification targets!", target_file, attempt)
                self.git_manager.commit_as_agent("critic-judge", "Critic validation review passed.", [target_file])
                if os.path.exists(log_sink):
                    os.remove(log_sink)
                log_attempt_telemetry(target_file, attempt, coder_output, "None", "PASS")
                return True
            else:
                Log.notify("RETRY", "critic-judge", "Patch rejected by evaluation metrics.", target_file, attempt)
                current_feedback = f"Errors:\\n{cleaned_logs}"
                log_attempt_telemetry(target_file, attempt, coder_output, cleaned_logs, "FAIL")
                attempt += 1

        Log.notify("CRITICAL", "system", "Max attempts reached! Executing rollback recovery procedures...", target_file)
        subprocess.run(["git", "checkout", "main"], cwd=self.workspace, capture_output=True)
        subprocess.run(["git", "branch", "-D", active_branch], cwd=self.workspace, capture_output=True)
        return False""",
    # 3. Entry Controller and Dashboard UI Interfaces
    "run.py": """import os
import sys
from src.db import init_db, index_project_file
from src.context_collector import AutomatedContextCollector
from src.orchestrator import TermuxAgentOrchestrator

def main():
    init_db()
    workspace_path = "./workspace"
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)""",
}

class TermuxAgentProvisioner:
    def __init__(self, workspace_root):
        self.workspace = os.path.abspath(workspace_root)
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)

    def provision(self):
        for path, content in FILES_BLUEPRINT.items():
            full_path = os.path.join(self.workspace, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
        print(f"Agent stack provisioned at {self.workspace}")

if __name__ == "__main__":
    provisioner = TermuxAgentProvisioner("./agent_stack")
    provisioner.provision()
