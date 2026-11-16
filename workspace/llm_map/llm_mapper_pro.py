#!/usr/bin/env python3
"""
Caveman LLM Ecosystem Mapper vPRO – profiles, dependency graph, AST snippets,
time‑correlated file tracking, and blazingly LLM‑efficient indexes.

Usage:
  python llm_mapper_pro.py update                    # incremental scan of home dir
  python llm_mapper_pro.py update --profile deepseek  # use profile deepseek
  python llm_mapper_pro.py full-scan                  # ignore cache, re‑scan everything
  python llm_mapper_pro.py generate-map               # rebuild SYSTEM_MAP.md, CAVEMAN_INDEX.md
  python llm_mapper_pro.py graph-tree deepcli/core.py  # show dependency tree
  python llm_mapper_pro.py graph-dot > graph.dot      # export Graphviz DOT
"""

import os, sys, json, hashlib, re, time, argparse, fnmatch
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path

HOME = Path.home()
MAP_DIR = HOME / "workspace/llm_map"
INDEX_FILE = MAP_DIR / "llm_index_compact.jsonl"
DEPS_FILE = MAP_DIR / "deps.jsonl"
AST_FILE = MAP_DIR / "ast_snippets.json"
CONFIG_DIR = HOME / ".config/llm_map"
PROFILES_DIR = CONFIG_DIR / "profiles"
DEFAULT_PROFILE = PROFILES_DIR / "default.json"

# ── Bloat patterns (files to ignore) ──────────────────────────────────────
BLOAT_GLOBS = [
    "*/node_modules/*", "*/.git/*", "*/__pycache__/*", "*.pyc",
    "storage/*", "*.apk", "*.mp4", "*.mp3", "*.jpg", "*.png",
    "*.gif", "*.ico", "*.ttf", "*.woff*", "*.eot", "*.db",
    "*.log", ".bash_history", ".python_history", ".lesshst",
    ".deepcli_tui_history", "*.bak", "*~", "*.swp",
]

# ── Language detectors ────────────────────────────────────────────────────
LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".sh": "bash", ".md": "markdown", ".json": "json",
    ".jsonl": "jsonl", ".txt": "text", ".yml": "yaml",
    ".yaml": "yaml", ".cfg": "ini", ".ini": "ini",
    ".jsx": "javascript", ".tsx": "typescript",
}

def detect_lang(path: Path) -> str:
    return LANG_MAP.get(path.suffix.lower(), "unknown")

# ── AST snippet (first def/function/class) ────────────────────────────────
def extract_ast_snippet(path: Path) -> str:
    try:
        content = path.read_text(errors="ignore")[:4096]
        if path.suffix == ".py":
            for line in content.splitlines():
                if re.match(r'\s*(def |class )', line):
                    return line.strip()[:80]
        elif path.suffix in (".js", ".jsx", ".ts", ".tsx"):
            for line in content.splitlines():
                if re.match(r'\s*(function |const \w+ = \(.*\) =>|export (default )?function )', line):
                    return line.strip()[:80]
        return ""
    except Exception:
        return ""

def file_hash(path: Path) -> str:
    """Short content hash for deduplication"""
    try:
        return hashlib.md5(path.read_bytes()[:4096]).hexdigest()[:8]
    except Exception:
        return ""

def is_bloat(path: Path) -> bool:
    rel = str(path.relative_to(HOME))
    for pattern in BLOAT_GLOBS:
        if fnmatch.fnmatch(rel, pattern):
            return True
    return False

# ── Profile management ────────────────────────────────────────────────────
def load_profile(name: str = "default") -> dict:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    profile_file = PROFILES_DIR / f"{name}.json"
    if profile_file.exists():
        return json.loads(profile_file.read_text())
    # Default: include everything, no explicit excludes (bloat still filtered)
    return {"include": ["."], "exclude": []}

def should_include(path: Path, profile: dict) -> bool:
    rel = str(path.relative_to(HOME))
    # explicit excludes
    for ex in profile.get("exclude", []):
        if rel.startswith(ex.rstrip("/")):
            return False
    # explicit includes (if none given, include everything)
    incs = profile.get("include", ["."])
    for inc in incs:
        if rel.startswith(inc.rstrip("/")):
            return True
    return False

# ── Dependency extraction (import / require) ──────────────────────────────
def extract_deps(path: Path, root: Path = HOME) -> list:
    deps = []
    try:
        content = path.read_text(errors="ignore")
        if path.suffix == ".py":
            for m in re.finditer(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE):
                deps.append(m.group(1))
        elif path.suffix in (".js", ".jsx", ".ts", ".tsx"):
            for m in re.finditer(r'(?:require\(|import\s+.*?from\s+)[\'"]([^\'"]+)[\'"]', content):
                deps.append(m.group(1))
    except Exception:
        pass
    return deps

def resolve_dep_to_path(dep: str, lang: str) -> str:
    """Very rough resolver: only works for relative/sibling imports."""
    # For simplicity, store the raw import string; path resolution is project-specific.
    return dep

