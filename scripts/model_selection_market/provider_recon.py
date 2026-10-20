"""MSM-006: deterministic, provenance-pinned third-party provider research ingestion.

This module only catalogs upstream claims. It does not contact provider endpoints,
execute upstream source, or make any provider runtime-eligible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "msm-provider-recon-v1"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 15
REPOS = {
    "mnfst/awesome-free-llm-apis": {"license": "UNVERIFIED_UPSTREAM_LICENSE", "files": ("data.json",)},
    "tashfeenahmed/freellmapi": {"license": "UNVERIFIED_UPSTREAM_LICENSE", "files": ("package.json", "server/src/providers/index.ts")},
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

class ReconError(ValueError):
    """Fail-closed input, transport, or schema error."""


def fetch_bytes(url: str) -> bytes:
    """Fetch fixed GitHub HTTPS URLs, rejecting redirects away from GitHub."""
    from urllib.parse import urlsplit
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in {"api.github.com", "raw.githubusercontent.com"} or parsed.username or parsed.password:
        raise ReconError("refusing non-allowlisted URL")
    headers = {"User-Agent": "msm-provider-recon/1", "Accept": "application/vnd.github+json"}
    metadata_urls = {f"https://api.github.com/repos/{repo}/commits/HEAD" for repo in REPOS}
    token = os.environ.get("PROVIDER_RECON_GITHUB_TOKEN", "")
    if token and url in metadata_urls:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", token):
            raise ReconError("invalid GitHub metadata credential format")
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            final = urlsplit(response.geturl())
            if final.scheme != "https" or final.hostname != parsed.hostname:
                raise ReconError("unexpected final URL")
            payload = response.read(MAX_RESPONSE_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ReconError(f"fetch failed: {exc}") from exc
    if len(payload) > MAX_RESPONSE_BYTES:
        raise ReconError("response exceeds size limit")
    return payload

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ReconError("redirects are not permitted")


def _json(data: bytes, label: str) -> Any:
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReconError(f"malformed JSON in {label}") from exc


def _pinned(repo: str, sha: str, path: str) -> tuple[str, bytes]:
    url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
    return url, fetch_bytes(url)


def _claims_mnfst(doc: Any) -> list[dict[str, Any]]:
    if not isinstance(doc, dict) or not isinstance(doc.get("providers"), list):
        raise ReconError("mnfst data.json missing providers array")
    rows, seen = [], set()
    for provider in doc["providers"]:
        if not isinstance(provider, dict) or not isinstance(provider.get("name"), str) or not provider["name"].strip() or not isinstance(provider.get("models"), list):
            raise ReconError("invalid mnfst provider row")
        pkey = _key(provider["name"])
        for model in provider["models"]:
            if not isinstance(model, dict):
                raise ReconError("invalid mnfst model row")
            # Upstream uses null IDs for explicitly aggregated “N more models”
            # entries. Retain those directory claims with a stable synthetic key.
            model_id = model.get("id")
            if model_id is None and isinstance(model.get("name"), str) and model["name"].strip():
                model_id = "aggregate:" + model["name"].strip()
            if not isinstance(model_id, str) or not model_id.strip():
                raise ReconError("invalid mnfst model row")
            mkey = _key(model_id)
            key = (pkey, mkey)
            if key in seen: raise ReconError(f"duplicate candidate {key}")
            seen.add(key)
            rows.append({"provider_key": pkey, "provider_name": provider["name"], "model_key": mkey, "model_id": model_id, "model_name": model.get("name", model_id), "claims": {"context": model.get("context"), "modality": model.get("modality"), "quota": model.get("rateLimit"), "max_output": model.get("maxOutput")}, "evidence_class": "THIRD_PARTY_CLAIM", "runtime_eligible": False, "quota_remaining": None, "blocked_reasons": ["third-party unverified claim", "no runtime eligibility evidence"]})
    return rows


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _claims_freellmapi(package: Any, source: str) -> list[dict[str, Any]]:
    if not isinstance(package, dict) or not isinstance(package.get("name"), str):
        raise ReconError("malformed freellmapi package.json")
    # Extract only syntactic provider class references: import declarations and
    # register(new XProvider()) calls. Never interpret/evaluate TypeScript.
    imports = re.findall(r"^import\s*\{\s*([A-Za-z_$][\w$]*Provider)\s*\}\s*from\s*['\"]([^'\"]+)['\"]\s*;?\s*$", source, re.M)
    registrations = set(re.findall(r"register\(new\s+([A-Za-z_$][\w$]*Provider)\(\)\)\s*;", source))
    paths = {klass: path for klass, path in imports}
    if not registrations or not registrations.issubset(paths):
        raise ReconError("provider index references do not match safe import/register pattern")
    rows = []
    for klass in sorted(registrations):
        name = klass[:-8]
        pkey = _key(name)
        rows.append({"provider_key": pkey, "provider_name": name, "model_key": "provider-catalog", "model_name": "provider catalog reference", "claims": {"context": None, "modality": None, "quota": None, "max_output": None}, "evidence_class": "THIRD_PARTY_CLAIM", "runtime_eligible": False, "quota_remaining": None, "blocked_reasons": ["source reference only; no model/quota verification", "third-party unverified claim"]})
    return rows


def build_snapshot(fetcher=fetch_bytes) -> dict[str, Any]:
    """Build a fully validated snapshot; injected fetcher supports offline tests."""
    sources, candidates = [], []
    for repo, config in REPOS.items():
        commit_url = f"https://api.github.com/repos/{repo}/commits/HEAD"
        commit_doc = _json(fetcher(commit_url), commit_url)
        sha = commit_doc.get("sha") if isinstance(commit_doc, dict) else None
        if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            raise ReconError(f"invalid full commit SHA for {repo}")
        source_files = {}
        raw = {}
        for path in config["files"]:
            url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
            data = fetcher(url)
            source_files[path] = {"url": url, "sha256": hashlib.sha256(data).hexdigest()}
            raw[path] = data
        sources.append({"repo": repo, "commit_sha": sha, "license_designation": config["license"], "files": source_files})
        if repo.startswith("mnfst/"):
            rows = _claims_mnfst(_json(raw["data.json"], "data.json"))
            candidates.extend({**row, "source_repo": repo} for row in rows)
        else:
            package = _json(raw["package.json"], "package.json")
            try: source = raw["server/src/providers/index.ts"].decode("utf-8")
            except UnicodeDecodeError as exc: raise ReconError("invalid provider index encoding") from exc
            rows = _claims_freellmapi(package, source)
            candidates.extend({**row, "source_repo": repo} for row in rows)
    candidates.sort(key=lambda x: (x["provider_key"], x["model_key"]))
    return {"schema_version": SCHEMA_VERSION, "sources": sources, "model_candidates": candidates, "integration_references": [{"source_repo": "tashfeenahmed/freellmapi", "path": "server/src/providers/index.ts", "kind": "static provider import/register references only", "count": sum(1 for c in candidates if c["model_key"] == "provider-catalog")}], "blocked_reasons": ["catalog data is unverified third-party research", "provider endpoints are never queried", "runtime eligibility is always false"]}


def write_snapshot(path: str | os.PathLike[str], snapshot: dict[str, Any]) -> None:
    """Atomically replace output only after complete snapshot construction."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(snapshot, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=target.parent, prefix=f".{target.name}.", delete=False) as f:
            temp_name = f.name
            f.write(payload); f.flush(); os.fsync(f.fileno())
        os.replace(temp_name, target)
    finally:
        if temp_name and os.path.exists(temp_name): os.unlink(temp_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="destination JSON snapshot")
    args = parser.parse_args(argv)
    try:
        snapshot = build_snapshot()
        write_snapshot(args.output, snapshot)
    except Exception as exc:
        parser.exit(2, f"provider recon failed; output not written: {exc}\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
