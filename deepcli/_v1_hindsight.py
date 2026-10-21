"""Hindsight client tools for deepagent.

Scaffold for remote Hindsight memory integration. Defines three async tool
handlers -- ``retain``, ``recall`` and ``reflect`` -- that talk to a remote
Hindsight server over HTTP.

This module is intentionally self-contained: it imports nothing from
``deepagent.py`` and does not modify it. It is meant to be wired in as a
future plugin in a later round.

See ``~/.deepcli/agent_workspaces/hindsight-recon.md`` for the recon notes
that informed this scaffold.

Usage sketch (later round)::

    from deepcli._v1_hindsight import build_hindsight_tools

    tools = build_hindsight_tools()
    for spec in tools:
        register_tool(spec.name, spec.handler, spec.schema)

Environment variables
---------------------
HINDSIGHT_BASE_URL
    Base URL of the Hindsight server. Defaults to ``http://localhost:8888``
    (self-hosted API default port). Use ``https://api.hindsight.vectorize.io``
    for Hindsight Cloud.
HINDSIGHT_API_KEY
    Optional bearer token, sent as ``Authorization: Bearer <key>``. Required
    for Hindsight Cloud, optional for self-hosted deployments.
HINDSIGHT_BANK_ID
    Default bank id when a tool call does not pass one. Defaults to
    ``default``.
HINDSIGHT_TIMEOUT_S
    Per-request timeout in seconds. Defaults to ``30``.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Mapping, MutableMapping, Sequence

import httpx

__all__ = [
    "HindsightClient",
    "HindsightError",
    "HindsightToolSpec",
    "build_hindsight_tools",
    "retain",
    "recall",
    "reflect",
]


DEFAULT_BASE_URL = "http://localhost:8888"
DEFAULT_BANK_ID = "default"
DEFAULT_TIMEOUT_S = 30.0


class HindsightError(RuntimeError):
    """Raised when a Hindsight request fails."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        payload: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


