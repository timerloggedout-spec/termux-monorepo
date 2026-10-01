"""Quota-aware router. Cloud primary; local FTS5 fallback; circuit breaker."""
from __future__ import annotations

import os
import sys
import time

try:
    from ._v1_hindsight import HindsightClient, HindsightError
except ImportError:
    from _v1_hindsight import HindsightClient, HindsightError  # type: ignore

try:
    from ._v1_hindsight_local import LocalHindsightClient
except ImportError:
    from _v1_hindsight_local import LocalHindsightClient  # type: ignore


DEMOTE_CODES = {402, 429, 500, 502, 503, 504}
RESET_AFTER_S = int(os.environ.get("HINDSIGHT_ROUTER_RESET_S", "900"))


class _LocalCodespaceClient:
    """HTTP client for self-hosted Hindsight over SSH tunnel (localhost:18888)."""
    def __init__(self, url: str):
        self.base_url = url
        self.default_bank_id = os.environ.get(
            "HINDSIGHT_BANK_ID", "deepagent::termux-monorepo"
        )

    async def _req(self, path: str, method: str = "GET", payload=None):
        import json, urllib.request, urllib.error
        url = self.base_url.rstrip("/") + path
        body = json.dumps(payload).encode() if payload else None
        hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
        req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise HindsightError(f"codespace {path} HTTP {e.code}",
                                 status_code=e.code, payload=e.read()[:300])
        except Exception as e:
            raise HindsightError(f"codespace unreachable: {e}")

    async def aretain(self, content, *, bank_id=None, metadata=None):
        _b = bank_id or self.default_bank_id
        item = {"content": content}
        if metadata:
            item["metadata"] = {k: str(v) for k, v in metadata.items()}
        return await self._req(f"/v1/default/banks/{_b}/memories",
                               method="POST", payload={"items": [item]})

    async def arecall(self, query, *, bank_id=None, limit=None):
        _b = bank_id or self.default_bank_id
        p = {"query": query}
        if limit:
            p["top_k"] = int(limit)
        return await self._req(f"/v1/default/banks/{_b}/memories/recall",
                               method="POST", payload=p)

    async def areflect(self, query, *, bank_id=None):
        _b = bank_id or self.default_bank_id
        return await self._req(f"/v1/default/banks/{_b}/reflect",
                               method="POST", payload={"query": query})

    async def aclose(self):
        pass


class RoutedHindsightClient:
    def __init__(self, cloud=None, local=None):
        self.cloud = cloud or HindsightClient()
        self.local = local or LocalHindsightClient()
        _cs_url = os.environ.get("HS_LOCAL_URL", "")
        self.codespace = _LocalCodespaceClient(_cs_url) if _cs_url else None
        self.default_bank_id = os.environ.get(
            "HINDSIGHT_BANK_ID", self.cloud.default_bank_id
        )
        self.base_url = _cs_url or self.cloud.base_url
        self._cloud_healthy = True
        self._demoted_at = 0.0

    def _maybe_restore(self):
        if (not self._cloud_healthy) and (time.time() - self._demoted_at) > RESET_AFTER_S:
            self._cloud_healthy = True

    def _demote(self, reason):
        self._cloud_healthy = False
        self._demoted_at = time.time()
        print("[router] cloud demoted: " + reason + "; routing local FTS5", file=sys.stderr)

    async def aretain(self, content, *, bank_id=None, metadata=None):
        self._maybe_restore()
        if self.codespace is not None:
            try:
                return await self.codespace.aretain(content, bank_id=bank_id, metadata=metadata)
            except HindsightError as e:
                if getattr(e, "status_code", None) in DEMOTE_CODES:
                    self._demote("HTTP " + str(e.status_code))
                else:
                    raise
        return await self.local.aretain(content, bank_id=bank_id, metadata=metadata)

    async def arecall(self, query, *, bank_id=None, limit=None):
        self._maybe_restore()
        if self.codespace is not None:
            try:
                return await self.codespace.arecall(query, bank_id=bank_id, limit=limit)
            except HindsightError as e:
                if getattr(e, "status_code", None) in DEMOTE_CODES:
                    self._demote("HTTP " + str(e.status_code))
                else:
                    raise
        return await self.local.arecall(query, bank_id=bank_id, limit=limit)

    async def areflect(self, query, *, bank_id=None):
        self._maybe_restore()
        if self.codespace is not None:
            try:
                return await self.codespace.areflect(query, bank_id=bank_id)
            except HindsightError as e:
                if getattr(e, "status_code", None) in DEMOTE_CODES:
                    self._demote("HTTP " + str(e.status_code))
                else:
                    raise
        return await self.local.areflect(query, bank_id=bank_id)

    async def aclose(self):
        try:
            await self.cloud.aclose()
        except Exception:
            pass

    def status(self):
        return {
            "cloud_healthy": self._cloud_healthy,
            "demoted_at": self._demoted_at,
            "base_url": self.base_url,
            "bank_id": self.default_bank_id,
            "local_db": str(self.local.db_path),
        }
