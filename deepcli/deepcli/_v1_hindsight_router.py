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


class RoutedHindsightClient:
    def __init__(self, cloud=None, local=None):
        self.cloud = cloud or HindsightClient()
        self.local = local or LocalHindsightClient()
        self.default_bank_id = self.cloud.default_bank_id
        self.base_url = self.cloud.base_url
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
        if self._cloud_healthy:
            try:
                return await self.cloud.aretain(content, bank_id=bank_id, metadata=metadata)
            except HindsightError as e:
                if getattr(e, "status_code", None) in DEMOTE_CODES:
                    self._demote("HTTP " + str(e.status_code))
                else:
                    raise
        return await self.local.aretain(content, bank_id=bank_id, metadata=metadata)

    async def arecall(self, query, *, bank_id=None, limit=None):
        self._maybe_restore()
        if self._cloud_healthy:
            try:
                return await self.cloud.arecall(query, bank_id=bank_id, limit=limit)
            except HindsightError as e:
                if getattr(e, "status_code", None) in DEMOTE_CODES:
                    self._demote("HTTP " + str(e.status_code))
                else:
                    raise
        return await self.local.arecall(query, bank_id=bank_id, limit=limit)

    async def areflect(self, query, *, bank_id=None):
        self._maybe_restore()
        if self._cloud_healthy:
            try:
                return await self.cloud.areflect(query, bank_id=bank_id)
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