@dataclass(slots=True)
class HindsightClient:
    """Minimal async HTTP client for a remote Hindsight server.

    Only the three core memory operations are exposed (retain / recall /
    reflect). The server's rich low-level API (banks, documents, entities,
    mental models, ...) is out of scope for this scaffold.
    """

    base_url: str = field(
        default_factory=lambda: os.environ.get("HINDSIGHT_BASE_URL", DEFAULT_BASE_URL)
    )
    api_key: str | None = field(
        default_factory=lambda: os.environ.get("HINDSIGHT_API_KEY") or None
    )
    default_bank_id: str = field(
        default_factory=lambda: os.environ.get("HINDSIGHT_BANK_ID", DEFAULT_BANK_ID)
    )
    timeout_s: float = field(
        default_factory=lambda: float(
            os.environ.get("HINDSIGHT_TIMEOUT_S", DEFAULT_TIMEOUT_S)
        )
    )
    _client: httpx.AsyncClient | None = field(default=None, init=False, repr=False)

    # -- plumbing ---------------------------------------------------------

    def _headers(self) -> MutableMapping[str, str]:
        headers: MutableMapping[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url.rstrip("/"),
                headers=self._headers(),
                timeout=self.timeout_s,
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def __aenter__(self) -> "HindsightClient":
        await self._http()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    async def _post(self, path: str, payload: Mapping[str, Any]) -> Any:
        client = await self._http()
        try:
            resp = await client.post(path, json=dict(payload))
        except httpx.HTTPError as exc:  # network / timeout / protocol
            raise HindsightError(
                f"Hindsight request to {self._url(path)} failed: {exc}"
            ) from exc

        if resp.status_code >= 400:
            body: Any
            try:
                body = resp.json()
            except (json.JSONDecodeError, ValueError):
                body = resp.text
            raise HindsightError(
                f"Hindsight {path} returned HTTP {resp.status_code}",
                status_code=resp.status_code,
                payload=body,
            )

        if not resp.content:
            return None
        try:
            return resp.json()
        except (json.JSONDecodeError, ValueError):
            return resp.text

    # -- core operations --------------------------------------------------

    async def aretain(
        self,
        content: str,
        *,
        bank_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Any:
        """Store a memory in the given bank."""
        payload: dict[str, Any] = {
            "bank_id": bank_id or self.default_bank_id,
            "content": content,
        }
        if metadata:
            payload["metadata"] = dict(metadata)
        return await self._post("/retain", payload)

    async def arecall(
        self,
        query: str,
        *,
        bank_id: str | None = None,
        limit: int | None = None,
    ) -> Any:
        """Retrieve relevant memories for a query."""
        payload: dict[str, Any] = {
            "bank_id": bank_id or self.default_bank_id,
            "query": query,
        }
        if limit is not None:
            payload["limit"] = int(limit)
        return await self._post("/recall", payload)

    async def areflect(
        self,
        query: str,
        *,
        bank_id: str | None = None,
    ) -> Any:
        """Ask the server to synthesize an answer from stored memories."""
        payload: dict[str, Any] = {
            "bank_id": bank_id or self.default_bank_id,
            "query": query,
        }
        return await self._post("/reflect", payload)


# ---------------------------------------------------------------------------
# Tool specs
# ---------------------------------------------------------------------------


ToolHandler = Callable[..., Awaitable[Any]]


@dataclass(slots=True)
class HindsightToolSpec:
    """A single tool exposed to the agent runtime."""

    name: str
    description: str
    schema: Mapping[str, Any]
    handler: ToolHandler


_DEFAULT_CLIENT: HindsightClient | None = None


def _client() -> HindsightClient:
    """Lazily construct a process-wide default client."""
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None:
        _DEFAULT_CLIENT = HindsightClient()
    return _DEFAULT_CLIENT


async def retain(
    content: str,
    *,
    bank_id: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    client: HindsightClient | None = None,
) -> dict[str, Any]:
    """Tool handler: persist a memory to the remote Hindsight server."""
    active = client or _client()
    result = await active.aretain(content, bank_id=bank_id, metadata=metadata)
    return {"ok": True, "operation": "retain", "result": result}


async def recall(
    query: str,
    *,
    bank_id: str | None = None,
    limit: int | None = None,
    client: HindsightClient | None = None,
) -> dict[str, Any]:
    """Tool handler: retrieve relevant memories from the server."""
    active = client or _client()
    result = await active.arecall(query, bank_id=bank_id, limit=limit)
    return {"ok": True, "operation": "recall", "result": result}


async def reflect(
    query: str,
    *,
    bank_id: str | None = None,
    client: HindsightClient | None = None,
) -> dict[str, Any]:
    """Tool handler: synthesize an answer from stored memories."""
    active = client or _client()
    result = await active.areflect(query, bank_id=bank_id)
    return {"ok": True, "operation": "reflect", "result": result}


def build_hindsight_tools(
    client: HindsightClient | None = None,
) -> Sequence[HindsightToolSpec]:
    """Return the retain / recall / reflect tool specs for registration.

    ``client`` is captured in the handler closures when provided; otherwise
    the process-wide default client is resolved lazily on first call.
    """

    async def _retain(
        content: str,
        bank_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await retain(content, bank_id=bank_id, metadata=metadata, client=client)

    async def _recall(
        query: str,
        bank_id: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await recall(query, bank_id=bank_id, limit=limit, client=client)

    async def _reflect(
        query: str,
        bank_id: str | None = None,
    ) -> dict[str, Any]:
        return await reflect(query, bank_id=bank_id, client=client)

    return (
        HindsightToolSpec(
            name="hindsight_retain",
            description=(
                "Persist a fact, observation or experience to long-term "
                "Hindsight memory so it can be recalled later."
            ),
            schema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The memory text to store.",
                    },
                    "bank_id": {
                        "type": "string",
                        "description": "Optional memory bank id.",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional structured metadata.",
                    },
                },
                "required": ["content"],
            },
            handler=_retain,
        ),
        HindsightToolSpec(
            name="hindsight_recall",
            description=(
                "Retrieve memories relevant to a query from Hindsight long-term memory."
            ),
            schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query.",
                    },
                    "bank_id": {
                        "type": "string",
                        "description": "Optional memory bank id.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to return.",
                    },
                },
                "required": ["query"],
            },
            handler=_recall,
        ),
        HindsightToolSpec(
            name="hindsight_reflect",
            description=(
                "Ask Hindsight to synthesize an answer or mental model from "
                "everything it has stored about a topic."
            ),
            schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to reflect on.",
                    },
                    "bank_id": {
                        "type": "string",
                        "description": "Optional memory bank id.",
                    },
                },
                "required": ["query"],
            },
            handler=_reflect,
        ),
    )
