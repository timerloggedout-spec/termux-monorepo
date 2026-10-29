#!/usr/bin/env python3
"""Minimal stdlib Pinecone REST client (control + data plane).

Auth: PINECONE_API_KEY env only; the key is never printed or logged.
API version pinned to 2025-10 per vendor reference docs (2026-10-28):
- control plane: https://api.pinecone.io/indexes[/create-for-model]
- data plane (integrated-inference indexes): https://{host}/records/namespaces/{ns}/upsert|search
- stats: https://{host}/describe_index_stats
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

API_VERSION = "2025-10"
CONTROL_BASE = "https://api.pinecone.io"


class PineconeError(RuntimeError):
    pass


def _default_request(method, url, headers, body_bytes, timeout=120):
    req = urllib.request.Request(url, data=body_bytes, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


class PineconeClient:
    def __init__(self, api_key=None, request=None):
        self.api_key = api_key if api_key is not None else os.environ.get("PINECONE_API_KEY", "")
        if not self.api_key:
            raise PineconeError("PINECONE_API_KEY not set")
        self._request = request or _default_request

    def _call(self, method, url, payload=None, ndjson=None):
        headers = {"Api-Key": self.api_key, "X-Pinecone-Api-Version": API_VERSION,
                   "Accept": "application/json"}
        body = None
        if ndjson is not None:
            headers["Content-Type"] = "application/x-ndjson"
            body = ndjson.encode("utf-8")
        elif payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")
        status, raw = self._request(method, url, headers, body)
        if status >= 400:
            raise PineconeError(f"{method} {url} -> HTTP {status}: {raw[:300]!r}")
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    # --- control plane ---
    def list_indexes(self):
        return self._call("GET", f"{CONTROL_BASE}/indexes").get("indexes", [])

    def describe_index(self, name):
        return self._call("GET", f"{CONTROL_BASE}/indexes/{name}")

    def create_index_for_model(self, name, model="llama-text-embed-v2",
                               field="chunk_text", cloud="aws", region="us-east-1"):
        return self._call("POST", f"{CONTROL_BASE}/indexes/create-for-model", {
            "name": name, "cloud": cloud, "region": region,
            "embed": {"model": model, "field_map": {"text": field}},
        })

    def ensure_index(self, name, **kw):
        for idx in self.list_indexes():
            if idx.get("name") == name:
                return self.describe_index(name), False
        return self.create_index_for_model(name, **kw), True

    # --- data plane ---
    def upsert_records(self, host, namespace, records, batch_size=50):
        sent = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            ndjson = "\n".join(json.dumps(r, ensure_ascii=False) for r in batch)
            self._call("POST", f"https://{host}/records/namespaces/{namespace}/upsert",
                       ndjson=ndjson)
            sent += len(batch)
        return sent

    def search_records(self, host, namespace, text, top_k=5,
                       fields=("chunk_text", "source_path", "section")):
        out = self._call("POST", f"https://{host}/records/namespaces/{namespace}/search", {
            "query": {"inputs": {"text": text}, "top_k": top_k},
            "fields": list(fields),
        })
        return out.get("result", {}).get("hits", []), out.get("usage", {})

    def describe_index_stats(self, host):
        return self._call("POST", f"https://{host}/describe_index_stats", {})