# ── Scan engine ───────────────────────────────────────────────────────────
def scan_files(profile: dict, full_scan: bool = False):
    """Walk HOME, yield file entries (dict) respecting profile and bloat."""
    # Load existing index for incremental update
    existing = {}
    if not full_scan and INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            for line in f:
                item = json.loads(line)
                existing[item['p']] = item

    # Collect current mtimes in index (for incremental)
    # We'll walk the filesystem and if a path is unchanged, reuse old entry.
    # This speeds up subsequent runs immensely.

    # Yield new/updated entries, and remember unchanged ones.
    unchanged_entries = {}
    for dirpath, dirnames, filenames in os.walk(HOME):
        # Exclude bloat dirs early
        rel = Path(dirpath).relative_to(HOME)
        if any(fnmatch.fnmatch(str(rel) + "/", pat) for pat in BLOAT_GLOBS if pat.endswith('/*')):
            dirnames[:] = []  # don't descend
            continue
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if not should_include(fpath, profile):
                continue
            if is_bloat(fpath):
                continue
            rel_path = str(fpath.relative_to(HOME))
            try:
                stat = fpath.stat()
                mtime = int(stat.st_mtime)
                size = stat.st_size
            except OSError:
                continue

            # Check if unchanged
            if rel_path in existing:
                old = existing[rel_path]
                if old.get('mtime') == mtime and old.get('size') == size:
                    unchanged_entries[rel_path] = old
                    continue

            # New or changed — build entry
            lang = detect_lang(fpath)
            snippet = extract_ast_snippet(fpath) if lang in ("python","javascript","typescript") else ""
            hash_val = file_hash(fpath)
            # Project heuristics: top-level dir name
            project = rel_path.split("/")[0] if "/" in rel_path else "root"
            entry = {
                "p": rel_path,
                "pj": project,
                "l": lang,
                "b": is_bloat(fpath),
                "ts": datetime.fromtimestamp(fpath.stat().st_mtime, tz=timezone.utc).isoformat() if fpath.exists() else "",  # (should already be filtered, but keep)
                "s": size,
                "t": mtime,       # timestamp for time correlation
                "h": hash_val,    # content hash
                "as": snippet if snippet else "",
                "by": 0,          # will be filled after dep scan
            }
            yield entry

    # After the walk, yield unchanged entries (for completeness)
    for p, old in unchanged_entries.items():
        # Ensure it's still valid according to profile/bloat (rarely changes)
        # For performance, we assume unchanged files remain valid.
        yield old

# ── Dependency graph builder ──────────────────────────────────────────────
def build_graph(entries: list):
    """Populate deps.jsonl and update 'by' counts."""
    # map path -> entry
    index = {e['p']: e for e in entries}
    dep_edges = []
    # Reset by counters
    for e in entries:
        e['by'] = 0
    for entry in entries:
        if entry['l'] not in ("python","javascript","typescript"):
            continue
        fpath = HOME / entry['p']
        deps = extract_deps(fpath)
        for dep in deps:
            # simple heuristic: try to match to a file path (very rough)
            # store raw dependency; actual resolution could be a later step.
            dep_edge = {"from": entry['p'], "to": dep, "type": "import"}
            dep_edges.append(dep_edge)
            # increment used_by if we can find a file that matches
            # For now we just save edges; 'by' count we compute offline from deps.
    # Write deps file
    with open(DEPS_FILE, 'w') as df:
        for edge in dep_edges:
            df.write(json.dumps(edge) + "\n")
    # Recalculate 'by' from edges: count how many times a file is a target
    # This gives a rough "used_by" count even without full resolution.
    by_counts = defaultdict(int)
    for edge in dep_edges:
        # edge['to'] is an import string, not a file path. Not perfect but okay.
        # We'll use it as is.
        by_counts[edge['to']] += 1
    for e in entries:
        # for a path, if it appears in by_counts, set 'by'
        # crude: match if the import string is a substring of the path
        for imp, cnt in by_counts.items():
            if imp in e['p']:  # e.g., 'deepcli.core' matches 'deepcli/core.py'
                e['by'] += cnt

# ── Main command handlers ─────────────────────────────────────────────────
def cmd_update(args):
    profile = load_profile(args.profile)
    entries = list(scan_files(profile, full_scan=False))
    build_graph(entries)
    # Write index
    with open(INDEX_FILE, 'w') as out:
        for e in entries:
            out.write(json.dumps(e) + "\n")
    # Write AST snippets map
    ast_map = {}
    for e in entries:
        if e['as']:
            ast_map[e['h']] = e['as']
    with open(AST_FILE, 'w') as af:
        json.dump(ast_map, af, indent=2)
    print(f"✅ Index updated: {len(entries)} files, deps -> {DEPS_FILE}")

