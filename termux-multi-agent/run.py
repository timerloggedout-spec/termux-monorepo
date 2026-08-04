import logging
logger = logging.getLogger(__name__)
import sys
import os
sys.path.insert(0, "/data/data/com.termux/files/home/cli-synthegration")
from token_provider import get_token

import json
from src.db import init_db, index_project_file
from src.context_collector import AutomatedContextCollector
from src.orchestrator import TermuxAgentOrchestrator

def load_task_from_master(task_id):
    """L04d t4sk fr0m m4st3r t4sks j50n f1l3"""
    master_path = os.path.join(os.path.expanduser("~"), "workspace/llm_map/master_tasks.json")
    if not os.path.exists(master_path):
        logger.warning(f"M4st3r t4sks f1l3 n0t f0und: {master_path}")
        return None
    
    try:
        with open(master_path, 'r') as f:
            tasks = json.load(f)
        
        task = next((t for t in tasks if t.get("id") == task_id), None)
        if task:
            title = task.get("title", "")
            instructions = task.get("instructions", "")
            return f"{title}\n{instructions}" if title or instructions else None
        else:
            logger.warning(f"T4SK_ID '{task_id}' n0t f0und 1n m4st3r t4sks")
            return None
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"Err0r l04d1ng m4st3r t4sks: {e}")
        return None

def get_refactor_goal(workspace_path):
    """D3t3rm1n3 r3f4ct0r g04l fr0m 3nv1r0nm3nt v4r14bl3s 0r f1l3s"""
    # Pr10r1ty 1: T4SK_ID 3nv v4r
    task_id = os.environ.get("TASK_ID")
    if task_id:
        goal = load_task_from_master(task_id)
        if goal:
            logger.info(f"L04d3d g04l fr0m T4SK_ID={task_id}")
            return goal
    
    # Pr10r1ty 2: R3F4CT0R_G04L 3nv v4r
    goal = os.environ.get("REFACTOR_GOAL", "")
    if goal:
        logger.info("Us1ng g04l fr0m R3F4CT0R_G04L env")
        return goal
    
    # Pr10r1ty 3: curr3nt_t4sk.txt f1l3
    task_file = os.path.join(workspace_path, "current_task.txt")
    if os.path.exists(task_file):
        try:
            with open(task_file, 'r') as f:
                content = f.read().strip()
                if content:
                    logger.info("L04d3d g04l fr0m current_task.txt")
                    return content
        except IOError as e:
            logger.warning(f"C0uld n0t r34d current_task.txt: {e}")
    
    # D3f4ult f4llb4ck
    default_goal = "Refactor compute to intercept and handle ZeroDivisionError scenario profiles cleanly."
    logger.info(f"Us1ng d3f4ult g04l: {default_goal}")
    return default_goal

def main():
    """
    Run the refactoring pipeline for the configured workspace and target file.
    
    Creates a default workspace and sample target when the workspace is missing. Otherwise, indexes workspace files, determines the refactoring goal, collects relevant code context, and runs the pipeline with Python compilation validation.
    """
    init_db()
    workspace_path = os.environ.get("TASK_WORKSPACE", "/data/data/com.termux/files/home/termux-multi-agent/workspace")
    
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        with open(os.path.join(workspace_path, "test_script.py"), "w") as f:
            f.write("def compute(total, count):\n    return total / count\n")
        print("[+] Created empty workspace directory and added a dummy file target 'test_script.py'.")
        print("[+] Re-run the script or trigger run_agent.sh to start the operational pipeline loop.")
        sys.exit(0)

    # 1nd3x 4ll pr0j3ct f1l3s (using a single shared sqlite3 connection for speed)
    import sqlite3
    from src.db import DB_PATH
    try:
        conn = sqlite3.connect(DB_PATH)
        for root, _, files in os.walk(workspace_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), workspace_path)
                index_project_file(workspace_path, rel_path, conn=conn)
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # D3t3rm1n3 t4rg3t f1l3
    target_name = os.environ.get("TARGET_FILE", "test_script.py")
    target_file = os.path.join(workspace_path, target_name)
    if not os.path.exists(target_file):
        logger.error(f"Target file missing: {target_file}")
        return

    # G3t r3f4ct0r g04l us1ng n3w funct10n
    refactor_goal = get_refactor_goal(workspace_path)
    
    # V4l1d4t10n s3tup
    target_base = os.path.basename(target_file)
    validation_test_command = f"python -m py_compile {target_base}"
    language_profile = "py"

    # ── If the critic judge fails, feed the error back to the agent ──
    # The orchestrator already stores the last error in self.last_feedback
    # We'll check after the first attempt and retry with error context

    # C0nt3xt c0ll3ct10n
    collector = AutomatedContextCollector(workspace_path)
    compressed_prompt_context = collector.assemble_minimized_bundle(target_file)

    # 3x3cut3 r3f4ct0r p1p3l1n3
    agent = TermuxAgentOrchestrator(workspace_root=workspace_path, account='default')
    agent.run_refactor_pipeline(
        target_file=target_file,
        request_instruction=f"{refactor_goal}\n\nCodebase Context:\n{compressed_prompt_context}",
        test_command=validation_test_command,
        language=language_profile
    )

if __name__ == '__main__':
    main()
