--- /data/data/com.termux/files/home/termux-multi-agent/workspace/agent_shell.py
+++ /data/data/com.termux/files/home/termux-multi-agent/workspace/agent_shell.py
@@ -9,7 +9,7 @@
 HOME = Path.home()
 MASTER = HOME / 'workspace/llm_map/master_tasks.json'
 ORCHESTRATOR = HOME / 'termux-multi-agent/run.py'
-SIMPLE_AGENT = HOME / 'workspace/llm_map/simple_agent.py'
+TASK_ID_ENV_VAR = 'TASK_ID'
 
 def list_tasks():
     tasks = json.loads(MASTER.read_text())
@@ -18,7 +18,7 @@
         print(f"{icon} {t['id']}: {t['status']} [{t['assigned_agent']}] {t['title']}")
 
 def run_task(task_id):
-    """Execute a task via the orchestrator if it has a target file, else via simple_agent."""
+    """Execute a task via run.py with TASK_ID env var for all tasks."""
     tasks = json.loads(MASTER.read_text())
     task = next((t for t in tasks if t['id'] == task_id), None)
     if not task:
@@ -28,38 +28,36 @@
         print(f"Task {task_id} is already {task['status']}.")
         return
 
-    # For tasks that modify code, use the orchestrator pipeline.
-    # The orchestrator expects a workspace with a target file and a refactor goal.
-    if task.get('component') in ('Verdicts', 'Promotion', 'Scanner', 'TUI', 'Automation', 'Cleanup'):
-        sandbox = Path(task.get('sandbox', '~/sandbox/default')).expanduser()
-        sandbox.mkdir(parents=True, exist_ok=True)
-        target_file = sandbox / 'target.py'
-        if not target_file.exists():
-            target_file.write_text(f"# Task {task_id} placeholder\n")
-        # Write the refactor goal to current_task.txt (read by run.py)
-        (sandbox / 'current_task.txt').write_text(task['title'] + '\n' + task.get('instructions', ''))
-        # Call the orchestrator with the sandbox as workspace
-        env = os.environ.copy()
-        env['AGENT_NAME'] = task['assigned_agent']
-        result = subprocess.run(
-            ['python3', str(ORCHESTRATOR)],
-            cwd=str(sandbox), capture_output=True, text=True, timeout=120, env=env
-        )
-        print(result.stdout[-500:] if result.stdout else result.stderr[:500])
-        # Update task status based on output
-        if 'PASS' in (result.stdout + result.stderr).upper():
-            task['status'] = 'done'
-        else:
-            task['status'] = 'failed'
-        task['result'] = (result.stdout + result.stderr)[:200]
+    # Always use run.py for all tasks with TASK_ID environment variable
+    sandbox = Path(task.get('sandbox', '~/sandbox/default')).expanduser()
+    sandbox.mkdir(parents=True, exist_ok=True)
+    
+    # Ensure target file exists
+    target_file = sandbox / 'target.py'
+    if not target_file.exists():
+        target_file.write_text(f"# Task {task_id} placeholder\n")
+    
+    # Write instructions to current_task.txt for run.py
+    instructions = task['title'] + '\n' + task.get('instructions', '')
+    (sandbox / 'current_task.txt').write_text(instructions)
+    
+    # Set up environment with TASK_ID for run.py
+    env = os.environ.copy()
+    env['AGENT_NAME'] = task['assigned_agent']
+    env[TASK_ID_ENV_VAR] = task_id
+    
+    # Execute run.py with sandbox as working directory
+    result = subprocess.run(
+        ['python3', str(ORCHESTRATOR)],
+        cwd=str(sandbox), capture_output=True, text=True, timeout=120, env=env
+    )
+    
+    print(result.stdout[-500:] if result.stdout else result.stderr[:500])
+    
+    # Update task status based on run.py output
+    if 'PASS' in (result.stdout + result.stderr).upper():
+        task['status'] = 'done'
     else:
-        # For research/docs tasks, use simple_agent
-        subprocess.run(['python3', str(SIMPLE_AGENT), task_id])
-
+        task['status'] = 'failed'
+    task['result'] = (result.stdout + result.stderr)[:200]
+    
     json.dump(tasks, open(MASTER, 'w'), indent=2)
 
 def run_command(cmd):
