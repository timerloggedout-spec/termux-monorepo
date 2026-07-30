"""Route a patch request to the most appropriate tool."""
import sys, os, subprocess

def apply_patch(target: str, patch_content: str, method: str = "auto") -> bool:
    """Apply a patch to a file. method: 'auto', 'cedar', 'sed', 'python'."""
    if method == "auto":
        # Prefer CEDARscript for structured diffs, sed for simple substitutions, PYEOF for complex
        if "ADD_IMPORT" in patch_content or "MODIFY FUNCTION" in patch_content:
            method = "cedar"
        elif "\n" not in patch_content and "s/" in patch_content:
            method = "sed"
        else:
            method = "python"

    if method == "cedar":
        try:
            from cedarscript_editor import CEDARScriptASTParser, CEDARScriptEditor
            parser = CEDARScriptASTParser()
            commands, errors = parser.parse_script(patch_content)
            if errors:
                print(f"CEDARscript errors: {errors}", file=sys.stderr)
                return False
            editor = CEDARScriptEditor(root_path="/")
            editor.apply_commands(commands)
            return True
        except ImportError:
            print("CEDARscript not installed, falling back to python", file=sys.stderr)
            method = "python"
        except Exception as e:
            print(f"CEDARscript failed: {e}", file=sys.stderr)
            return False

    if method == "sed":
        # Minimal sed wrapper for simple substitutions
        result = subprocess.run(["sed", "-i", patch_content, target], capture_output=True, text=True)
        return result.returncode == 0

    if method == "python":
        # Write a temporary script and execute
        script = f"""
import sys
target = sys.argv[1]
with open(target) as f:
    content = f.read()
# Apply patch (the patch_content is Python code that modifies 'content')
{patch_content}
with open(target, 'w') as f:
    f.write(content)
"""
        tmp = os.path.join(os.path.dirname(target), "_patch_tmp.py")
        with open(tmp, 'w') as f:
            f.write(script)
        result = subprocess.run([sys.executable, tmp, target], capture_output=True, text=True)
        os.unlink(tmp)
        return result.returncode == 0
