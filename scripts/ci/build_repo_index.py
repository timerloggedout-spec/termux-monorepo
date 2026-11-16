#!/usr/bin/env python3
"""build_repo_index.py — repo-side adaptive variant of
workspace/llm_map/build_final_all_profile.py.

Original: merges device-home stores (step5_bloat.jsonl, file_graph.json,
cli-synthegration provenance, func_index.jsonl, ~/.config profiles) into
llm_index_compact.jsonl + CAVEMAN_INDEX.md. Universe-bound: every input
lives under $HOME on one device; step5_bloat.jsonl is opened unguarded
(crash if absent). This variant derives the same compact schema from the
repo universe only:

  p   path (repo-relative)                <- git index
  s   size bytes                           <- git blob size
  l   language                             <- extension map
  h   blob sha prefix                      <- git index
  b   bloat flag                           <- workspace/llm_map/bloat_exclusions.lst
  ts  last-commit ISO time for the path    <- one `git log --name-only` pass
  as  signature summary (<=3)              <- func_index.jsonl if present
  ah  signature hashes (<=3)               <- func_index.jsonl if present
  fr  fragment-provenance count            <- 0 (owned by context_relationships)
  vr  version-provenance count             <- 0 (owned by context_relationships)
  d   outbound deps (<=5)                  <- ast imports (py) / import-regex (js,ts)
  by  inbound dependent count              <- reverse of d
  pj  project tag                          <- workspace/llm_map/project_mapping.json
                                              if present, else first path segment

fr/vr are deliberately NOT re-derived here: provenance counting is the
context_relationships system's job (archwiz/context_relationships/); this
index keeps the fields for schema compatibility with the original compact
format. Stdlib only; read-only w.r.t. the tree except the two outputs.
"""
import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

LANG = {".py": "python", ".js": "javascript", ".ts": "typescript",
        ".tsx": "typescript", ".jsx": "javascript", ".sh": "shell",
        ".md": "markdown", ".json": "json", ".yml": "yaml", ".yaml": "yaml",
        ".html": "html", ".css": "css", ".rs": "rust", ".go": "go",
        ".java": "java", ".kt": "kotlin", ".rb": "ruby", ".php": "php"}
SKIP_PREFIXES = (".git/",)
MAX_PARSE_BYTES = 500_000
JS_IMPORT = re.compile(r"(?:from\s+|require\(\s*)['\"](\.[^'\"]+)['\"]")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, check=True).stdout


def load_index(root):
    entries = []
    out = git(root, "ls-files", "-s", "-z")
    for rec in out.split("\0"):
        if not rec.strip():
            continue
        meta, path = rec.split("\t", 1)
        parts = meta.split()
        mode, sha = parts[0], parts[1]
        if mode == "160000":  # gitlink
            continue
        entries.append({"path": path, "sha": sha, "mode": mode})
    sizes = {}
    out = git(root, "ls-files", "-s", "-z")  # sizes via cat-file batch
    proc = subprocess.run(
        ["git", "-C", str(root), "cat-file", "--batch-check=%(objectname) %(objectsize)"],
        input="\n".join(e["sha"] for e in entries),
        capture_output=True, text=True)
    for line in proc.stdout.splitlines():
        p = line.split()
        if len(p) == 2:
            sizes[p[0]] = int(p[1])
    for e in entries:
        e["size"] = sizes.get(e["sha"], 0)
    return entries


def last_touched(root):
    ts = {}
    out = git(root, "log", "--format=commit:%cI", "--name-only", "--", ".")
    current = ""
    for line in out.splitlines():
        if line.startswith("commit:"):
            current = line[len("commit:"):]
        elif line.strip() and line not in ts:
            ts[line] = current
    return ts


def bloat_set(root):
    f = root / "workspace/llm_map/bloat_exclusions.lst"
    if not f.exists():
        return set()
    return {ln.strip() for ln in f.read_text().splitlines()
            if ln.strip() and not ln.startswith("#")}


def project_map(root):
    f = root / "workspace/llm_map/project_mapping.json"
    if f.exists():
        try:
            return json.loads(f.read_text())
        except ValueError:
            return {}
    return {}


def load_profile(root):
    name = os.environ.get("LLM_PROFILE", "default")
    pf = root / "ops/llm_map/profiles" / f"{name}.json"
    if pf.exists():
        try:
            return json.loads(pf.read_text())
        except ValueError:
            pass
    return {"include": ["."], "exclude": []}


def apply_profile(entries, profile):
    inc = profile.get("include", ["."])
    exc = profile.get("exclude", [])
    out = []
    for e in entries:
        p = e["path"]
        if any(p.startswith(x.rstrip("/")) for x in exc):
            continue
        if inc == ["."] or any(p.startswith(i.rstrip("/")) for i in inc):
            out.append(e)
    return out


