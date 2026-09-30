"""Local FTS5 Hindsight client. Same async interface as cloud."""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Mapping

DB_DEFAULT = Path.home() / ".deepcli/bank-local.db"


class LocalHindsightClient:
    def __init__(self, db_path=None, bank_id=None):
        self.db_path = Path(db_path) if db_path else DB_DEFAULT
        self.default_bank_id = bank_id or os.environ.get(
            "HINDSIGHT_BANK_ID", "deepagent::termux-monorepo"
        )

    def _con(self):
        c = sqlite3.connect(self.db_path)
        c.execute("PRAGMA journal_mode=WAL")
        return c

    async def aretain(self, content, *, bank_id=None, metadata=None):
        _bank = bank_id or self.default_bank_id
        _key = "local:" + uuid.uuid4().hex[:12]
        _meta = {k: str(v) for k, v in (metadata or {}).items()}
        _meta["bank_id"] = _bank
        _meta["local_write"] = "1"
        c = self._con()
        try:
            c.execute(
                "INSERT INTO memory(source,key,content,metadata) VALUES(?,?,?,?)",
                ("local_retain", _key, content[:8000], json.dumps(_meta)),
            )
            c.commit()
            return {"success": True, "bank_id": _bank, "items_count": 1,
                    "async": False, "local": True, "id": _key}
        finally:
            c.close()

    async def arecall(self, query, *, bank_id=None, limit=None):
        _limit = int(limit) if limit else 10
        _q = (query or "").strip()
        c = self._con()
        try:
            if not _q:
                return {"results": [], "local": True, "query": query}
            _safe = _q.replace('"', '""')
            try:
                rows = c.execute(
                    "SELECT m.id, m.source, m.key, m.content, m.metadata "
                    "FROM memory_fts f JOIN memory m ON m.id = f.rowid "
                    "WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
                    (_safe, _limit),
                ).fetchall()
            except sqlite3.OperationalError:
                rows = c.execute(
                    "SELECT id, source, key, content, metadata FROM memory "
                    "WHERE content LIKE ? LIMIT ?",
                    ("%" + _q + "%", _limit),
                ).fetchall()
            results = []
            for rid, src, key, content, mj in rows:
                try:
                    meta = json.loads(mj or "{}")
                except Exception:
                    meta = {}
                results.append({
                    "id": key or str(rid),
                    "text": content[:500],
                    "type": "observation",
                    "source": src,
                    "metadata": meta,
                })
            return {"results": results, "local": True, "query": query, "count": len(results)}
        finally:
            c.close()

    async def areflect(self, query, *, bank_id=None):
        return {"answer": None, "reason": "local-only", "local": True}

    async def aclose(self):
        pass