def cmd_full_scan(args):
    profile = load_profile(args.profile)
    entries = list(scan_files(profile, full_scan=True))
    build_graph(entries)
    # (re)write index
    with open(INDEX_FILE, 'w') as out:
        for e in entries:
            out.write(json.dumps(e) + "\n")
    print(f"✅ Full scan: {len(entries)} files indexed.")

def cmd_generate_map(args):
    if not INDEX_FILE.exists():
        print("❌ No index found. Run 'update' first.")
        return
    entries = []
    with open(INDEX_FILE) as f:
        for line in f:
            entries.append(json.loads(line))
    # Generate SYSTEM_MAP.md
    proj = defaultdict(list)
    for e in entries:
        if not e['b']:
            proj[e['pj']].append(e)
    with open(MAP_DIR / "SYSTEM_MAP.md", 'w') as sm:
        sm.write("# SYSTEM MAP — Full Project Catalogue\n\n")
        for pj, files in sorted(proj.items(), key=lambda x: -len(x[1])):
            sm.write(f"## {pj} ({len(files)} files)\n\n")
            for f in sorted(files, key=lambda x: -x['by'])[:10]:
                sm.write(f"- `{f['p']}` (used by {f['by']})")
                if f.get('as'): sm.write(f" — {f['as'][:80]}")
                sm.write('\n')
            sm.write('\n')
    # Generate CAVEMAN_INDEX.md
    top = sorted([e for e in entries if not e['b']], key=lambda x: -x['by'])[:300]
    with open(MAP_DIR / "CAVEMAN_INDEX.md", 'w') as ci:
        ci.write("# 🪨 Caveman Index — Most Important Files\n\n")
        ci.write(f"Total indexed: {len(entries)} | non‑bloat: {sum(1 for e in entries if not e['b'])}\n\n")
        for e in top:
            ci.write(f"- `{e['p']}` (by:{e['by']}) {e['as'][:60] if e['as'] else ''}\n")
    print("✅ SYSTEM_MAP.md and CAVEMAN_INDEX.md regenerated.")

def cmd_graph_tree(args):
    target = args.file
    if not target:
        print("Provide a file path (relative to HOME).")
        return
    # Load deps
    if not DEPS_FILE.exists():
        print("No dependency data. Run 'update' first.")
        return
    edges = []
    with open(DEPS_FILE) as f:
        for line in f:
            edges.append(json.loads(line))
    # Build adjacency: from -> list of to
    graph = defaultdict(list)
    for e in edges:
        graph[e['from']].append(e['to'])
    # Print ASCII tree (simple indented recursion, depth limit 4)
    visited = set()
    def print_tree(file, prefix="", depth=0):
        if depth > 4: return
        print(f"{prefix}{'└── ' if prefix else ''}{file}")
        visited.add(file)
        deps = graph.get(file, [])
        for dep in deps[:5]:  # limit branches
            if dep not in visited:
                print_tree(dep, prefix + "    ", depth+1)
    print_tree(target)

def cmd_graph_dot(args):
    if not DEPS_FILE.exists():
        print("No dependency data.")
        return
    print("digraph G {")
    with open(DEPS_FILE) as f:
        for line in f:
            e = json.loads(line)
            print(f'  "{e["from"]}" -> "{e["to"]}";')
    print("}")

def cmd_profile_create(args):
    name = args.name
    inc = args.include.split(',') if args.include else ["."]
    exc = args.exclude.split(',') if args.exclude else []
    profile = {"include": inc, "exclude": exc}
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROFILES_DIR / f"{name}.json", 'w') as pf:
        json.dump(profile, pf, indent=2)
    print(f"✅ Profile '{name}' created with include={inc}, exclude={exc}")

# ── CLI parser ────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="llm_mapper_PRO")
    sub = parser.add_subparsers(dest="command")
    up = sub.add_parser("update", help="Incremental index update")
    up.add_argument("--profile", default="default", help="Profile name")
    full = sub.add_parser("full-scan", help="Full re-scan")
    full.add_argument("--profile", default="default")
    gen = sub.add_parser("generate-map", help="Generate SYSTEM_MAP.md etc.")
    tree = sub.add_parser("graph-tree", help="Show dependency tree for a file")
    tree.add_argument("file")
    dot = sub.add_parser("graph-dot", help="Export DOT graph")
    pc = sub.add_parser("profile-create", help="Create a new inclusion profile")
    pc.add_argument("name")
    pc.add_argument("--include", help="Comma-separated dirs to include")
    pc.add_argument("--exclude", help="Comma-separated dirs to exclude")
    args = parser.parse_args()
    if args.command == "update":
        cmd_update(args)
    elif args.command == "full-scan":
        cmd_full_scan(args)
    elif args.command == "generate-map":
        cmd_generate_map(args)
    elif args.command == "graph-tree":
        cmd_graph_tree(args)
    elif args.command == "graph-dot":
        cmd_graph_dot(args)
    elif args.command == "profile-create":
        cmd_profile_create(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