def func_summaries(root):
    """Consume workspace/llm_map/func_index.jsonl (the func_index variant's
    output) exactly like the original consumed it; absent = empty."""
    f = root / "workspace/llm_map/func_index.jsonl"
    snippets, per_file = {}, defaultdict(list)
    if not f.exists():
        return snippets, per_file
    for line in f.read_text(errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        rel, sig = e.get("file", ""), e.get("sig", "")
        if not rel or not sig:
            continue
        text = f"{e.get('kind', 'de')} {e.get('name', '')}"
        text += sig.split("(", 1)[1] if "(" in sig else ""
        text = text.strip()
        if not text:
            continue
        h = hashlib.sha256(text.encode()).hexdigest()[:8]
        snippets[h] = text
        per_file[rel].append(h)
    return snippets, per_file


def py_deps(root, path, text, pathset, by_stem):
    deps = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return deps
    pkg = Path(path).parent
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                base = pkg
                for _ in range(node.level - 1):
                    base = base.parent
                if node.module:
                    cand = str(base / (node.module.replace(".", "/") + ".py"))
                    if cand in pathset:
                        deps.add(cand)
                    cand2 = str(base / node.module.replace(".", "/") / "__init__.py")
                    if cand2 in pathset:
                        deps.add(cand2)
                else:
                    for a in node.names:
                        cand = str(base / (a.name + ".py"))
                        if cand in pathset:
                            deps.add(cand)
            elif node.module:
                top = node.module.split(".")[0]
                for cand in by_stem.get(top, []):
                    deps.add(cand)
        elif isinstance(node, ast.Import):
            for a in node.names:
                top = a.name.split(".")[0]
                for cand in by_stem.get(top, []):
                    deps.add(cand)
    deps.discard(path)
    return deps


def js_deps(root, path, text, pathset):
    deps = set()
    pkg = Path(path).parent
    for m in JS_IMPORT.finditer(text):
        rel = m.group(1)
        for cand in (str(pkg / (rel + ".js")), str(pkg / (rel + ".ts")),
                     str(pkg / rel), str(pkg / rel / "index.js")):
            norm = os.path.normpath(cand)
            if norm in pathset:
                deps.add(norm)
    deps.discard(path)
    return deps


def build(root):
    entries = [e for e in load_index(root)
               if not e["path"].startswith(SKIP_PREFIXES)]
    entries = apply_profile(entries, load_profile(root))
    pathset = {e["path"] for e in entries}
    ts_map = last_touched(root)
    bloat = bloat_set(root)
    pmap = project_map(root)
    snippets, per_file = func_summaries(root)

    by_stem = defaultdict(list)
    for e in entries:
        if e["path"].endswith(".py"):
            stem = Path(e["path"]).stem
            if stem != "__init__":
                by_stem[stem].append(e["path"])

    graph = {}
    for e in entries:
        p = e["path"]
        ext = Path(p).suffix
        if ext not in (".py", ".js", ".ts", ".tsx", ".jsx"):
            continue
        fp = root / p
        try:
            if e["size"] > MAX_PARSE_BYTES:
                continue
            text = fp.read_text(errors="replace")
        except OSError:
            continue
        if ext == ".py":
            graph[p] = sorted(py_deps(root, p, text, pathset, by_stem))
        else:
            graph[p] = sorted(js_deps(root, p, text, pathset))

    dep_map = defaultdict(set)
    for src, ds in graph.items():
        for d in ds:
            dep_map[d].add(src)

    final = []
    for e in entries:
        p = e["path"]
        hashes = per_file.get(p, [])[:3]
        summary = "; ".join(snippets[h].split("\n")[0][:40] for h in hashes)
        final.append({
            "p": p, "s": e["size"],
            "l": LANG.get(Path(p).suffix, "?"),
            "h": e["sha"][:8],
            "b": any(p.startswith(b.rstrip("/")) or p == b for b in bloat),
            "ts": ts_map.get(p, ""),
            "as": summary, "ah": hashes,
            "fr": 0, "vr": 0,
            "d": graph.get(p, [])[:5],
            "by": len(dep_map.get(p, set())),
            "pj": pmap.get(p, p.split("/")[0]),
        })
    final.sort(key=lambda x: (x["b"], -x["by"], x["p"]))
    return final, graph, snippets


def write_outputs(root, final, graph, snippets):
    out_dir = root / "workspace/llm_map"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "llm_index_compact.jsonl", "w") as f:
        for rec in final:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    proj = defaultdict(list)
    for e in final:
        if not e["b"]:
            proj[e["pj"]].append(e)
    md = ("# Caveman Ecosystem – LLM Index v6.0 (repo-derived)\n\n"
          f"**{len(final)} files** indexed. "
          f"**{sum(len(v) for v in graph.values())}** dependency edges. "
          f"**{len(snippets)}** AST signatures. "
          f"**{sum(1 for e in final if e['b'])}** bloat.\n\n"
          "## Projects (auto-discovered)\n")
    for pj, items in sorted(proj.items(), key=lambda x: -len(x[1])):
        top = max(items, key=lambda i: i["by"])
        md += f"- **{pj}** ({len(items)} files) – top: `{top['p']}` (used by {top['by']})\n"
    md += "\n## Most-Used Files (non-bloat)\n"
    shown = 0
    for e in final:
        if e["b"] or shown >= 15:
            continue
        md += f"- `{e['p']}` (used by {e['by']})"
        if e["as"]:
            md += f" – {e['as'][:60]}"
        md += "\n"
        shown += 1
    (out_dir / "CAVEMAN_INDEX.md").write_text(md)
    return len(final)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="repo root (default: cwd)")
    ap.add_argument("--no-write", action="store_true",
                    help="print summary only, write nothing")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    final, graph, snippets = build(root)
    n = len(final) if args.no_write else write_outputs(root, final, graph, snippets)
    print(f"repo index: {n} entries, "
          f"{sum(1 for e in final if e['ah'])} AST-enriched, "
          f"{sum(len(v) for v in graph.values())} dep edges")
    return 0


if __name__ == "__main__":
    sys.exit(main())
