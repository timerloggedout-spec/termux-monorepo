import re
from pathlib import Path
import shutil
import sys

# --- YOUR ACTUAL FILE PATHS ---
DISPATCH_TASK = Path("~/workspace/llm_map/dispatch_task.py").expanduser()
PARALLEL_AGENTS = Path("~/termux-multi-agent/workspace/src/parallel_agents.py").expanduser()
ORCHESTRATOR = Path("~/termux-multi-agent/workspace/src/orchestrator.py").expanduser()

# --- Verify files exist ---
for p, name in [(DISPATCH_TASK, "dispatch_task.py"), (PARALLEL_AGENTS, "parallel_agents.py"), (ORCHESTRATOR, "orchestrator.py")]:
    if not p.exists():
        print(f"❌ {name} not found at: {p}")
        sys.exit(1)
print("✅ All target files confirmed.")

# --- Backup originals (FIXED: .py.bak extension) ---
backups = {}
for p in [DISPATCH_TASK, PARALLEL_AGENTS, ORCHESTRATOR]:
    backup = p.with_suffix(p.suffix + ".bak")  # .py → .py.bak
    shutil.copy2(p, backup)
    backups[p] = backup
    print(f"✅ Backed up: {p} → {backup}")

# --- Patch dispatch_task.py ---
def patch_dispatch_task():
    content = backups[DISPATCH_TASK].read_text()
    new_imports = """
from templates.volley_logger import log_volley
from templates.priority_matrix import PriorityMatrix
from templates.cid_integration import CIDRegistry
import time
"""
    if "from templates.volley_logger" not in content:
        content = content.replace("import json\n", "import json\n" + new_imports)
    init_code = "priority_matrix = PriorityMatrix()\ncid_registry = CIDRegistry()\n"
    if "priority_matrix = PriorityMatrix()" not in content:
        content = content.replace("import time\n", "import time\n" + init_code)
    volley_log_code = """
    # --- Volley Logging ---
    volley_id = f"{task_id}_{int(time.time())}"
    priority = priority_matrix.get_priority(task_id)
    if not priority:
        priority_matrix.score_task(
            task_id=task_id,
            efficiency_impact=70 if "refactor" in task.get("component", "").lower() else 30,
            elite_impact=90 if "orchestrator" in task.get("source", "") else 50,
            feature_impact=10
        )
        priority = priority_matrix.get_priority(task_id)
    log_volley(
        volley_id=volley_id,
        from_agent="dispatcher",
        to_agent=task.get('assigned_agent', 'deepseek_coder'),
        status="progress",
        volley_type=task.get("component", "unknown"),
        file=task.get("source", ""),
        priority=priority,
        cedar_script=task.get("cedar_script", False),
        cid_py=task.get("cid_py", True)
    )
"""
    if "# --- Volley Logging ---" not in content:
        content = content.replace("    if sf.exists():\n", volley_log_code + "    if sf.exists():\n")
    DISPATCH_TASK.write_text(content)
    print(f"✅ Patched: {DISPATCH_TASK}")

# --- Patch parallel_agents.py ---
def patch_parallel_agents():
    content = backups[PARALLEL_AGENTS].read_text()
    new_imports = """
from templates.volley_logger import log_volley
from templates.priority_matrix import PriorityMatrix
from templates.skillopt_core import SkillTrainer, Rollout
import time
"""
    if "from templates.volley_logger" not in content:
        content = content.replace("from pathlib import Path\n", "from pathlib import Path\n" + new_imports)
    init_code = "skill_trainer = SkillTrainer()\n"
    if "skill_trainer = SkillTrainer()" not in content:
        content = content.replace("from datetime import datetime, timezone\n", "from datetime import datetime, timezone\n" + init_code)
    volley_log_start = """
        volley_id = f"abc_{self.id}_{int(time.time())}"
        log_volley(
            volley_id=volley_id,
            from_agent="parallel_agent",
            to_agent="deepseek_coder",
            status="progress",
            volley_type="abc_test",
            file=self.target_file,
            strategy=self.strategy,
            priority=priority_matrix.get_priority(volley_id)
        )
"""
    if "volley_id = f\"abc_{self.id" not in content:
        content = content.replace("    def run(self, token: str, session_id: str):\n", "    def run(self, token: str, session_id: str):\n" + volley_log_start)
    volley_log_end = """
        # --- Log volley end ---
        log_volley(
            volley_id=volley_id,
            from_agent="parallel_agent",
            to_agent="deepseek_coder",
            status="complete" if self.success else "failed",
            volley_type="abc_test",
            file=self.target_file,
            strategy=self.strategy,
            start_time=self.start_time,
            end_time=time.time(),
            duration_sec=time.time() - self.start_time,
            success=self.success,
            error=self.result if not self.success else None
        )
        # --- Save rollout for SkillOpt ---
        skill_trainer.save_rollout(Rollout(
            input=self.original_code,
            output=self.result,
            success=self.success,
            strategy=self.strategy,
            duration=time.time() - self.start_time,
            elo_delta=self.elo_delta,
            file=self.target_file,
            timestamp=str(int(time.time()))
        ))
"""
    if "# --- Log volley end ---" not in content:
        content = content.replace("        self.end_time = time.time()\n        return self\n", "        self.end_time = time.time()\n" + volley_log_end + "        return self\n")
    PARALLEL_AGENTS.write_text(content)
    print(f"✅ Patched: {PARALLEL_AGENTS}")

