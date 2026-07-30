"""Execute CEDARscript commands using cedarscript_editor."""
import subprocess
import sys
from pathlib import Path

try:
    from cedarscript_editor import CEDARScriptEditor, CEDARScriptASTParser
    HAS_CEDAR_EDITOR = True
except ImportError:
    HAS_CEDAR_EDITOR = False

class Executor:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).expanduser().resolve()
        if HAS_CEDAR_EDITOR:
            self.editor = CEDARScriptEditor(root_path=str(self.root_path))
            self.parser = CEDARScriptASTParser()
        else:
            self.editor = None

    def run(self, command: str, dry_run: bool = False) -> dict:
        """Run a single CEDARscript command (may be pointer or full)."""
        if not HAS_CEDAR_EDITOR:
            return {"error": "cedarscript_editor not installed", "command": command}
        # If command is a pointer, expand it first (caller should expand)
        # We'll assume it's full command here
        commands, errors = self.parser.parse_script(command)
        if errors:
            return {"error": errors, "command": command}
        if dry_run:
            return {"dry_run": True, "commands": [str(c) for c in commands], "command": command}
        self.editor.apply_commands(commands)
        return {"success": True, "command": command}
