import sys, os, re, json, subprocess
from pathlib import Path
from datetime import datetime
import logging

sys.path.insert(0, "/data/data/com.termux/files/home/deepcli")
from deepcli.core import get_token, create_session, chat_completion, fetch_sessions

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s")
logger = logging.getLogger("orchestrator")

class TermuxAgentOrchestrator:
    def __init__(self, workspace_root: str, account: str = "default"):
        self.workspace = Path(workspace_root)
        self.token = self._load_token(account)
        self.session_id = None
        self._init_session()

    def _load_token(self, account: str) -> str:
        """Return token for given account. account='default' uses deepcli config,
        account='cookies2' uses cookies_2.json token extraction."""
        if account == "cookies2":
            # extract token from cookies_2.json (aws-waf-token + ds_session_id cookie string)
            cookie_path = Path("/data/data/com.termux/files/home/deepseek-cli/cookies_2.json")
            if cookie_path.exists():
                try:
                    data = json.loads(cookie_path.read_text())
                    # format as cookie header for the API (or use aws-waf-token directly)
                    aws_token = None
                    session_id = None
                    for c in data.get("cookies", []):
                        if c["name"] == "aws-waf-token":
                            aws_token = c["value"]
                        elif c["name"] == "ds_session_id":
                            session_id = c["value"]
                    if aws_token:
                        return aws_token  # Bearer token expects aws-waf-token
                except Exception as e:
                    logger.warning(f"Failed to parse cookies_2.json: {e}")
        # default: use deepcli's get_token
        return get_token()

    def _init_session(self):
        try:
            self.session_id = create_session(self.token)
            logger.info(f"Agent session created: {self.session_id}")
        except Exception as e:
            logger.warning(f"Session creation failed: {e}")

    def call_deepseek_v4_pro(self, system_prompt: str, user_prompt: str) -> str:
        full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
        if self.session_id:
            try:
                return chat_completion(self.token, full_prompt, self.session_id)
            except Exception as e:
                logger.warning(f"Completion failed, retrying new session: {e}")
                self._init_session()
        if not self.session_id:
            self.session_id = create_session(self.token)
        return chat_completion(self.token, full_prompt, self.session_id)

    def parse_and_apply_cedar_diff(self, target_file, coder_output):
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", coder_output, re.DOTALL)
        if not code_blocks:
            return False, "No code block found in LLM output"
        new_code = code_blocks[-1]
        Path(target_file).write_text(new_code)
        return True, f"Applied patch to {target_file}"

    def run_refactor_pipeline(self, target_file, language="python", request_instruction=None, test_command=None):
        logger.info("Initializing isolated branch...")
        target = Path(target_file)
        if not target.exists():
            logger.error(f"Target file missing: {target_file}")
            return
        original = target.read_text()
        # ast-grep scan for functions
        funcs = []
        try:
            result = subprocess.check_output(
                ["ast-grep", "--pattern", "def $FUNC($$$ARGS): { $$$BODY }", "--lang", language, "--json", target_file],
                cwd=str(self.workspace), text=True, stderr=subprocess.DEVNULL
            )
            if result.strip():
                matches = json.loads(result)
                funcs = [m.get("metaVariables", {}).get("FUNC", "unknown") for m in matches]
        except Exception:
            pass

        instr = request_instruction or "Refactor this code to improve performance and readability"
        user_prompt = f"File: {target_file}\nFunctions: {funcs}\n{instr}\n```\n{original}\n```"
        coder_system = "You are a 1337 code refactoring assistant. Reply with only the improved code in a code block."

        for attempt in range(3):
            logger.info(f"DeepSeek v4-Pro (try {attempt+1}): Generating code fix...")
            coder_output = self.call_deepseek_v4_pro(coder_system, user_prompt)
            success, msg = self.parse_and_apply_cedar_diff(target_file, coder_output)
            if success:
                logger.info(f"Refactor succeeded: {msg}")
                return
            logger.warning(f"Attempt {attempt+1} failed: {msg}")
        logger.error("All refactor attempts exhausted")

    def search_conversations(self, term: str):
        sessions = fetch_sessions(self.token)
        results = []
        for s in sessions:
            title = s.get("title", "") or s.get("name", "")
            if term.lower() in title.lower():
                results.append(s)
        return results
