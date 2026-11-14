#!/usr/bin/env python3
"""func_index.py — repo-side adaptive variant of workspace/llm_map/func_indexer.py.

Original: regex extraction over the device-generated llm_index_compact.jsonl,
top-level `def`/`class` only (misses async, nested defs and methods), reads
files from $HOME. This variant walks the git index of a checkout:

  * python  -> ast.parse: FunctionDef + AsyncFunctionDef + ClassDef at ANY
               depth, with dotted qualnames (Class.method, outer.inner);
  * js/ts   -> regex: function/class declarations, arrow functions assigned
               to const/let/var, and class methods;
  * output  -> workspace/llm_map/func_index.jsonl, same record shape as the
               original {file, name, kind, line, sig, doc}; python records
               add "qual" (dotted qualname) — additive, original consumers
               ignore unknown keys (verified: the one in-repo reader,
               build_final_all_profile.py, reads via named .get() only —
               Delphi schema-fit read, 2026-11-01).

Kind code table (of record — the precursor's value domain; kind flows
verbatim into the compact index's `as` summaries, so codes stay stable):
  python:  "de" = def/async def, "clas" = class   (precursor codes)
  js/ts:   "function", "class"                    (precursor codes)
Async-ness and nesting are NOT new kind codes: they are carried by `sig`
(the verbatim source line) and `qual` (dotted qualname) respectively.

Consumers: build_repo_index.py (signatures), foresight_feed.py (coverage).
Stdlib only; deterministic ordering (path, line).
"""
import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

MAX_PARSE_BYTES = 500_000
JS_FUNC = re.compile(r"(?:async\s+)?function\s+([\w$]+)|class\s+([\w$]+)")
JS_ARROW = re.compile(r"(?:const|let|var)\s+([\w$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>")
JS_METHOD = re.compile(r"^\s{2,}(?:async\s+)?([\w$]+)\s*\([^)]*\)\s*\{")


def git_files(root):
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                         capture_output=True, text=True, check=True).stdout
    return sorted(p for p in out.split("\0") if p)


def py_defs(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    lines = text.splitlines()
    out = []

    def visit(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "de"  # precursor code domain (see docstring table)
                qual = prefix + child.name
                sig = lines[child.lineno - 1].strip()[:120] if child.lineno <= len(lines) else ""
                doc = (ast.get_docstring(child) or "").split("\n")[0][:80]
                out.append({"name": child.name, "qual": qual, "kind": kind,
                            "line": child.lineno, "sig": sig, "doc": doc})
                visit(child, qual + ".")
            elif isinstance(child, ast.ClassDef):
                qual = prefix + child.name
                sig = lines[child.lineno - 1].strip()[:120] if child.lineno <= len(lines) else ""
                doc = (ast.get_docstring(child) or "").split("\n")[0][:80]
                out.append({"name": child.name, "qual": qual, "kind": "clas",
                            "line": child.lineno, "sig": sig, "doc": doc})
                visit(child, qual + ".")
            else:
                visit(child, prefix)

    visit(tree, "")
    return out


def js_defs(text):
    out = []
    in_class = False
    for i, line in enumerate(text.splitlines(), 1):
        m = JS_FUNC.search(line)
        if m:
            name = m.group(1) or m.group(2)
            kind = "class" if m.group(2) else "function"
            out.append({"name": name, "qual": name, "kind": kind,
                        "line": i, "sig": line.strip()[:120], "doc": ""})
            in_class = kind == "class"
            continue
        m = JS_ARROW.search(line)
        if m:
            out.append({"name": m.group(1), "qual": m.group(1),
                        "kind": "function", "line": i,
                        "sig": line.strip()[:120], "doc": ""})
            continue
        if in_class:
            m = JS_METHOD.match(line)
            if m and m.group(1) not in ("if", "for", "while", "switch", "catch"):
                out.append({"name": m.group(1), "qual": m.group(1),
                            "kind": "function", "line": i,
                            "sig": line.strip()[:120], "doc": ""})
        if line.strip() == "}":
            in_class = False
    return out


def build(root, paths=None):
    records = []
    for p in (paths if paths is not None else git_files(root)):
        ext = Path(p).suffix
        if ext not in (".py", ".js", ".ts", ".tsx", ".jsx"):
            continue
        fp = root / p
        try:
            if fp.stat().st_size > MAX_PARSE_BYTES:
                continue
            text = fp.read_text(errors="replace")
        except OSError:
            continue
        defs = py_defs(text) if ext == ".py" else js_defs(text)
        for d in defs:
            records.append({"file": p, **d})
    records.sort(key=lambda r: (r["file"], r["line"]))
    return records


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="workspace/llm_map/func_index.jsonl")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    records = build(root)
    if not args.no_write:
        out = root / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"func index: {len(records)} definitions "
          f"across {len({r['file'] for r in records})} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
