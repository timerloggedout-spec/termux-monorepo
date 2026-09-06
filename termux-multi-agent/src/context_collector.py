import sqlite3
import os
import re
import subprocess
import shutil
from pathlib import Path

DB_PATH = "local_repo.db"

class AutomatedContextCollector:
    def _get_cached_signatures(self, file_path):
        """Return function signatures from func_index.jsonl if the file hasn't changed."""
        import hashlib, json
        func_index = Path.home() / 'workspace/llm_map/func_index.jsonl'
        if not func_index.exists():
            return None
        file_p = Path(file_path)
        if not file_p.exists():
            return None
        current_hash = hashlib.sha256(file_p.read_bytes()).hexdigest()[:16]
        cache_file = Path.home() / '.cache/sig_cache' / f'{file_p.name}.{current_hash}.json'
        if cache_file.exists():
            with open(cache_file) as cf:
                return json.load(cf)
        # Build and cache
        sigs = []
        try:
            rel_str = str(file_p.relative_to(Path.home()))
        except ValueError:
            rel_str = str(file_p)
        with open(func_index) as fi:
            for line in fi:
                entry = json.loads(line)
                if entry.get('file') == rel_str:
                    sigs.append(f"{entry['name']} line {entry['line']}: {entry.get('sig','')[:80]}")
        if sigs:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w') as cf:
                json.dump(sigs, cf)
            return sigs
        return None

    def __init__(self, workspace_root):
        self.workspace = os.path.abspath(workspace_root)

    def find_dependent_files(self, file_relative_path, conn=None):
        """
        Find files in the workspace dependent on or referenced by the target file.
        Accepts an optional open sqlite3.Connection to reuse existing connection handles and minimize disk I/O.
        Combines edge queries with UNION to halve query roundtrips.
        """
        base_name = os.path.splitext(file_relative_path)[0]
        related_files = set()
        close_conn = False
        if conn is None:
            conn = sqlite3.connect(DB_PATH)
            close_conn = True

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT target_file FROM edges WHERE source_file = ? OR target_file LIKE ?
                UNION
                SELECT source_file FROM edges WHERE target_file = ? OR source_file LIKE ?
                """,
                (file_relative_path, f"%{base_name}%", file_relative_path, f"%{base_name}%")
            )
            for row in cursor.fetchall():
                related_files.add(row[0])
        finally:
            if close_conn:
                conn.close()

        valid_dependencies = []
        extensions = ('.py', '.js', '.mjs', '.rs', '.sh')
        for ref in related_files:
            if ref == file_relative_path:
                continue
            if ref.endswith(extensions):
                if os.path.exists(os.path.join(self.workspace, ref)):
                    valid_dependencies.append(ref)
                continue
            for ext in extensions:
                check_path = f"{ref}{ext}"
                if check_path != file_relative_path and os.path.exists(os.path.join(self.workspace, check_path)):
                    valid_dependencies.append(check_path)
                    break
        return valid_dependencies

    def generate_ast_skeleton(self, file_relative_path):
        if not shutil.which("ast-grep"):
            return f"// Unable to trace AST module boundary map for {file_relative_path}"
        abs_path = os.path.join(self.workspace, file_relative_path)
        ext = os.path.splitext(file_relative_path)[1]
        if ext == '.py':
            pattern = "class $NAME: $$$"
        elif ext in ['.js', '.mjs']:
            pattern = "function $NAME($$ $) { $$$ }"
        else:
            return f"/* Structural stub context for file: {file_relative_path} */"
        try:
            output = subprocess.check_output(["ast-grep", "run", "--pattern", pattern, "--json", abs_path], cwd="/data/data/com.termux/files/home/termux-multi-agent", text=True)
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
        mode = os.environ.get("CONTEXT_MODE", "full")
        target_path = os.path.join(self.workspace, active_target_file)
        dependencies = self.find_dependent_files(active_target_file)
        bundle = ["=== CODEBASE ARCHITECTURE SUBSTRUCTURE CONTEXT ==="]
        for dep in dependencies:
            skeleton = self.generate_ast_skeleton(dep)
            bundle.append(f'\n<file path="{dep}" layout="dependent_skeleton">\n{skeleton}\n')

        if mode == "minimized":
            sigs = self._get_cached_signatures(target_path)
            target_code = "\n".join(sigs) if sigs else "# No signatures"
        elif mode == "compact":
            with open(target_path) as f:
                target_code = f.read()[:2048]
            sigs = self._get_cached_signatures(target_path)
            if sigs:
                target_code += "\n\n" + "\n".join(sigs)
        else:
            with open(target_path) as f:
                target_code = f.read()

        bundle.append(f'\n<file path="{active_target_file}" layout="active_target_edit_zone">\n{target_code}\n')
        return "\n".join(bundle)
