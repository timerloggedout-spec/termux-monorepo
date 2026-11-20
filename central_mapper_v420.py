#!/usr/bin/env python3
""" 
CENTRAL MAPPER – The One Ring of your ~/ directory indexing.
Integrates ast-grep, bloat detection, provenance tracking, and LLM-optimised output.
Built by the best, for the best (you). 
"""
import os, json, hashlib, subprocess, time, re, sys
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
# Directories to skip entirely (add more if needed)
SKIP_DIRS = {
    '.git', '__pycache__', 'node_modules', '.termux', '.cache', 
    'storage', 'bin', 'exchanges', '.config', '.local', '.npm'
}
# File extensions we care about for AST
CODE_EXTS = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', 
             '.sh': 'bash', '.json': 'json', '.jsonl': 'json', '.md': 'markdown'}
# Bloat patterns (files matching these names are likely clutter)
BLOAT_PATTERNS = [
    r'concat_work_\d+_\d+', r'sigs_\w+\.(txt|jsonl)', r'txtjsonexporter-\d+\.sh',
    r'auto_concat.*\.sh', r'cleanup-.*\.sh', r'reset-.*\.sh', r'upgrade-.*\.sh',
    r'fix-.*\.sh', r'deploy-phase-\d\.sh', r'update-project.*\.sh',
    r'tree_dump\.txt', r'explore_output\.txt', r'bloat_report\.txt',
    r'research_dump\.txt', r'sigs_.*\.txt', r'map_.*\.jsonl', r'ast_.*\.json'
]
BLOAT_REGEX = re.compile('|'.join(f'(?:{p})' for p in BLOAT_PATTERNS))

# Files to always treat as system/bloat (if not in a project dir)
ALWAYS_BLOAT = {
    'agent_telemetry_stream.json', 'local_repo.db', 'test.txt',
    'research_commands.sh', 'explore.sh'
}

