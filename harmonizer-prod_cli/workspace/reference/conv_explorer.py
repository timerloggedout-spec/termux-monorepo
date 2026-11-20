#!/usr/bin/env python3
"""Search DeepSeek conversations – live API or local export."""
import sys, json, re, argparse, hashlib
from synthegration_index import MessageIndex
from pathlib import Path

HOME = Path.home()
DOWNLOADS = HOME / "storage" / "downloads" / "synthegration_exports"
CACHE_DIR = HOME / ".cache" / "synthegration"

def cache_manifest(export_root: Path, manifest: list):
    """Write a quick-lookup index to ~/.cache/synthegration/"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / (export_root.resolve().name + ".idx.json")
    index = {
        "source": str(export_root.resolve()),
        "sessions": {},
        "total_blocks": len(manifest)
    }
    for b in manifest:
        sid = b.get("conversation_id", "unknown")
        if sid not in index["sessions"]:
            index["sessions"][sid] = {
                "title": b.get("conversation_title", ""),
                "block_count": 0,
                "languages": set()
            }
        index["sessions"][sid]["block_count"] += 1
        index["sessions"][sid]["languages"].add(b.get("language", "text"))
    # Convert sets to lists for JSON
    for s in index["sessions"].values():
        s["languages"] = list(s["languages"])
    cache_file.write_text(json.dumps(index, indent=2))
    return index

def load_cached_index(export_root: Path):
    """Try to load cached index, return None if missing or stale."""
    cache_file = CACHE_DIR / (export_root.resolve().name + ".idx.json")
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except:
            pass
    return None


def load_offline_manifest(export_root: Path):
    """Load manifest.json from export directory, using cache if available."""
    export_root = export_root.resolve()
    cached = load_cached_index(export_root)
    if cached:
        # Cache exists; we still need full manifest for code extraction
        pass
    manifest_path = export_root / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    # Fallback: try _1st-processed subdirectory
    alt = export_root / "_1st-processed" / "manifest.json"
    if alt.exists():
        with open(alt) as f:
            return json.load(f)
    # Last resort: search for any manifest.json
    for mf in export_root.rglob("manifest.json"):
        with open(mf) as f:
            return json.load(f)
    raise FileNotFoundError(f"No manifest.json found in {export_root}")

def search_offline(manifest, term: str):
    """Return blocks matching term in title, language, or code snippet."""
    results = []
    for block in manifest:
        title = block.get("conversation_title", "").lower()
        lang = block.get("language", "").lower()
        snippet = block.get("preceding_text_snippet", "").lower()
        code = block.get("code", "").lower()
        term_lower = term.lower()
        if term_lower in title or term_lower in lang or term_lower in snippet or term_lower in code:
            results.append(block)
    return results

def export_blocks(blocks, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for blk in blocks:
        h = blk.get("code_hash", hashlib.sha256(blk["code"].encode()).hexdigest()[:8])
        lang = blk.get("language", "text")
        ext = {"python":"py","javascript":"js","typescript":"ts","bash":"sh","html":"html","css":"css","json":"json"}.get(lang, lang)
        fname = f"{lang}_{h}.{ext}"
        (out / fname).write_text(blk["code"])
        # Write meta
        (out / (fname + ".meta.json")).write_text(json.dumps(blk, indent=2))
    manifest_out = out / "manifest.json"
    if manifest_out.exists():
        existing = json.loads(manifest_out.read_text())
        existing.extend(blocks)
        manifest_out.write_text(json.dumps(existing, indent=2))
    else:
        manifest_out.write_text(json.dumps(blocks, indent=2))
    return len(blocks)

def list_offline_sessions(manifest):
    sessions = {}
    for b in manifest:
        sid = b.get("conversation_id", "unknown")
        title = b.get("conversation_title", "Untitled")
        if sid not in sessions:
            sessions[sid] = title
    return sessions

def main():
    parser = argparse.ArgumentParser(description="DeepSeek conversation explorer")
    parser.add_argument("search", nargs="?", help="Keyword to filter sessions/blocks")
    parser.add_argument("--export", type=str, help="Export code blocks from session ID")
    parser.add_argument("--list", action="store_true", help="List sessions")
    parser.add_argument("--offline", type=str, help="Use local export directory instead of live API")
    parser.add_argument("--output", type=str, help="Custom output directory for export")
    args = parser.parse_args()

    offline_root = Path(args.offline) if args.offline else None
    manifest = None
    if offline_root:
        manifest = load_offline_manifest(offline_root)
        print(f"Loaded {len(manifest)} blocks from offline export")
    else:
        # Live API mode
        sys.path.insert(0, "/data/data/com.termux/files/home/deepcli")
        from deepcli.core import get_token, fetch_sessions, get_history

    if args.list:
        if manifest:
            sessions = list_offline_sessions(manifest)
            for sid, title in sorted(sessions.items(), key=lambda x: x[1]):
                print(f"{sid} | {title} ({sum(1 for b in manifest if b['conversation_id']==sid)} blocks)")
        else:
            token = get_token()
            sessions = fetch_sessions(token)
            for s in sessions[:100]:
                print(f"{s.get('id','')} | {s.get('title','Untitled')}")
        return

    if args.export:
        out_dir = Path(args.output) if args.output else DOWNLOADS / args.export
        if manifest:
            blocks = [b for b in manifest if b.get("conversation_id") == args.export]
            n = export_blocks(blocks, out_dir)
            print(f"Exported {n} blocks from offline manifest to {out_dir}")
        else:
            token = get_token()
            msgs = get_history(token, args.export)
            blocks = []
            for msg in msgs:
                content = msg.get("content","")
                for match in re.finditer(r"```(\w+)?\n(.*?)```", content, re.DOTALL):
                    blocks.append({
                        "conversation_id": args.export,
                        "conversation_title": msg.get("title",""),
                        "message_role": msg.get("role",""),
                        "message_timestamp": msg.get("inserted_at",""),
                        "language": match.group(1) or "text",
                        "code": match.group(2),
                        "code_hash": hashlib.sha256(match.group(2).encode()).hexdigest()[:16]
                    })
            n = export_blocks(blocks, out_dir)
            print(f"Exported {n} blocks from live session to {out_dir}")
        return


    if args.index_export:
        mi = MessageIndex()
        count = mi.load_export(Path(args.index_export))
        print(f"Indexed {count} terms from {args.index_export}")
        return

    if args.search_messages:
        mi = MessageIndex.load()
        if not mi.inverted:
            print("Message index not built. Run with --index-export <conversations.json> first.")
            return
        term = args.search
        if not term:
            print("Please provide a search term.")
            return
        results = mi.search(term)
        for sid, midx, role, snippet, title in results:
            print(f"{sid[:8]}... | {title[:60]} | {role}: {snippet[:100]}")
        if not results:
            print("No matches found in message bodies.")
        return

    if args.search:
        if manifest:
            results = search_offline(manifest, args.search)
            print(f"Found {len(results)} blocks matching '{args.search}':")
            for b in results[:20]:
                print(f"  {b['conversation_id'][:8]}... | {b['conversation_title'][:60]} | {b['language']} | {b['code_hash']}")
        else:
            token = get_token()
            sessions = fetch_sessions(token)
            hits = [s for s in sessions if args.search.lower() in (s.get("title","") or "").lower()]
            for s in hits:
                print(f"{s.get('id','')} | {s.get('title','')}")
        return

    parser.print_help()


def export_session_live(session_id: str, output_dir: str = None, account: str = "default"):
    """Fetch a session via live API and export its code blocks to Downloads."""
    import sys, json, re
    from pathlib import Path
    sys.path.insert(0, str(HOME / "deepcli"))
    from deepcli.core import get_token, get_history
    if output_dir is None:
        output_dir = DOWNLOADS / session_id
    else:
        output_dir = Path(output_dir)
    token = get_token()
    msgs = get_history(token, session_id)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    blocks = []
    for msg in msgs:
        content = msg.get("content", "")
        # extract fenced code blocks
        # Extract thinking/reasoning content if present
        thinking = msg.get('reasoning_content', '') or msg.get('thinking', '') or ''
        if thinking:
            tname = f"{msg.get('role','unknown')}_thinking_{len(blocks)}.md"
            (output_dir / tname).write_text(thinking)
            blocks.append({"msg_id": msg.get("id"), "role": msg.get("role"), "language": "thinking", "code_snippet": thinking[:200]})

        for match in re.finditer(r"```(\w*)\n(.*?)```", content, re.DOTALL):
            lang = match.group(1) or "text"
            code = match.group(2)
            fname = f"{msg.get('role','unknown')}_{len(blocks)}.{lang if lang != 'text' else 'txt'}"
            (output_dir / fname).write_text(code)
            blocks.append({"msg_id": msg.get("id"), "role": msg.get("role"), "language": lang, "code_snippet": code[:200]})
    manifest = output_dir / "manifest.json"
    manifest.write_text(json.dumps(blocks, indent=2))
    # Also save full messages for later re-harvesting
    (output_dir / "messages.json").write_text(json.dumps(msgs, indent=2, ensure_ascii=False))
    print(f"Exported {len(blocks)} blocks to {output_dir}")
    return blocks

if __name__ == "__main__":
    main()
