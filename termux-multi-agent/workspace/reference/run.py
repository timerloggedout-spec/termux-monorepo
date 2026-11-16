import logging
logger = logging.getLogger(__name__)
import sys
import sys, os
sys.path.insert(0, "/data/data/com.termux/files/home/cli-synthegration")
from token_provider import get_token

import os
import sys
from src.db import init_db, index_project_file
from src.context_collector import AutomatedContextCollector
from src.orchestrator import TermuxAgentOrchestrator

def main():
    init_db()
    workspace_path = "/data/data/com.termux/files/home/termux-multi-agent/workspace"
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        with open(os.path.join(workspace_path, "test_script.py"), "w") as f:
            f.write("def compute(total, count):\n    return total / count\n")
        print("[+] Created empty workspace directory and added a dummy file target 'test_script.py'.")
        print("[+] Re-run the script or trigger run_agent.sh to start the operational pipeline loop.")
        sys.exit(0)

    for root, _, files in os.walk(workspace_path):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), workspace_path)
            index_project_file(workspace_path, rel_path)

    target_file = os.path.join(workspace_path, "test_script.py")
    if not os.path.exists(target_file):
        logger.error(f"Target file missing: {target_file}")
        return
    refactor_goal = "Refactor compute to intercept and handle ZeroDivisionError scenario profiles cleanly."
    validation_test_command = "python -m py_compile test_script.py"
    language_profile = "py"

    collector = AutomatedContextCollector(workspace_path)
    compressed_prompt_context = collector.assemble_minimized_bundle(target_file)

    agent = TermuxAgentOrchestrator(workspace_root=workspace_path, account='default')
    agent.run_refactor_pipeline(
        target_file=target_file,
        request_instruction=f"{refactor_goal}\n\nCodebase Context:\n{compressed_prompt_context}",
        test_command=validation_test_command,
        language=language_profile
    )

if __name__ == '__main__':
    main()