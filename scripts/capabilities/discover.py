#!/usr/bin/env python3
"""Metadata-first nested capability discovery and progressive search index."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

VERSION = "1.2"
MAX_SKILL_BYTES = 2_000_000
MAX_TOOL_CATALOG_BYTES = 20_000_000
SKILL_NAMES = {"SKILL.md", "SKILLS.md"}
SKILL_SUFFIXES = {".skills", ".skill"}
MANIFEST_NAMES = {"plugin.json", "marketplace.json", ".mcp.json", "mcp.json", "tools.json", "tool-manifest.json"}
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+._-]{1,}", re.I)
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
LONG_TOKEN_RE = re.compile(r"\b(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{20,}|AIza[0-9A-Za-z_-]{30,})\b")
SECRET_VALUE_RE = re.compile(r"""(?i)(["']?(?:api[_-]?key|token|password|secret|client[_-]?secret|access[_-]?token|refresh[_-]?token|private[_-]?key)["']?\s*[:=]\s*["'])([^"']{8,})(["'])""")
BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}")
SECRET_RE = re.compile(r"(?:\b(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{20,}|AIza[0-9A-Za-z_-]{30,})\b|(?:[\"']?(?:api[_-]?key|token|password|secret|client[_-]?secret|access[_-]?token|refresh[_-]?token|private[_-]?key)[\"']?\s*[:=]\s*[\"'][^\"']{8,}[\"'])|\bBearer\s+[A-Za-z0-9._~+/=-]{12,})",re.I)

def redact_sensitive(value: str) -> str:
    value = SECRET_VALUE_RE.sub(lambda match: match.group(1) + "[REDACTED]" + match.group(3), value)
    value = BEARER_RE.sub("Bearer [REDACTED]", value)
    return LONG_TOKEN_RE.sub("[REDACTED]", value)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def parse_frontmatter(text: str) -> dict:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result

def path_surface(path: Path, root: Path, external: bool = False) -> tuple[str, str]:
    parts = path.relative_to(root).as_posix().split("/")
    if external:
        return "workspace-external", "unverified"
    if "vendor" in parts:
        return "repo-vendor-skills", "unverified"
    if path.name.lower() in MANIFEST_NAMES or "plugins" in parts or ".claude-plugin" in parts or ".codex-plugin" in parts:
        return "repo-plugin-manifests", "repository-canonical"
    if parts[0] == ".agents":
        return "repo-agent-skills", "repository-canonical"
    if parts[0] == ".github":
        return "repo-github-skills", "repository-canonical"
    if parts[0] == ".claude":
        return "repo-claude-skills", "repository-canonical"
    return "repo-nested-skills", "repository-canonical"

def load_taxonomy() -> dict:
    candidate = Path(__file__).resolve().parents[2] / "ops" / "capability_discovery" / "taxonomy.json"
    if candidate.is_file():
        return json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError("ops/capability_discovery/taxonomy.json is required")

def taxonomy_hash(taxonomy: dict) -> str:
    return digest(json.dumps(taxonomy,sort_keys=True,separators=(",",":")).encode())

def validate_classification(domain: str, function: str, taxonomy: dict) -> tuple[str, str]:
    domains = taxonomy.get("domains", {})
    if domain not in domains or function not in domains[domain]:
        return "agentic", "capability-discovery"
    return domain, function

def infer_tags(name: str, description: str, locator: str, explicit: str = "") -> tuple[str, str, list[str]]:
    text = " ".join((name, description, locator, explicit)).lower()
    rules = [
        ("specialized", "finance", ("finance", "credit score", "banking", "investment", "portfolio", "brokerage", "stock market")),
        ("specialized", "health", ("health", "medical", "medication", "sleep", "fitness", "nutrition")),
        ("specialized", "legal", ("legal", "court", "litigation", "case law")),
        ("specialized", "regulatory", ("regulatory", "medtech", "fda", "compliance")),
        ("specialized", "scientific", ("genomic", "peptide", "molecular", "chemistry", "protein", "scientific")),
        ("specialized", "media", ("video", "audio", "speech", "media", "descript", "elevenlabs")),
        ("specialized", "property", ("property", "real estate", "idealista", "housing")),
        ("specialized", "automotive", ("automotive", "vehicle", "tesla", "car repair")),
        ("specialized", "outdoors", ("hiking", "trail", "offroad", "outdoors")),
        ("engineering", "code-generation", ("code", "coding", "refactor", "debug", "software", "developer")),
        ("testing", "testing", ("test", "qa", "benchmark", "evaluation", "validation")),
        ("delivery", "ci-cd", ("github action", "workflow", "deploy", "release", "ci/cd")),
        ("research", "vendor-discovery", ("research", "discover", "search", "catalog", "source")),
        ("data", "analytics", ("data", "database", "analytics", "sql", "observability")),
        ("agentic", "skill-discovery", ("skill", "agent", "tool", "mcp", "orchestrat", "context")),
        ("design", "product-design", ("design", "ux", "ui", "figma", "visual")),
        ("operations", "workflow-automation", ("ops", "automation", "schedule", "incident", "termux")),
    ]
    for domain, function, needles in rules:
        if any(needle in text for needle in needles):
            facets = ["skill"]
            if "vendor" in locator.split("/"):
                facets.append("vendor")
            if "mcp" in text or "tool" in text:
                facets.append("tool")
            if "workflow" in text or "action" in text:
                facets.append("workflow")
            return domain, function, sorted(set(facets))
    return "agentic", "capability-discovery", ["skill"]

def import_tool_taxonomy_jsonl(path: Path, root: Path, external: bool = False) -> list[dict]:
    """Import the legacy Termux tool catalogue as unverified metadata records."""
    if path.stat().st_size > MAX_TOOL_CATALOG_BYTES:
        return []
    raw_file = path.read_bytes()
    snapshot_sha = digest(raw_file)
    taxonomy = load_taxonomy()
    taxonomy_sha = taxonomy_hash(taxonomy)
    source_id = "workspace-external" if external else "termux-tool-taxonomy-snapshot"
    rows = []
    for line_number, raw_line in enumerate(raw_file.splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            item = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(item, dict) or not item.get("name"):
            continue
        raw_metadata = json.dumps(item, sort_keys=True, separators=(",", ":"))
        sensitive_scan_text = " ".join(
            f"{key} {value}" for key, value in item.items()
        )
        trust = "quarantined" if SECRET_RE.search(sensitive_scan_text) else "unverified"
        safe_name = redact_sensitive(str(item.get("name") or ""))
        safe_description = redact_sensitive(str(item.get("description") or ""))
        safe_package = redact_sensitive(str(item.get("package") or ""))
        safe_source = redact_sensitive(str(item.get("source") or ""))
        safe_category = redact_sensitive(str(item.get("category") or ""))
        raw_tags = item.get("tags", [])
        if not isinstance(raw_tags, list):
            raw_tags = []
        safe_tags = [redact_sensitive(str(tag)) for tag in raw_tags]
        relative = path.relative_to(root).as_posix()
        locator = (
            f"external:{root.name}/{relative}#L{line_number}"
            if external else f"{relative}#L{line_number}"
        )
        safe_locator = redact_sensitive(locator)
        explicit = " ".join([safe_category, safe_package, safe_source, *safe_tags])
        domain, function, facets = infer_tags(
            safe_name, safe_description, safe_locator, explicit
        )
        domain, function = validate_classification(domain, function, taxonomy)
        facets = [facet for facet in facets if facet != "skill"]
        facets.extend(["tool", "local"])
        if external:
            facets.append("external")
        identity = digest(
            f"{source_id}\0{safe_package}\0{safe_name}\0{safe_locator}".encode()
        )[:24]
        searchable = " ".join([
            safe_name, safe_description, safe_package, safe_source,
            safe_category, *safe_tags,
        ])
        rows.append({
            "id": f"{source_id}:{identity}",
            "kind": "tool",
            "source_id": source_id,
            "locator": safe_locator,
            "name": safe_name[:240],
            "description": safe_description[:1200],
            "content_sha256": digest(raw_line),
            "taxonomy_sha256": taxonomy_sha,
            "domain": domain,
            "function": function,
            "facets": sorted(set(facets)),
            "trust": trust,
            "lifecycle": "classified",
            "version_ref": snapshot_sha,
            "aliases": [],
            "permissions": [],
            "tags": sorted(set(TOKEN_RE.findall(
                (searchable + " " + safe_locator).lower()
            )))[:80],
        })
    return rows


def scan_repository(root: Path, external: bool = False) -> list[dict]:
    rows = []
    taxonomy = load_taxonomy()
    taxonomy_sha = taxonomy_hash(taxonomy)
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        is_skill_file = path.name in SKILL_NAMES or path.suffix.lower() in SKILL_SUFFIXES
        is_manifest_file = path.name.lower() in MANIFEST_NAMES
        is_tool_catalog = path.name == "all_tools.jsonl" and path.parent.name == "_TOOL_TAXONOMY"
        if is_tool_catalog:
            rows.extend(import_tool_taxonomy_jsonl(path, root, external=external))
            continue
        if not is_skill_file and not is_manifest_file:
            continue
        relative = path.relative_to(root).as_posix()
        locator = f"external:{root.name}/{relative}" if external else relative
        source_id, trust = path_surface(path, root, external)
        try:
            if path.suffix.lower() == ".skill":
                with zipfile.ZipFile(path) as archive:
                    members = [n for n in archive.namelist()
                               if Path(n).name == "SKILL.md" and not Path(n).is_absolute()
                               and ".." not in Path(n).parts]
                    if len(members) != 1:
                        continue
                    info = archive.getinfo(members[0])
                    if info.file_size > MAX_SKILL_BYTES:
                        continue
                    raw = archive.read(members[0])
            else:
                if path.stat().st_size > MAX_SKILL_BYTES:
                    continue
                raw = path.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError, zipfile.BadZipFile):
            continue
        manifest_data = {}
        frontmatter = {}
        if is_manifest_file:
            try:
                manifest_data = json.loads(text)
                if isinstance(manifest_data, list):
                    manifest_data = {"tools": manifest_data}
                if not isinstance(manifest_data, dict):
                    continue
            except json.JSONDecodeError:
                continue
            name = manifest_data.get("name") or manifest_data.get("id") or path.parent.name or path.stem
            description = str(manifest_data.get("description") or manifest_data.get("displayName") or "")
            mcp_servers = manifest_data.get("mcpServers", {})
            plugins = manifest_data.get("plugins", [])
            tools = manifest_data.get("tools", [])
            skills = manifest_data.get("skills", [])
            if isinstance(mcp_servers, dict):
                description += f"; MCP servers={len(mcp_servers)}"
            if isinstance(plugins, (list, dict)):
                description += f"; plugin entries={len(plugins)}"
            if isinstance(tools, (list, dict)):
                description += f"; tool entries={len(tools)}"
            if isinstance(skills, (list, dict)):
                description += f"; skill entries={len(skills)}"
            manifest_tags = " ".join(str(key) for key in manifest_data.keys())
        else:
            frontmatter = parse_frontmatter(text)
            heading = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), "")
            name = frontmatter.get("name") or heading or path.stem
            description = frontmatter.get("description") or ""
            manifest_tags = frontmatter.get("tags", "")
        if SECRET_RE.search(text):
            trust = "quarantined"
        safe_name = redact_sensitive(str(name))
        safe_description = redact_sensitive(str(description))
        safe_locator = redact_sensitive(str(locator))
        safe_manifest_tags = redact_sensitive(str(manifest_tags))
        domain, function, facets = infer_tags(safe_name, safe_description, safe_locator, safe_manifest_tags)
        domain, function = validate_classification(domain, function, taxonomy)
        if source_id == "repo-vendor-skills":
            facets.append("vendor")
        if source_id == "workspace-external":
            facets.append("external")
        if is_manifest_file:
            facets.append("plugin" if "plugin" in path.name.lower() or "marketplace" in path.name.lower() else "tool")
            facets.append("tool-manifest" if "mcp" in path.name.lower() or "tool" in path.name.lower() else "plugin-manifest")
        if path.name == "SKILLS.md" or path.suffix.lower() == ".skills":
            facets.append("index")
        kind = "manifest" if is_manifest_file else (
            "skill" if path.name == "SKILL.md" or path.suffix.lower() == ".skill" else "reference"
        )
        rows.append({
            "id": f"repo:{locator}",
            "kind": kind,
            "source_id": source_id, "locator": safe_locator, "name": safe_name[:240],
            "description": safe_description[:1200], "content_sha256": digest(raw),
            "taxonomy_sha256": taxonomy_sha,
            "domain": domain, "function": function, "facets": sorted(set(facets)),
            "trust": trust, "lifecycle": "classified",
            "version_ref": redact_sensitive(str(manifest_data.get("version") or "")) or None,
            "aliases": [], "permissions": [],
            "tags": sorted(set(TOKEN_RE.findall((safe_name + " " + safe_description + " " + safe_locator + " " + safe_manifest_tags).lower())))[:80]
        })
    return rows

