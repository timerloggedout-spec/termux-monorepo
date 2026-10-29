#!/usr/bin/env python3
"""Pinecone knowledge integration for termux-monorepo.

Consumer: semantic search over the repo's own ops knowledge base
(docs/ops/*.md, top level) for lanes / Delphi research retrieval.
Corpus is chunked deterministically; record ids are content hashes, so a
re-sync upserts the same ids for unchanged text (idempotent).

Modes:
  sync     ensure index + upsert corpus + smoke searches (default)
  search   one query against the synced namespace
  observe  quota reading: list indexes + per-index record counts (JSON)

Runs on GitHub Actions (.github/workflows/pinecone-knowledge.yml) with
PINECONE_API_KEY from the Actions secret store; never on the VM as a service.
Index: termux-knowledge (integrated inference, llama-text-embed-v2,
aws/us-east-1 — the Starter-plan region). Namespace: repo-docs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pinecone_client import PineconeClient, PineconeError  # noqa: E402

INDEX_NAME = "termux-knowledge"
NAMESPACE = "repo-docs"
CORPUS_GLOB = "docs/ops/*.md"
MAX_CHUNK_CHARS = 1500
MAX_RECORDS = 4000
SMOKE_QUERIES = (
    "Pinecone free tier Starter plan limits",
    "Delphi oracle method ballot cross-vote",
    "no-staging rule push all work to the repo",
)


def chunk_markdown(path: Path, text: str):
    """Split on headings, then pack paragraphs into <=MAX_CHUNK_CHARS chunks."""
    records = []
    section = "(intro)"
    buf = []

    def flush():
        if not buf:
            return
        body = "\n".join(buf).strip()
        buf.clear()
        if len(body) < 40:
            return
        for i in range(0, len(body), MAX_CHUNK_CHARS):
            piece = body[i:i + MAX_CHUNK_CHARS].strip()
            if len(piece) < 40:
                continue
            digest = hashlib.sha256(piece.encode("utf-8")).hexdigest()[:12]
            slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")[:48]
            records.append({
                "_id": f"{slug}--{digest}",
                "chunk_text": piece,
                "source_path": str(path),
                "section": section[:120],
            })

    for line in text.splitlines():
        if line.startswith("#"):
            flush()
            section = line.lstrip("# ").strip() or section
            buf.append(line)
        else:
            buf.append(line)
    flush()
    return records


def build_corpus(root: Path):
    records = []
    files = sorted(root.glob(CORPUS_GLOB))
    for f in files:
        records.extend(chunk_markdown(Path(f.relative_to(root)), f.read_text(encoding="utf-8", errors="replace")))
    return files, records[:MAX_RECORDS]


def wait_ready(client, name, timeout_s=600, poll_s=10, sleep=time.sleep):
    deadline = time.monotonic() + timeout_s
    while True:
        desc = client.describe_index(name)
        if desc.get("status", {}).get("ready"):
            return desc
        if time.monotonic() > deadline:
            raise PineconeError(f"index {name} not ready within {timeout_s}s")
        sleep(poll_s)


def observe(client):
    out = {"indexes": []}
    for idx in client.list_indexes():
        entry = {"name": idx.get("name"), "host": idx.get("host"),
                 "dimension": idx.get("dimension"), "metric": idx.get("metric")}
        try:
            stats = client.describe_index_stats(idx["host"])
            entry["total_record_count"] = stats.get("totalRecordCount")
            entry["namespaces"] = {k: v.get("recordCount")
                                   for k, v in stats.get("namespaces", {}).items()}
        except PineconeError as e:
            entry["stats_error"] = str(e)[:160]
        out["indexes"].append(entry)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="sync", choices=("sync", "search", "observe"))
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--root", default=".")
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args(argv)

    client = PineconeClient()
    if args.mode == "observe":
        print(json.dumps(observe(client), indent=1, sort_keys=True))
        return 0

    desc, created = client.ensure_index(INDEX_NAME)
    desc = wait_ready(client, INDEX_NAME)
    host = desc["host"]

    if args.mode == "search":
        hits, usage = client.search_records(host, NAMESPACE, args.query, top_k=args.top_k)
        for h in hits:
            f = h.get("fields", {})
            print(f"{h.get('_score', 0):.4f}  {f.get('source_path', '?')} §{f.get('section', '')}")
        print(json.dumps({"usage": usage}, sort_keys=True))
        return 0

    files, records = build_corpus(Path(args.root))
    sent = client.upsert_records(host, NAMESPACE, records)
    summary = {"index": INDEX_NAME, "created": created, "namespace": NAMESPACE,
               "corpus_files": len(files), "records_upserted": sent, "smoke": []}
    # Eventual consistency: poll until the namespace is queryable.
    hits = []
    for _ in range(12):
        hits, _u = client.search_records(host, NAMESPACE, SMOKE_QUERIES[0], top_k=1)
        if hits:
            break
        time.sleep(10)
    for q in SMOKE_QUERIES:
        hits, usage = client.search_records(host, NAMESPACE, q, top_k=3)
        summary["smoke"].append({
            "query": q,
            "hits": [{"id": h.get("_id"), "score": h.get("_score"),
                      "source_path": h.get("fields", {}).get("source_path")} for h in hits],
            "usage": usage,
        })
    summary["observe"] = observe(client)
    text = json.dumps(summary, indent=1, sort_keys=True)
    print(text)
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as fh:
            fh.write("## Pinecone knowledge sync\n\n```json\n" + text + "\n```\n")
    if not summary["smoke"][0]["hits"]:
        print("SMOKE FAIL: no hits after sync", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
