#!/usr/bin/env python3
import sys, os, shutil, subprocess
from pathlib import Path

sys.path.insert(0, str(Path.home() / "termux-multi-agent" / "src"))
sys.path.insert(0, str(Path.home() / "termux-multi-agent"))
from orchestrator import TermuxAgentOrchestrator

account = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ('primary','secondary') else 'primary'
if account in ('primary','secondary'):
    goal = sys.argv[2] if len(sys.argv) > 2 else "Refactor the target file."
    target_original = Path(sys.argv[3]) if len(sys.argv) > 3 else Path.home() / "deepcli-tui" / "tui.py"
else:
    goal = sys.argv[1] if len(sys.argv) > 1 else "Refactor the target file."
    target_original = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "deepcli-tui" / "tui.py"
    account = 'primary'

# Check for --promote flag (never auto-promote without it)
auto_promote = '--promote' in sys.argv
if auto_promote:
    sys.argv.remove('--promote')

sandbox = Path.home() / "termux-multi-agent" / "workspace" / f"refactor_target{target_original.suffix}"

# Backup original
backup_path = target_original.with_suffix(target_original.suffix + '.bak')
if not backup_path.exists():
    backup_path.write_text(target_original.read_text())
# Start with a pristine copy of the original
    sandbox.write_text(target_original.read_text())
print(f"Target: {target_original} -> {sandbox}")

# Detect language
language = "python"
js_exts = (".js", ".mjs", ".cjs")
ts_exts = (".ts", ".tsx", ".mts")
sh_exts = (".sh", ".bash", ".zsh", ".fish")
rs_exts = (".rs",)
html_exts = (".html", ".htm", ".xhtml")
css_exts = (".css", ".scss", ".less")
if target_original.suffix in js_exts:
    language = "javascript"
elif target_original.suffix in ts_exts:
    language = "typescript"
elif target_original.suffix in sh_exts:
    language = "bash"
elif target_original.suffix in rs_exts:
    language = "rust"
elif target_original.suffix in html_exts:
    language = "html"
elif target_original.suffix in css_exts:
    language = "css"

orchestrator = TermuxAgentOrchestrator(
    workspace_root=str(Path.home() / "termux-multi-agent" / "workspace"),
    account=account
)
try:
    orchestrator.run_refactor_pipeline(
        target_file=str(sandbox),
        request_instruction=goal,
        test_command=f"node --check {sandbox}" if language == "javascript" else f"python -m py_compile {sandbox}",
        language=language
    )
except Exception as e:
    print(f"❌ Agent failed: {e}. Restoring original.")
    sandbox.write_text(backup_path.read_text())
    raise

# Validate
lang_cmds = {
    "python": ["python", "-m", "py_compile", str(sandbox)],
    "javascript": ["node", "--check", str(sandbox)],
    "typescript": ["npx", "tsc", "--noEmit", str(sandbox)],
    "bash": ["bash", "-n", str(sandbox)],
    "rust": ["rustc", "--edition", "2021", "-Z", "no-codegen", str(sandbox)],
}
cmd = lang_cmds.get(language, ["python", "-m", "py_compile", str(sandbox)])
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Validation passed for {sandbox}")
    # Capture session_id from orchestrator log (last created session)
    session_id = None
    try:
        import re, io
        log_stream = io.StringIO()
        # The orchestrator logs to root logger; we can't easily capture here.
        # Instead, get the session_id from the orchestrator object directly.
        session_id = orchestrator.session_id
    except Exception:
        pass
    # Log to run_history AFTER validation, with session_id
    try:
        import sqlite3
        db = Path.home() / "termux-multi-agent" / "local_repo.db"
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO run_history (target_file, attempt_number, patch_content, verdict, account, validated, session_id) VALUES (?,1,?,'success',?,1,?)",
            (str(target_original), sandbox.read_text()[:1000], account, session_id)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
    # Log to run_history AFTER validation
    try:
        import sqlite3
        db = Path.home() / "termux-multi-agent" / "local_repo.db"
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO run_history (target_file, attempt_number, patch_content, verdict, account) VALUES (?,1,?,'success',?)",
            (str(target_original), sandbox.read_text()[:1000], account)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
    if auto_promote:
        backup_promote = target_original.with_suffix(target_original.suffix + '.pre_promote.bak')
        shutil.copy2(target_original, backup_promote)
        shutil.copy2(sandbox, target_original)
        print(f"✅ Promoted: {sandbox} -> {target_original}")
        print(f"   Backup saved: {backup_promote}")
    else:
        print(f"⚠️  Review sandbox first: {sandbox}")
        print(f"   To promote: python3 direct_task.py --promote ... <goal> <target>")
else:
    print(f"❌ Validation failed:\n{result.stderr}")