# --- Patch orchestrator.py ---
def patch_orchestrator():
    content = backups[ORCHESTRATOR].read_text()
    new_imports = """
from templates.volley_logger import log_volley
from templates.priority_matrix import PriorityMatrix
import json
import time
from datetime import datetime
"""
    if "from templates.volley_logger" not in content:
        content = content.replace("import re\n", "import re\n" + new_imports)
    init_code = "priority_matrix = PriorityMatrix()\n"
    if "priority_matrix = PriorityMatrix()" not in content:
        content = content.replace("logger = logging.getLogger(\"orchestrator\")\n", "logger = logging.getLogger(\"orchestrator\")\n" + init_code)
    volley_log_start = """
        volley_id = f"refactor_{target_file}_{int(time.time())}"
        start_time = datetime.now().isoformat() + "Z"
        log_volley(
            volley_id=volley_id,
            from_agent="orchestrator",
            to_agent="deepseek_coder",
            status="progress",
            volley_type="refactor",
            file=target_file,
            priority=priority_matrix.get_priority(volley_id)
        )
"""
    if "volley_id = f\"refactor_{target_file" not in content:
        content = content.replace("        for attempt in range(3):\n", volley_log_start + "        for attempt in range(3):\n")
    volley_log_success = """
            log_volley(
                volley_id=volley_id,
                from_agent="orchestrator",
                to_agent="deepseek_coder",
                status="complete",
                volley_type="refactor",
                file=target_file,
                start_time=start_time,
                end_time=datetime.now().isoformat() + "Z",
                success=True,
                cid_py="CID.py" in coder_output
            )
"""
    if "status=\"complete\"" not in content:
        content = content.replace("                return True, msg\n", volley_log_success + "                return True, msg\n")
    volley_log_failure = """
    log_volley(
        volley_id=volley_id,
        from_agent="orchestrator",
        to_agent="researcher",
        status="research",
        volley_type="refactor",
        file=target_file,
        start_time=start_time,
        end_time=datetime.now().isoformat() + "Z",
        success=False,
        error=msg
    )
    # --- Create research task ---
    try:
        tasks = json.loads(Path("~/termux-multi-agent/workspace/master_tasks.json").expanduser().read_text())
    except:
        tasks = []
    research_task_id = f"research_{target_file}_{int(time.time())}"
    tasks.append({
        "id": research_task_id,
        "title": f"Research failure: {target_file}",
        "component": "Research",
        "assigned_agent": "researcher",
        "status": "pending",
        "context_mode": "minimized",
        "instructions": f"Failed after 3 attempts. Last error: {msg}",
        "source": target_file,
        "priority": "elite"
    })
    Path("~/termux-multi-agent/workspace/master_tasks.json").expanduser().write_text(json.dumps(tasks, indent=2))
"""
    if "status=\"research\"" not in content:
        content = content.replace("        logger.error(\"All refactor attempts exhausted\")\n", volley_log_failure + "        logger.error(\"All refactor attempts exhausted\")\n")
    ORCHESTRATOR.write_text(content)
    print(f"✅ Patched: {ORCHESTRATOR}")

# --- Execute ---
if __name__ == "__main__":
    patch_dispatch_task()
    patch_parallel_agents()
    patch_orchestrator()
    print("\n🎯 All files patched for elite performance enhancement!")
