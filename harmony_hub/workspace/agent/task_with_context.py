#!/usr/bin/env python3
"""Run multi-agent with investigator patches as context, working on a sandbox copy."""
import sys, os, subprocess, json, shutil
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: task_with_context.py <context_dir> <target_file> [goal]")
    sys.exit(1)

context_dir = Path(sys.argv[1])
target = Path(sys.argv[2])
goal = sys.argv[3] if len(sys.argv) > 3 else "Refactor the target using the context patches as examples."

# 1. Build context from investigator patches
context_parts = []
for cf in sorted(context_dir.glob("*.py"))[:8]:  # limit to 8 for prompt size
    content = cf.read_text()[:800]
    context_parts.append(f"// Patch: {cf.name}\n{content}\n")
context_text = "\n".join(context_parts)

# 2. Create sandbox workspace for this task
workspace = Path.home() / "termux-multi-agent" / "workspace"
workspace.mkdir(parents=True, exist_ok=True)

# 3. Copy target into sandbox
sandbox_target = workspace / "refactor_target.py"
shutil.copy2(target, sandbox_target)

# 4. Write the full task prompt that the agent will read
task_prompt = f"""GOAL: {goal}

CONTEXT (successful prior patches for similar files):
{context_text}

TARGET FILE: {sandbox_target}
Original source: {target}
Do NOT modify the original. Work on the sandbox copy at {sandbox_target}.
After your changes, run validation: python -m py_compile {sandbox_target}
Only if validation passes, suggest the file is ready for review."""

task_file = workspace / "current_task.txt"
task_file.write_text(task_prompt)
print(f"Task prepared: {task_file}")
print(f"Sandbox target: {sandbox_target}")
print(f"Context from {len(context_parts)} investigator patches")

# 5. Run the agent (which reads test_script.py by default; we'll hack it)
# Copy the target over the default test file so the agent works on it
default_target = workspace / "test_script.py"
default_target.write_text(sandbox_target.read_text())

agent_script = Path.home() / "harmony_hub" / "workspace" / "agent" / "run_with_elo.py"
result = subprocess.run([sys.executable, agent_script], cwd=Path.home() / "termux-multi-agent")

# 6. Copy agent output back to sandbox
if default_target.exists():
    shutil.copy2(default_target, sandbox_target)

# 7. Validate
validation = subprocess.run(["python", "-m", "py_compile", sandbox_target], capture_output=True, text=True)
if validation.returncode == 0:
    print(f"✅ Validation passed for {sandbox_target}")
    print(f"Review the sandbox file, then promote to {target} with:")
    print(f"  cp {sandbox_target} {target}")
else:
    print(f"❌ Validation failed:\n{validation.stderr}")

sys.exit(result.returncode)
