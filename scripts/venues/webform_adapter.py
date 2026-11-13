#!/usr/bin/env python3
"""Generic web-form venue adapter (QUE #5254).

For form-only venues: a configurable multipart/form POST driven by
the entry's binding {endpoint, fields{}, file_field, url_extract} —
the response either IS the public URL (plain-text body, the
file-host shape) or carries it (regex extract). No venue-specific
code per form venue; a new form venue is a binding, not a module.
"""
from __future__ import annotations

import re
import urllib.request
import uuid
from pathlib import Path


def build_multipart(fields: dict, file_field: str | None,
                    artifact: str | None) -> tuple[bytes, str]:
    boundary = f"venue-exec-{uuid.uuid4().hex}"
    chunks = []
    for name, value in (fields or {}).items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            .encode())
        chunks.append(f"{value}\r\n".encode())
    if file_field and artifact:
        data = Path(artifact).read_bytes()
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            f'Content-Disposition: form-data; name="{file_field}"; '
            f'filename="{Path(artifact).name}"\r\n'.encode())
        chunks.append(b"Content-Type: application/octet-stream\r\n\r\n")
        chunks.append(data + b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), boundary


def extract_url(body: str, pattern: str | None) -> str | None:
    text = body.strip()
    if pattern:
        m = re.search(pattern, text)
        return m.group(1) if m else None
    # Default shape: the whole body is the public URL.
    if text.startswith("http://") or text.startswith("https://"):
        return text.split()[0]
    return None


def execute(binding: dict, artifact: str | None, transport=None) -> dict:
    endpoint = binding.get("endpoint")
    if not endpoint:
        return {"status": "refused", "reason": "binding_missing_endpoint",
                "detail": "webform binding carries no endpoint"}
    body, boundary = build_multipart(binding.get("fields") or {},
                                     binding.get("file_field"),
                                     artifact)
    req = urllib.request.Request(endpoint, data=body, method="POST")
    req.add_header("Content-Type",
                   f"multipart/form-data; boundary={boundary}")
    open_fn = transport or urllib.request.urlopen
    try:
        with open_fn(req, timeout=60) as resp:
            text = resp.read().decode("utf-8", "replace")
            status = resp.status
    except Exception as exc:
        return {"status": "refused", "reason": "venue_post_failed",
                "detail": f"{type(exc).__name__}: {exc}"[:200]}
    if status >= 400:
        return {"status": "refused", "reason": f"venue_http_{status}",
                "detail": text[:200]}
    url = extract_url(text, binding.get("url_extract"))
    if not url:
        return {"status": "refused", "reason": "no_public_url_in_response",
                "detail": text[:200]}
    return {"status": "executed", "public_url": url,
            "detail": f"form POST {endpoint} -> {status}"}