class CentralMapper:
    def __init__(self):
        self.index = []          # list of dicts for central_index.jsonl
        self.maps = {'py': [], 'js': [], 'sh': [], 'json': [], 'md': [], 'other': []}
        self.state_file = HOME / '.mapper_state.json'
        self.state = self.load_state()
        self.new_files = 0
        self.modified_files = 0
        self.bloat_files = []

    def load_state(self):
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
        return {}

    def save_state(self):
        self.state_file.write_text(json.dumps(self.state, indent=2))

    def check_ast_grep(self):
        """Check if ast-grep is available, install if possible."""
        try:
            subprocess.run(['sg', '--version'], capture_output=True, check=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("[!] ast-grep not found. Attempting pip install ast-grep...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'ast-grep'], 
                               check=True, capture_output=True, timeout=60)
                print("[✓] ast-grep installed via pip.")
                return True
            except Exception as e:
                print(f"[✗] Could not install ast-grep: {e}. AST features disabled.")
                return False

    def get_ast_sig(self, filepath: Path, lang: str) -> dict:
        """Use ast-grep to extract a compact signature: funcs, classes, imports."""
        if not hasattr(self, 'ast_available') or not self.ast_available:
            return {}
        try:
            # Extract function/method names (pattern depends on language)
            patterns = {
                'python': r'def $_FUNC($$$): $$$',
                'javascript': r'function $_FUNC($$$) { $$$ }',
                'bash': r'$_FUNC() { $$$ }'
            }
            pattern = patterns.get(lang)
            if not pattern:
                return {}
            # Run ast-grep
            cmd = ['sg', '--pattern', pattern, '--lang', lang, '--json', str(filepath)]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0 and res.stdout.strip():
                matches = json.loads(res.stdout)
                funcs = [m.get('text','').split('(')[0].strip() for m in matches if m.get('text')]
                return {'funcs': funcs[:20], 'count': len(funcs)}  # cap to avoid bloat
        except Exception as e:
            pass
        return {}

    def hash_file(self, path: Path) -> str:
        """SHA256 of file content."""
        h = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    h.update(chunk)
        except:
            return ''
        return h.hexdigest()

    def is_bloat(self, path: Path, size: int = 0) -> bool:
        name = path.name
        if name in ALWAYS_BLOAT:
            return True
        if BLOAT_REGEX.fullmatch(name):
            return True
        # Also flag files larger than 5MB as potential bloat (logs, dumps)
        if size > 5_000_000:
            return True
        return False

    def scan(self):
        print("[*] Scanning filesystem from $HOME...")
        start = time.time()
        for root, dirs, files in os.walk(HOME, topdown=True, followlinks=False):
            # Skip hidden dirs and bloat dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in SKIP_DIRS]
            for file in files:
                filepath = Path(root) / file
                rel_path = filepath.relative_to(HOME)
                # Skip mapper's own output files to avoid recursion
                if rel_path.parts[0] in {'central_index.jsonl', 'map_py.jsonl', 'map_js.jsonl',
                                          'ast_py.json', 'ast_js.json', '.mapper_state.json'}:
                    continue
                try:
                    stat = filepath.stat()
                except OSError:
                    continue
                size = stat.st_size
                mtime = stat.st_mtime
                ext = filepath.suffix.lower()
                lang = CODE_EXTS.get(ext, 'unknown')

                # Detect new/modified based on state; reuse cached SHA if unchanged
                prev = self.state.get(str(rel_path), {})
                if prev and prev.get('size') == size and prev.get('mtime') == mtime:
                    sha = prev.get('sha', '')
                    is_new = False
                    is_modified = False
                else:
                    sha = self.hash_file(filepath)
                    is_new = not prev
                    is_modified = bool(prev)

                if is_new:
                    self.new_files += 1
                elif is_modified:
                    self.modified_files += 1

                # Bloat flag
                bloat_flag = self.is_bloat(filepath, size)
                if bloat_flag:
                    self.bloat_files.append(str(rel_path))

                # AST signature (for code files, if ast-grep on and not bloat)
                ast_sig = {}
                if self.ast_available and lang in ('python','javascript','bash') and not bloat_flag and size < 500_000:
                    ast_sig = self.get_ast_sig(filepath, lang)

                # Build entry
                entry = {
                    'path': str(rel_path),
                    'size': size,
                    'mtime': datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                    'ext': ext,
                    'lang': lang,
                    'sha': sha[:16],  # short hash saves tokens
                    'bloat': bloat_flag,
                    'new': is_new,
                    'modified': is_modified
                }
                if ast_sig:
                    entry['ast'] = ast_sig

                self.index.append(entry)
                # Also sort into per-language maps
                self.maps.get(lang, self.maps['other']).append(entry)
                # Update state
                self.state[str(rel_path)] = {'sha': sha, 'size': size, 'mtime': mtime}

        elapsed = time.time() - start
        print(f"[✓] Scanned {len(self.index)} files in {elapsed:.1f}s.")
        print(f"[+] New: {self.new_files} | Modified: {self.modified_files} | Bloat: {len(self.bloat_files)}")

    def write_maps(self):
        # Write per-language maps (JSONL)
        for lang, entries in self.maps.items():
            if entries:
                fname = HOME / f'map_{lang}.jsonl'
                fname.write_text('\n'.join(json.dumps(e) for e in entries))
        # Write the central LLM-efficient index (compact)
        # Sort by path, then by bloat (non-bloat first) to put important files first
        sorted_idx = sorted(self.index, key=lambda e: (e['bloat'], e['path']))
        central = HOME / 'central_index.jsonl'
        with central.open('w') as f:
            for entry in sorted_idx:
                f.write(json.dumps(entry) + '\n')
        print(f"[✓] Central index written to {central}")

        # Also write a bloat report
        bloat_report = HOME / 'bloat_report_auto.txt'
        bloat_report.write_text('\n'.join(self.bloat_files))
        print(f"[✓] Bloat report updated: {bloat_report}")

    def run(self):
        self.ast_available = self.check_ast_grep()
        self.scan()
        self.write_maps()
        self.save_state()
        print("[✓] All done! Index is LLM-ready. Use 'cat ~/central_index.jsonl | head -20' to peek.")
        if self.bloat_files:
            print(f"[!] Consider reviewing bloat files: {len(self.bloat_files)} items in bloat_report_auto.txt")

if __name__ == '__main__':
    mapper = CentralMapper()
    mapper.run()