def import_session_json(path: Path, kind: str) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    taxonomy = load_taxonomy()
    taxonomy_sha = taxonomy_hash(taxonomy)
    if kind == "plugin-skill":
        items = data.get("skills", data.get("plugin_skills", []))
        source_id = "session-plugin-skills"
    else:
        items = data.get("actions", data.get("tools", []))
        source_id = "session-tool-actions"
    rows = []
    for item in items:
        name = item.get("name") or item.get("uri") or item.get("id")
        if not name:
            continue
        description = item.get("activation_description") or item.get("summary") or item.get("description") or ""
        locator = item.get("uri") or item.get("name") or str(name)
        raw_metadata = str(name) + " " + str(description) + " " + str(locator)
        quarantined = bool(SECRET_RE.search(raw_metadata))
        safe_name = redact_sensitive(str(name))
        safe_description = redact_sensitive(str(description))
        safe_locator = redact_sensitive(str(locator))
        domain, function, facets = infer_tags(safe_name, safe_description, safe_locator)
        domain, function = validate_classification(domain, function, taxonomy)
        facets = [facet for facet in facets if facet != "skill"]
        facets.extend(["session", "plugin", "skill"] if kind == "plugin-skill" else ["tool"])
        if kind == "tool" and "mcp" in safe_name.lower():
            facets.append("mcp")
        fingerprint = digest((safe_name + "\0" + safe_description).encode())
        rows.append({
            "id": f"session:{kind}:{safe_name}", "kind": kind if kind == "plugin-skill" else "tool",
            "source_id": source_id, "locator": safe_locator, "name": safe_name[:240],
            "description": safe_description[:1200], "content_sha256": item.get("sha256") or fingerprint,
            "taxonomy_sha256": taxonomy_sha,
            "domain": domain, "function": function, "facets": sorted(set(facets)),
            "trust": "quarantined" if quarantined else "session-observed", "lifecycle": "discovered",
            "version_ref": data.get("snapshot", {}).get("captured_at"),
            "aliases": [], "permissions": [],
            "tags": sorted(set(TOKEN_RE.findall((safe_name + " " + safe_description).lower())))[:80]
        })
    return rows

