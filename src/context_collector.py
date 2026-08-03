import sqlite3
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
                snippet = n.get('text', '').split('\n')[0]
                skeleton_lines.append(f"    {snippet} ...")
            return "\n".join(skeleton_lines)
        except Exception:
            return f"// Unable to trace AST module boundary map for {file_relative_path}"

    def assemble_minimized_bundle(self, active_target_file):
        dependencies = self.find_dependent_files(active_target_file)
        bundle = ["=== CODEBASE ARCHITECTURE SUBSTRUCTURE CONTEXT ==="]
        for dep in dependencies:
            skeleton = self.generate_ast_skeleton(dep)
            bundle.append(f'\n<file path="{dep}" layout="dependent_skeleton">\n{skeleton}\n')
        with open(os.path.join(self.workspace, active_target_file), 'r') as f:
            full_source = f.read()
        bundle.append(f'\n<file path="{active_target_file}" layout="active_target_edit_zone">\n{full_source}\n')
        return "\n".join(bundle)
