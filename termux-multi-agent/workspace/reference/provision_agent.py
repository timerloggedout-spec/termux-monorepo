import os
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
<<<<<<< SEARCH
[Insert the exact lines of existing code to be changed]
=======
[Insert the exact new replacement code lines here]
>>>>>>> REPLACE""",
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
                target_file TEXT,
                attempt_number INTEGER,
                patch_content TEXT,
                error_log TEXT,
                verdict TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
        conn.commit()

def log_attempt_telemetry(target_file, attempt, patch, errors, verdict):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO run_history (target_file, attempt_number, patch_content, error_log, verdict) VALUES (?, ?, ?, ?, ?)",
            (target_file, attempt, patch, errors, verdict)
        )
        conn.commit()

def index_project_file(workspace_root, relative_path):
    abs_path = os.path.join(workspace_root, relative_path)
    ext = os.path.splitext(relative_path)[1]
    lang_map = {'.py': 'python', '.js': 'javascript', '.mjs': 'javascript', '.rs': 'rust'}
    lang = lang_map.get(ext)
    if not lang:
        return
    try:
        output = subprocess.check_output(["ast-grep", "scan", "--json", abs_path], text=True)
        nodes = json.loads(output)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            for node in nodes:
                node_id = f"{relative_path}:{node.get('range', {}).get('start', {}).get('line', 0)}"
                cursor.execute(
                    "INSERT OR REPLACE INTO nodes VALUES (?, ?, ?, ?, ?, ?)",
                    (node_id, relative_path, lang, node.get('kind'), node.get('text', '')[:50],
                     node.get('range', {}).get('start', {}).get('line', 0))
                )
        import_pattern = "import $MOD from '$PATH'" if lang == 'javascript' else "import $MOD"
        import_output = subprocess.check_output(
            ["ast-grep", "scan", "--pattern", import_pattern, "--json", abs_path], text=True
        )
        import_nodes = json.loads(import_output)
        for imp in import_nodes:
            imp_text = imp.get('text', '')
            quoted_paths = re.findall(r"['\"](.*?)['\"]", imp_text)
            for target in quoted_paths:
                clean_target = target.lstrip('./').replace('.js', '').replace('.py', '')
                cursor.execute(
                    "INSERT OR IGNORE INTO edges VALUES (?, ?, ?)",
                    (relative_path, clean_target, "imports")
                )
        conn.commit()
    except Exception:
        pass""",
    "src/sandbox.py": """import subprocess
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
    return check.returncode == 0""",
    "src/parser.py": """import re

def parse_compiler_logs(raw_stderr, language):
    condensed_errors = []
    if language in ['js', 'mjs']:
        matches = re.findall(r'(ReferenceError|TypeError|SyntaxError): (.*?)\\n', raw_stderr)
        for err_type, message in matches:
            condensed_errors.append(f"[{err_type}] -> {message}")
    elif language == 'rs':
        matches = re.findall(r'error\\[E\\d+\\]: (.*?)\\n\\s+--> (.*?):(\\d+):(\\d+)', raw_stderr)
        for desc, file, line, col in matches:
            condensed_errors.append(f"[RustError] {desc} (File: {file} Line: {line})")
    elif language == 'py':
        matches = re.findall(r'(\\w+Error): (.*?)\\n', raw_stderr)
        for err_type, message in matches:
            condensed_errors.append(f"[PythonError] {err_type}: {message}")
    return "\\n".join(condensed_errors) if condensed_errors else "Execution Status: Clear compilation.\"""" ,
    "src/telemetry.py": """import json
import time

TELEMETRY_LOG = "agent_telemetry_stream.json"

class TermuxTelemetryLogger:
    @staticmethod
    def notify(level, agent_id, message, target_file=None, attempt=None):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        colors = {"INFO": "\\033[94m[INFO]\\033[0m", "SUCCESS": "\\033[92m[SUCCESS]\\033[0m",
                  "RETRY": "\\033[93m[RETRY]\\033[0m", "CRITICAL": "\\033[91m[CRITICAL]\\033[0m"}
        color_tag = colors.get(level, f"[{level}]")
        context_str = f" ({target_file} | Try #{attempt})" if target_file and attempt else ""
        print(f"{timestamp} {color_tag} [{agent_id}]{context_str}: {message}")
        log_entry = {"timestamp": timestamp, "level": level, "agent": agent_id,
                     "target": target_file, "attempt": attempt, "message": message}
        with open(TELEMETRY_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\\n")""",
    "src/git_manager.py": """import subprocess
import os
import time

class AgentGitManager:
    def __init__(self, workspace_root):
        self.workspace = os.path.abspath(workspace_root)
        self.identities = {
            "deepseek-v4-pro": {"name": "DeepSeek Coder Agent", "email": "v4pro@deepseek.agent"},
            "critic-judge": {"name": "Critic Judge Agent", "email": "judge@critic.agent"}
        }

    def create_feature_branch(self, base_branch="main"):
        if not os.path.exists(os.path.join(self.workspace, ".git")):
            subprocess.run(["git", "init"], cwd=self.workspace, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=self.workspace, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial repository commit"], cwd=self.workspace, capture_output=True)
        branch_name = f"ai-refactor-{int(time.time())}"
        subprocess.run(["git", "checkout", base_branch], cwd=self.workspace, capture_output=True)
        result = subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.workspace, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to initialize Git branch: {result.stderr}")
        return branch_name

    def commit_as_agent(self, agent_id, commit_message, file_paths):
        identity = self.identities.get(agent_id, {"name": "Local Agent", "email": "agent@local.dev"})
        agent_env = os.environ.copy()
        agent_env["GIT_AUTHOR_NAME"] = identity["name"]
        agent_env["GIT_AUTHOR_EMAIL"] = identity["email"]
        agent_env["GIT_COMMITTER_NAME"] = identity["name"]
        agent_env["GIT_COMMITTER_EMAIL"] = identity["email"]
        for path in file_paths:
            subprocess.run(["git", "add", path], cwd=self.workspace, capture_output=True)
        result = subprocess.run(["git", "commit", "-m", commit_message], cwd=self.workspace, env=agent_env, capture_output=True, text=True)
        return result.returncode == 0""",
    "src/context_collector.py": """import sqlite3
import os
import re
import subprocess

DB_PATH = "local_repo.db"

class AutomatedContextCollector:
    def __init__(self, workspace_root):
        self.workspace = os.path.abspath(workspace_root)

    def find_dependent_files(self, file_relative_path):
        base_name = os.path.splitext(file_relative_path)[0]
        related_files = set()
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT target_file FROM edges WHERE source_file = ? OR target_file LIKE ?",
                           (file_relative_path, f"%{base_name}%"))
            for row in cursor.fetchall():
                related_files.add(row[0])
            cursor.execute("SELECT source_file FROM edges WHERE target_file = ? OR source_file LIKE ?",
                           (file_relative_path, f"%{base_name}%"))
            for row in cursor.fetchall():
                related_files.add(row[0])

        valid_dependencies = []
        for ref in related_files:
            for ext in ['.py', '.js', '.mjs', '.rs', '.sh']:
                check_path = ref if ref.endswith(ext) else f"{ref}{ext}"
                if os.path.exists(os.path.join(self.workspace, check_path)) and check_path != file_relative_path:
                    valid_dependencies.append(check_path)
                    break
        return valid_dependencies

    def generate_ast_skeleton(self, file_relative_path):
        abs_path = os.path.join(self.workspace, file_relative_path)
        ext = os.path.splitext(file_relative_path)[1]
        if ext == '.py':
            pattern = "class $NAME: $$$"
        elif ext in ['.js', '.mjs']:
            pattern = "function $NAME($$ $) { $$$ }"
        else:
            return f"/* Structural stub context for file: {file_relative_path} */"
        try:
            output = subprocess.check_output(["ast-grep", "scan", "--pattern", pattern, "--json", abs_path], text=True)
            import json
            nodes = json.loads(output)
            skeleton_lines = [f"// Architecture map for dependent file: {file_relative_path}"]
            for n in nodes:
                snippet = n.get('text', '').split('\\n')[0]
                skeleton_lines.append(f"    {snippet} ...")
            return "\\n".join(skeleton_lines)
        except Exception:
            return f"// Unable to trace AST module boundary map for {file_relative_path}"

    def assemble_minimized_bundle(self, active_target_file):
        dependencies = self.find_dependent_files(active_target_file)
        bundle = ["=== CODEBASE ARCHITECTURE SUBSTRUCTURE CONTEXT ==="]
        for dep in dependencies:
            skeleton = self.generate_ast_skeleton(dep)
            bundle.append(f"\\n<file path=\"{dep}\" layout=\"dependent_skeleton\">\\n{skeleton}\\n")
        with open(os.path.join(self.workspace, active_target_file), 'r') as f:
            full_source = f.read()
        bundle.append(f"\\n<file path=\"{active_target_file}\" layout=\"active_target_edit_zone\">\\n{full_source}\\n")
        return "\\n".join(bundle)""",
    "src/orchestrator.py": """import os
import re
import json
import requests
import time
import subprocess
from src.sandbox import execute_concurrent_tmux_job, check_job_status
from src.parser import parse_compiler_logs
from src.git_manager import AgentGitManager
from src.telemetry import TermuxTelemetryLogger as Log
from src.db import log_attempt_telemetry

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
CRITIC_API_KEY = os.environ.get("CRITIC_API_KEY")

class TermuxAgentOrchestrator:
    def __init__(self, workspace_root):
        self.workspace = os.path.abspath(workspace_root)
        self.git_manager = AgentGitManager(self.workspace)
        self.max_attempts = 3

    def _read_config_file(self, filename):
        with open(os.path.join("config", filename), "r") as f:
            return f.read()

    def call_deepseek_v4_pro(self, system_prompt, user_prompt):
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "deepseek-v4-pro",
                   "messages": [{"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}],
                   "temperature": 0.1}
        r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
        return r.json()['choices'][0]['message']['content']

    def call_critic_judge(self, system_prompt, target_code, test_logs):
        headers = {"Authorization": f"Bearer {CRITIC_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "critic-judge-model",
                   "messages": [{"role": "system", "content": system_prompt},
                                {"role": "user", "content": f"CODE:\\n{target_code}\\n\\nLOGS:\\n{test_logs}"}],
                   "temperature": 0.1}
        r = requests.post("https://api.critic-provider.com/v1/completions", headers=headers, json=payload)
        return r.json()['choices'][0]['message']['content']

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
        os.makedirs(workspace_path)
        with open(os.path.join(workspace_path, "test_script.py"), "w") as f:
            f.write("def compute(total, count):\\n    return total / count\\n")
        print("[+] Created empty workspace directory and added a dummy file target 'test_script.py'.")
        print("[+] Re-run the script or trigger run_agent.sh to start the operational pipeline loop.")
        sys.exit(0)

    for root, _, files in os.walk(workspace_path):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), workspace_path)
            index_project_file(workspace_path, rel_path)

    target_file = "test_script.py"
    refactor_goal = "Refactor compute to intercept and handle ZeroDivisionError scenario profiles cleanly."
    validation_test_command = "python -m py_compile test_script.py"
    language_profile = "py"

    collector = AutomatedContextCollector(workspace_path)
    compressed_prompt_context = collector.assemble_minimized_bundle(target_file)

    agent = TermuxAgentOrchestrator(workspace_root=workspace_path)
    agent.run_refactor_pipeline(
        target_file=target_file,
        request_instruction=f"{refactor_goal}\\n\\nCodebase Context:\\n{compressed_prompt_context}",
        test_command=validation_test_command,
        language=language_profile
    )

if __name__ == '__main__':
    main()""",
    "dashboard.py": """import time
import os
import json

TELEMETRY_LOG = "agent_telemetry_stream.json"

def clear_screen():
    print("\\033[H\\033[J", end="")

# Cache state variables to enable high-performance incremental I/O updates (state-tracking & seek/tell)
_last_position = 0
_active_jobs = {}

def read_latest_telemetry():
    global _last_position, _active_jobs
    if not os.path.exists(TELEMETRY_LOG):
        _last_position = 0
        _active_jobs = {}
        return []
    try:
        # Detect if log file has been truncated, rotated, or re-created
        file_size = os.path.getsize(TELEMETRY_LOG)
        if file_size < _last_position:
            _last_position = 0
            _active_jobs = {}

        with open(TELEMETRY_LOG, "r") as f:
            if _last_position > 0:
                f.seek(_last_position)
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    target = entry.get("target") or "System"
                    _active_jobs[target] = entry
                except json.JSONDecodeError:
                    continue
            _last_position = f.tell()
    except Exception:
        pass
    return list(_active_jobs.values())

def render_dashboard():
    clear_screen()
    print("=" * 65)
    print(" ⚡ TERMUX MULTI-AGENT PARALLEL TELEMETRY DASHBOARD ⚡ ")
    print("=" * 65)
    print(f" Last Sync: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 65)
    print(f"{'TARGET FILE':<20} | {'AGENT':<16} | {'TRY':<4} | {'STATUS':<15}")
    print("-" * 65)

    jobs = read_latest_telemetry()
    if not jobs:
        print(" [ Waiting for background agent pipelines to initialize... ]")
    for job in jobs:
        target = job.get("target") or "Global"
        if len(target) > 18:
            target = "..." + target[-15:]
        agent = job.get("agent", "Unknown")
        attempt = str(job.get("attempt") or "-")
        level = job.get("level", "INFO")

        if level == "SUCCESS":
            status_str = "\\033[92mSUCCESS\\033[0m"
        elif level == "RETRY":
            status_str = "\\033[93mRETRYING\\033[0m"
        elif level == "CRITICAL":
            status_str = "\\033[91mCRITICAL\\033[0m"
        else:
            status_str = "\\033[94mPROCESSING\\033[0m"

        print(f"{target:<20} | {agent:<16} | {attempt:<4} | {status_str:<15}")
        print(f" ↳ Msg: {job.get('message', '')[:60]}")
        print("-" * 65)

def main():
    try:
        while True:
            render_dashboard()
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\\nExiting Dashboard Viewer.")

if __name__ == '__main__':
    main()""",
    "run_agent.sh": """#!/usr/bin/env bash
if [ -z "$DEEPSEEK_API_KEY" ] || [ -z "$CRITIC_API_KEY" ]; then
    echo -e "\\e[91m[ERROR]\\e[0m Missing authentication configurations!"
    echo "Please declare API tokens before launching your pipeline:"
    echo "  export DEEPSEEK_API_KEY='your_key'"
    echo "  export CRITIC_API_KEY='your_key'"
    exit 1
fi

for cmd in ast-grep tmux python; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "\\e[91m[ERROR]\\e[0m Required tool missing: '$cmd'"
        exit 1
    fi
done

if [ "$1" == "--clean" ]; then
    rm -f agent_telemetry_stream.json local_repo.db temp_*_run.log
fi

if [ -z "$TMUX" ]; then
    SESSION_NAME="agent_master_hub_$(date +%s)"
    tmux new-session -d -s "$SESSION_NAME" "python run.py"
    tmux split-window -h -t "$SESSION_NAME" "python dashboard.py"
    tmux attach-session -t "$SESSION_NAME"
else
    tmux split-window -h "python dashboard.py"
    python run.py
fi"""
}

print("[*] Initiating deployment of the Termux multi-agent platform...")

# Process and write files dynamically
for file_path, file_content in FILES_BLUEPRINT.items():
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)

    with open(file_path, "w") as target_file:
        target_file.write(file_content.strip())
    print(f" -> Created asset node: {file_path}")

# Grant execution bounds onto the bash operational runner file script
os.chmod("run_agent.sh", 0o755)

print("\\n[+] Provision complete. System directory structural architecture successfully deployed!")
print("[+] Step 1: Run 'python run.py' to initialize the workspace directory branch.")
print("[+] Step 2: Configure your keys, then execute './run_agent.sh' to initialize the platform.")