def search_skills_sh(query: str, limit: int = 8, owner: str | None = None,
                     curated: bool = False) -> tuple[list[dict], str]:
    """Read-only skills.sh search. Requires a fresh Vercel OIDC token."""
    if len(query.strip()) < 2:
        return [], "query_too_short"
    if SECRET_RE.search(query):
        return [], "query_quarantined"
    safe_query = redact_sensitive(query)
    token = os.environ.get("VERCEL_OIDC_TOKEN")
    if not token:
        return [], "auth_required"
    if curated:
        endpoint = "https://skills.sh/api/v1/skills/curated"
        params = {}
    else:
        endpoint = "https://skills.sh/api/v1/skills/search"
        params = {"q": query, "limit": max(1, min(limit, 200))}
        if owner:
            params["owner"] = owner
    request = urllib.request.Request(
        endpoint + (("?" + urllib.parse.urlencode(params)) if params else ""),
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return [], f"http_{exc.code}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return [], "unavailable"

    if curated:
        items = []
        for publisher in payload.get("data", []):
            for skill in publisher.get("skills", []):
                items.append({**skill, "_curated_owner": publisher.get("owner", "")})
        terms = set(TOKEN_RE.findall(query.lower()))
        items = [item for item in items
                 if terms.intersection(TOKEN_RE.findall(
                     " ".join(str(item.get(key, "")) for key in ("id", "name", "source", "_curated_owner")).lower()
                 ))]
        items.sort(key=lambda item: item.get("installs", 0), reverse=True)
        search_type = "curated"
    else:
        items = payload.get("data", [])
        search_type = payload.get("searchType", "unknown")

    taxonomy_sha = taxonomy_hash(load_taxonomy())
    rows = []
    for item in items[:limit]:
        identity = item.get("id")
        if not identity:
            continue
        raw_name = item.get("name") or item.get("slug") or identity
        raw_source = item.get("source") or item.get("_curated_owner") or ""
        raw_detail_url = item.get("url") or ""
        raw_install_url = item.get("installUrl") or ""
        raw_metadata = json.dumps(item, sort_keys=True, separators=(",", ":"))
        sensitive_scan_text = " ".join(
            f"{key} {value}" for key, value in item.items()
        )
        quarantined = bool(SECRET_RE.search(sensitive_scan_text))
        safe_identity = redact_sensitive(str(identity))
        name = redact_sensitive(str(raw_name))
        source = redact_sensitive(str(raw_source))
        detail_url = redact_sensitive(str(raw_detail_url))
        install_url = redact_sensitive(str(raw_install_url))
        installs = item.get("installs")
        duplicate = bool(item.get("isDuplicate", False))
        description = redact_sensitive(
            f"skills.sh candidate; source={source}; installs={installs}; "
            f"duplicate={duplicate}; searchType={search_type}; "
            f"url={detail_url}; install={install_url}"
        )
        metadata = raw_metadata.encode()
        rows.append({
            "id": "skills-sh:" + safe_identity,
            "kind": "skill",
            "source_id": "skills-sh",
            "locator": detail_url or safe_identity,
            "name": str(name)[:240],
            "description": description[:1200],
            "content_sha256": digest(metadata),
            "taxonomy_sha256": taxonomy_sha,
            "domain": "agentic",
            "function": "skill-discovery",
            "facets": ["external", "skill", "vendor" if source else "community"],
            "trust": "quarantined" if quarantined else "community-reference",
            "lifecycle": "discovered",
            "version_ref": redact_sensitive(str(item.get("hash") or "")) or None,
            "aliases": [],
            "permissions": [],
            "tags": sorted(set(TOKEN_RE.findall((safe_query + " " + name + " " + source).lower())))[:80],
        })
    return rows, "ok"

def connect(db: Path) -> sqlite3.Connection:
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE IF NOT EXISTS capability (
      id TEXT PRIMARY KEY, kind TEXT NOT NULL, source_id TEXT NOT NULL,
      locator TEXT NOT NULL, name TEXT NOT NULL, description TEXT NOT NULL,
      content_sha256 TEXT, domain TEXT NOT NULL, function TEXT NOT NULL,
      facets TEXT NOT NULL, trust TEXT NOT NULL, lifecycle TEXT NOT NULL,
      version_ref TEXT, taxonomy_sha256 TEXT, record_sha256 TEXT,
      aliases TEXT NOT NULL DEFAULT '[]', permissions TEXT NOT NULL DEFAULT '[]',
      tags TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    capability_columns = {row[1] for row in con.execute("PRAGMA table_info(capability)")}
    for column, declaration in (("taxonomy_sha256","TEXT"),("aliases","TEXT NOT NULL DEFAULT '[]'"),("permissions","TEXT NOT NULL DEFAULT '[]'")):
        if column not in capability_columns:
            con.execute(f"ALTER TABLE capability ADD COLUMN {column} {declaration}")
    try:
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS capability_fts USING fts5(id UNINDEXED,name,description,tags,tokenize='unicode61')")
    except sqlite3.OperationalError:
        con.execute("CREATE TABLE IF NOT EXISTS capability_fts (id TEXT PRIMARY KEY,name TEXT,description TEXT,tags TEXT)")
    con.execute("""CREATE TABLE IF NOT EXISTS discovery_event (
      event_id TEXT PRIMARY KEY, capability_id TEXT NOT NULL, event TEXT NOT NULL,
      content_sha256 TEXT, taxonomy_sha256 TEXT, record_sha256 TEXT, source_id TEXT NOT NULL,
      recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    event_columns = {row[1] for row in con.execute("PRAGMA table_info(discovery_event)")}
    for column in ("taxonomy_sha256","record_sha256"):
        if column not in event_columns:
            con.execute(f"ALTER TABLE discovery_event ADD COLUMN {column} TEXT")
    con.execute("""CREATE TABLE IF NOT EXISTS capability_edge (
      edge_id TEXT PRIMARY KEY, from_id TEXT NOT NULL, to_id TEXT NOT NULL,
      relation TEXT NOT NULL, evidence_sha256 TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(from_id,to_id,relation)
    )""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_capability_domain ON capability(domain,function)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_capability_trust ON capability(trust,lifecycle)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_capability_edge_from ON capability_edge(from_id,relation)")
    con.execute("""CREATE TABLE IF NOT EXISTS catalog_cache (
      cache_key TEXT PRIMARY KEY, source TEXT NOT NULL, payload TEXT NOT NULL,
      expires_at REAL NOT NULL, cached_at REAL NOT NULL
    )""")
    return con

def cached_skills_sh_search(con: sqlite3.Connection, query: str, limit: int = 8,
                               owner: str | None = None, curated: bool = False) -> tuple[list[dict], str]:
    normalized = " ".join(query.lower().split())
    cache_key = digest(json.dumps(
        [normalized,limit,owner,curated],separators=(",",":")
    ).encode())
    cached = con.execute(
        "SELECT payload,expires_at FROM catalog_cache WHERE cache_key=?",
        (cache_key,),
    ).fetchone()
    now = time.time()
    if cached and cached[1] > now:
        return json.loads(cached[0]), "cached"
    rows,status = search_skills_sh(query,limit,owner=owner,curated=curated)
    if status == "ok":
        ttl = 300 if curated else 45
        con.execute("""INSERT INTO catalog_cache(cache_key,source,payload,expires_at,cached_at)
            VALUES (?,?,?,?,?) ON CONFLICT(cache_key) DO UPDATE SET
            source=excluded.source,payload=excluded.payload,
            expires_at=excluded.expires_at,cached_at=excluded.cached_at""",
            (cache_key,"skills.sh:curated" if curated else "skills.sh:search",
             json.dumps(rows,separators=(",",":")),now+ttl,now))
        con.commit()
    return rows,status

def upsert(con: sqlite3.Connection, rows: list[dict]) -> dict:
    changed = 0
    for row in rows:
        record_state = {key:row.get(key) for key in (
            "kind","source_id","locator","name","description","taxonomy_sha256",
            "domain","function","facets","trust","lifecycle","version_ref","aliases","permissions","tags"
        )}
        record_sha = digest(json.dumps(record_state,sort_keys=True,separators=(",",":")).encode())
        old = con.execute("SELECT content_sha256,record_sha256 FROM capability WHERE id=?", (row["id"],)).fetchone()
        event = "added" if old is None else (
            "changed" if old[0] != row["content_sha256"] else
            ("reclassified" if old[1] != record_sha else "seen")
        )
        con.execute("""INSERT INTO capability
          (id,kind,source_id,locator,name,description,content_sha256,domain,function,facets,trust,lifecycle,version_ref,taxonomy_sha256,record_sha256,aliases,permissions,tags)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
          ON CONFLICT(id) DO UPDATE SET kind=excluded.kind,source_id=excluded.source_id,
          locator=excluded.locator,name=excluded.name,description=excluded.description,
          content_sha256=excluded.content_sha256,domain=excluded.domain,function=excluded.function,
          facets=excluded.facets,trust=excluded.trust,lifecycle=excluded.lifecycle,
          version_ref=excluded.version_ref,taxonomy_sha256=excluded.taxonomy_sha256,
          record_sha256=excluded.record_sha256,aliases=excluded.aliases,permissions=excluded.permissions,
          tags=excluded.tags,updated_at=CURRENT_TIMESTAMP""",
          (row["id"],row["kind"],row["source_id"],row["locator"],row["name"],row["description"],
           row["content_sha256"],row["domain"],row["function"],json.dumps(row["facets"]),
           row["trust"],row["lifecycle"],row["version_ref"],row.get("taxonomy_sha256"),record_sha,
           json.dumps(row.get("aliases",[])),json.dumps(row.get("permissions",[]))," ".join(row["tags"])))
        con.execute("DELETE FROM capability_fts WHERE id=?", (row["id"],))
        con.execute("INSERT INTO capability_fts(id,name,description,tags) VALUES (?,?,?,?)",
                    (row["id"],row["name"],row["description"]," ".join(row["tags"])))
        if event != "seen":
            event_id = digest(f"{row['id']}|{event}|{row['content_sha256']}|{record_sha}".encode())
            con.execute("INSERT OR IGNORE INTO discovery_event(event_id,capability_id,event,content_sha256,taxonomy_sha256,record_sha256,source_id) VALUES (?,?,?,?,?,?,?)",
                        (event_id,row["id"],event,row["content_sha256"],row.get("taxonomy_sha256"),record_sha,row["source_id"]))
            changed += 1
    duplicates = con.execute("""SELECT a.id,b.id,a.content_sha256
        FROM capability a JOIN capability b
        ON a.content_sha256=b.content_sha256 AND a.id < b.id
        WHERE a.content_sha256 IS NOT NULL""").fetchall()
    expected_edges = {}
    for left,right,fingerprint in duplicates:
        edge_id = digest(f"{left}|{right}|content_identical|{fingerprint}".encode())
        expected_edges[edge_id] = (left,right,fingerprint)
    existing_edges = {row[0] for row in con.execute(
        "SELECT edge_id FROM capability_edge WHERE relation='content_identical'").fetchall()}
    for stale_edge in existing_edges - set(expected_edges):
        con.execute("DELETE FROM capability_edge WHERE edge_id=?", (stale_edge,))
    for edge_id,(left,right,fingerprint) in expected_edges.items():
        con.execute("""INSERT OR IGNORE INTO capability_edge
            (edge_id,from_id,to_id,relation,evidence_sha256) VALUES (?,?,?,?,?)""",
            (edge_id,left,right,"content_identical",fingerprint))
    con.commit()
    return {"scanned":len(rows),"changed":changed,
            "relationships":con.execute("SELECT count(*) FROM capability_edge").fetchone()[0],
            "total":con.execute("SELECT count(*) FROM capability").fetchone()[0]}

def search(con: sqlite3.Connection, query: str, limit: int = 8,
           include_quarantined: bool = False) -> list[dict]:
    terms = [term for term in TOKEN_RE.findall(query.lower()) if len(term) > 1]
    if not terms:
        return []
    match = " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)
    columns = """c.id,c.kind,c.source_id,c.name,c.description,c.locator,c.domain,c.function,
        c.facets,c.trust,c.lifecycle,c.version_ref,c.aliases,c.permissions,c.tags,
        c.content_sha256,c.taxonomy_sha256,c.record_sha256"""
    try:
        hits = con.execute(f"""SELECT {columns},bm25(capability_fts) AS rank
          FROM capability_fts f JOIN capability c ON c.id=f.id WHERE capability_fts MATCH ?
          AND (? OR c.trust != 'quarantined') ORDER BY rank LIMIT ?""",
          (match,1 if include_quarantined else 0,limit)).fetchall()
    except sqlite3.OperationalError:
        pattern = "%" + terms[0] + "%"
        hits = con.execute("""SELECT id,kind,source_id,name,description,locator,domain,function,
          facets,trust,lifecycle,version_ref,aliases,permissions,tags,
          content_sha256,taxonomy_sha256,record_sha256,0
          FROM capability WHERE (name LIKE ? OR description LIKE ? OR tags LIKE ?)
          AND (? OR trust != 'quarantined') LIMIT ?""",
          (pattern,pattern,pattern,1 if include_quarantined else 0,limit)).fetchall()
    fields = ["id","kind","source_id","name","description","locator","domain","function",
              "facets","trust","lifecycle","version_ref","aliases","permissions","tags",
              "content_sha256","taxonomy_sha256","record_sha256","rank"]
    results = []
    for row in hits:
        item = dict(zip(fields,row))
        for key in ("facets","aliases","permissions"):
            try:
                item[key] = json.loads(item[key] or "[]")
            except (TypeError,json.JSONDecodeError):
                item[key] = []
        item["tags"] = (item["tags"] or "").split()
        results.append(item)
    return results

def export_ledger(con: sqlite3.Connection, path: Path) -> int:
    path.parent.mkdir(parents=True,exist_ok=True)
    rows = con.execute("""SELECT event_id,capability_id,event,content_sha256,taxonomy_sha256,record_sha256,source_id,recorded_at
                          FROM discovery_event ORDER BY recorded_at,event_id""").fetchall()
    with path.open("w",encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(dict(zip(("event_id","capability_id","event","content_sha256","taxonomy_sha256","record_sha256","source_id","recorded_at"),row)),sort_keys=True)+"\n")
    return len(rows)

def local_first_search(con: sqlite3.Connection, query: str, limit: int = 8,
                      min_local_results: int = 5, owner: str | None = None,
                      ledger: Path = Path(".cache/capability-discovery-ledger.jsonl"),
                      include_quarantined: bool = False) -> tuple[list[dict], str]:
    """Search local metadata first; call read-only skills.sh only when coverage is thin."""
    hits = search(con,query,limit,include_quarantined)
    if len(hits) >= min_local_results:
        return hits,"local_sufficient"
    remote_rows,status = cached_skills_sh_search(con,query,limit,owner=owner)
    if remote_rows:
        upsert(con,remote_rows)
        export_ledger(con,ledger)
    return search(con,query,limit,include_quarantined),status

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command",required=True)
    scan = sub.add_parser("scan",help="Index local skills and optional session metadata exports")
    scan.add_argument("--root",default=".")
    scan.add_argument("--extra-root",action="append",default=[],help="Explicit additional workspace root; repeat to add more")
    scan.add_argument("--db",default=".cache/capability-index.sqlite")
    scan.add_argument("--ledger",default=".cache/capability-discovery-ledger.jsonl")
    scan.add_argument("--plugin-skills-json")
    scan.add_argument("--tool-actions-json")
    find = sub.add_parser("find",help="Search metadata only; hydrate full source after selection")
    find.add_argument("query")
    find.add_argument("--db",default=".cache/capability-index.sqlite")
    find.add_argument("--ledger",default=".cache/capability-discovery-ledger.jsonl")
    find.add_argument("--limit",type=int,default=8)
    catalog_group = find.add_mutually_exclusive_group()
    catalog_group.add_argument("--auto",action="store_true",help="Local-first; use read-only skills.sh search only when local coverage is thin and a token is available")
    catalog_group.add_argument("--skills-sh",action="store_true",help="Add read-only skills.sh search; requires VERCEL_OIDC_TOKEN")
    catalog_group.add_argument("--skills-sh-curated",action="store_true",help="Search the official curated skills.sh catalog; requires VERCEL_OIDC_TOKEN")
    find.add_argument("--min-local-results",type=int,default=5)
    find.add_argument("--include-quarantined",action="store_true",help="Include secret-like quarantined candidates for forensic review")
    find.add_argument("--owner",help="Limit skills.sh search to a GitHub owner")
    args = parser.parse_args()
    if args.command == "scan":
        root = Path(args.root).resolve()
        rows = scan_repository(root)
        seen_roots = {root}
        for raw_root in args.extra_root:
            extra_root = Path(raw_root).expanduser().resolve()
            if extra_root.is_dir() and extra_root not in seen_roots:
                rows.extend(scan_repository(extra_root, external=True))
                seen_roots.add(extra_root)
        if args.plugin_skills_json:
            rows.extend(import_session_json(Path(args.plugin_skills_json),"plugin-skill"))
        if args.tool_actions_json:
            rows.extend(import_session_json(Path(args.tool_actions_json),"tool"))
        con = connect(Path(args.db))
        result = upsert(con,rows)
        result["ledger_events"] = export_ledger(con,Path(args.ledger))
        print(json.dumps({"version":VERSION,**result},sort_keys=True))
        return 0
    con = connect(Path(args.db))
    external_status = "not_requested"
    if args.auto:
        hits,external_status = local_first_search(
            con,args.query,args.limit,args.min_local_results,args.owner,Path(args.ledger),
            args.include_quarantined
        )
    else:
        if args.skills_sh or args.skills_sh_curated:
            remote_rows,external_status = cached_skills_sh_search(
                con,args.query,args.limit,owner=args.owner,curated=args.skills_sh_curated
            )
            if remote_rows:
                upsert(con,remote_rows)
                export_ledger(con,Path(args.ledger))
        hits = search(con,args.query,args.limit,args.include_quarantined)
    print(json.dumps({"query":args.query,"count":len(hits),"external_skills_sh":external_status,"results":hits},ensure_ascii=False,sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
