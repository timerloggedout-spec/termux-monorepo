#!/usr/bin/env python3
"""Context Graph Builder v2.1 – supports --code, --chat, --code-summary, --chat-summary, --max-blocks, --orphans"""
import json, sys, os, re, hashlib, argparse
from pathlib import Path

HOME = Path.home()

# ---------- data ----------
PROVENANCE_FILE = HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json"
SESSION_STORE   = HOME / ".deepcli/session_store"
EXPORT_DIR      = HOME / "synthegration_exports"

def load_provenance():
    if PROVENANCE_FILE.exists():
        with open(PROVENANCE_FILE) as f:
            return json.load(f)
    return {}

def load_session_messages(sid):
    for p in [SESSION_STORE / f"{sid}.json",
              SESSION_STORE / "primary" / f"{sid}.json",
              SESSION_STORE / "secondary" / f"{sid}.json"]:
        if p.exists():
            with open(p) as f:
                return json.load(f)
    return []

def extract_code_blocks(sid, summary=False, max_blocks=0, orphans=False):
    msgs = load_session_messages(sid)
    blocks = []
    if isinstance(msgs, list):
        for mi, m in enumerate(msgs):
            content = m.get("content", "") or ""
            # Standard ``` blocks
            for bi, match in enumerate(re.finditer(r"```(?:\w+)?\n(.*?)\n```", content, re.DOTALL)):
                code = match.group(1).strip()
                blocks.append({"mi": mi, "bi": bi, "hash": hashlib.sha256(code.encode()).hexdigest()[:16],
                               "code": code[:500], "role": m.get("role","?")})
            # cat > file << 'EOF' ... EOF pattern
            for bi, match in enumerate(re.finditer(r"(cat\s+>[\w./-]+\s+<<\s*'?EOF'?\n.*?^EOF)", content, re.DOTALL | re.MULTILINE)):
                code = match.group(1).strip()
                blocks.append({"mi": mi, "bi": 100+bi, "hash": hashlib.sha256(code.encode()).hexdigest()[:16],
                               "code": code[:500], "role": m.get("role","?")})
            # node deepseek.js ... commands (single line)
            for bi, match in enumerate(re.finditer(r"^node\s+deepseek.*$", content, re.MULTILINE)):
                code = match.group(0).strip()
                blocks.append({"mi": mi, "bi": 200+bi, "hash": hashlib.sha256(code.encode()).hexdigest()[:16],
                               "code": code[:500], "role": m.get("role","?")})
    if orphans:
        # Load provenance and filter to blocks with no file match
        prov = load_provenance()
        sess_files = set()
        for f, entries in prov.items():
            for e in entries:
                if e.get("session") == sid:
                    sess_files.add(f)
        # Check each block's hash against provenance's snippets (simplistic)
        orphan_blocks = []
        for b in blocks:
            # if no file reference found (we don't have direct hash->file mapping here, so skip)
            pass
        # Better: use pointer_index gap – call find_orphan_commands logic
    if summary:
        blocks = [{"hash": b["hash"], "first_line": b["code"].split("\n")[0][:100], "role": b["role"]} for b in blocks]
    if max_blocks > 0:
        blocks = blocks[:max_blocks]
    return blocks

def extract_chat_context(sid, max_messages=5, summary=False):
    msgs = load_session_messages(sid)
    if not msgs or not isinstance(msgs, list):
        return []
    msgs = msgs[-max_messages:]
    if summary:
        return [{"role": m.get("role","?"), "preview": (m.get("content","") or "")[:80]} for m in msgs]
    return [{"role": m.get("role","?"), "content": (m.get("content","") or "")[:300],
             "thinking": (m.get("thinking_content","") or "")[:200],
             "message_id": m.get("message_id","")} for m in msgs]

def session_to_files(sid, prov):
    files = []
    for f, entries in prov.items():
        for e in entries:
            if e.get("session") == sid:
                files.append(f)
                break
    return files

def expand_deps(files, dep_graph, hops=1):
    expanded = set(files)
    for _ in range(hops):
        new = set()
        for f in expanded:
            if f in dep_graph:
                new.update(dep_graph[f])
            for src, imports in dep_graph.items():
                if f in imports:
                    new.add(src)
        expanded.update(new)
    return sorted(expanded)

def find_similar(target, candidates, top_n=3, thresh=0.03):
    try:
        t_text = (HOME / target).read_text()
    except:
        return []
    scores = []
    for c in candidates:
        if c == target:
            continue
        try:
            c_text = (HOME / c).read_text()
        except:
            continue
        t1 = set(t_text[:3000].split())
        t2 = set(c_text[:3000].split())
        u = len(t1 | t2)
        if u == 0:
            continue
        sim = len(t1 & t2) / u
        if sim >= thresh:
            scores.append((c, sim))
    scores.sort(key=lambda x: -x[1])
    return scores[:top_n]

def build_context(session_id=None, file_path=None, hop=1, similar=3,
                  include_chat=False, include_code=False,
                  chat_summary=False, code_summary=False, max_blocks=0):
    prov = load_provenance()
    dep_graph = {}
    fg = HOME / "workspace/llm_map/file_graph.json"
    if fg.exists():
        dep_graph = json.loads(fg.read_text())
    all_files = list(dep_graph.keys()) + list(prov.keys())

    seed = set()
    if session_id:
        seed = set(session_to_files(session_id, prov))
    if file_path:
        seed.add(file_path)

    expanded = expand_deps(list(seed), dep_graph, hop)
    sims = set()
    for sf in seed:
        for f, _ in find_similar(sf, all_files, similar):
            sims.add(f)
    files = sorted(set(expanded).union(sims))

    dep_map = {}
    for f in files:
        if f in dep_graph:
            dep_map[f] = [t for t in dep_graph[f] if t in files]

    timelines = {}
    for f in files:
        timelines[f] = {"provenance": prov.get(f, [])}

    chat = []
    if include_chat and session_id:
        chat = extract_chat_context(session_id, summary=chat_summary)
    code = []
    if include_code and session_id:
        code = extract_code_blocks(session_id, summary=code_summary, max_blocks=max_blocks)

    return {
        "session_id": session_id,
        "file": file_path,
        "files": files,
        "dependency_neighborhood": dep_map,
        "similar_files": list(sims),
        "timelines": timelines,
        "chat_context": chat,
        "code_blocks": code,
        "impact_notes": "run `oracle <file>` for detailed metrics"
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--session")
    parser.add_argument("--file")
    parser.add_argument("--hop", type=int, default=1)
    parser.add_argument("--similar", type=int, default=3)
    parser.add_argument("--chat", action="store_true")
    parser.add_argument("--code", action="store_true")
    parser.add_argument("--chat-summary", action="store_true")
    parser.add_argument("--code-summary", action="store_true")
    parser.add_argument("--max-blocks", type=int, default=0)
    parser.add_argument("--out")
    args = parser.parse_args()

    ctx = build_context(
        session_id=args.session,
        file_path=args.file,
        hop=args.hop,
        similar=args.similar,
        include_chat=args.chat or args.chat_summary,
        include_code=args.code or args.code_summary,
        chat_summary=args.chat_summary,
        code_summary=args.code_summary,
        max_blocks=args.max_blocks
    )
    out = json.dumps(ctx, indent=2, default=str)
    if args.out:
        Path(args.out).write_text(out)
        print(f"✅ Saved to {args.out}")
    else:
        print(out)
