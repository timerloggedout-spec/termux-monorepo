#!/usr/bin/env python3
"""Metadata-first nested capability discovery and progressive search index."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

VERSION = "1.1"
MAX_SKILL_BYTES = 2_000_000
SKILL_NAMES = {"SKILL.md", "SKILLS.md"}
SKILL_SUFFIXES = {".skills", ".skill"}
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+._-]{1,}", re.I)
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
SECRET_RE = re.compile(r"(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|(?i:api[_-]?key|token|password|secret)\s*[:=]\s*['\"][^'\"]{12,}['\"])")

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

def path_surface(path: Path, root: Path) -> tuple[str, str]:
    parts = path.relative_to(root).as_posix().split("/")
    if parts[0] == ".agents":
        return "repo-agent-skills", "repository-canonical"
    if parts[0] == ".github":
        return "repo-github-skills", "repository-canonical"
    if parts[0] == ".claude":
        return "repo-claude-skills", "repository-canonical"
    if "vendor" in parts:
        return "repo-vendor-skills", "unverified"
    return "repo-nested-skills", "repository-canonical"

def infer_tags(name: str, description: str, locator: str, explicit: str = "") -> tuple[str, str, list[str]]:
    text = " ".join((name, description, locator, explicit)).lower()
    rules = [
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

def scan_repository(root: Path) -> list[dict]:
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name not in SKILL_NAMES and path.suffix.lower() not in SKILL_SUFFIXES:
            continue
        locator = path.relative_to(root).as_posix()
        source_id, trust = path_surface(path, root)
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
        frontmatter = parse_frontmatter(text)
        heading = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), "")
        name = frontmatter.get("name") or heading or path.stem
        description = frontmatter.get("description") or ""
        if SECRET_RE.search(text):
            trust = "quarantined"
        domain, function, facets = infer_tags(name, description, locator, frontmatter.get("tags", ""))
        if source_id == "repo-vendor-skills":
            facets.append("vendor")
        if path.name == "SKILLS.md" or path.suffix.lower() == ".skills":
            facets.append("index")
        rows.append({
            "id": f"repo:{locator}",
            "kind": "skill" if path.name == "SKILL.md" or path.suffix.lower() == ".skill" else "reference",
            "source_id": source_id, "locator": locator, "name": name[:240],
            "description": description[:1200], "content_sha256": digest(raw),
            "domain": domain, "function": function, "facets": sorted(set(facets)),
            "trust": trust, "lifecycle": "classified", "version_ref": None,
            "aliases": [], "permissions": [],
            "tags": sorted(set(TOKEN_RE.findall((name + " " + description + " " + locator).lower())))[:80]
        })
    return rows

def import_session_json(path: Path, kind: str) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
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
        domain, function, facets = infer_tags(str(name), str(description), str(locator))
        facets.extend(["session", "plugin" if kind == "plugin-skill" else "tool"])
        fingerprint = digest((str(name) + "\0" + str(description)).encode())
        rows.append({
            "id": f"session:{kind}:{name}", "kind": kind if kind == "plugin-skill" else "tool",
            "source_id": source_id, "locator": str(locator), "name": str(name)[:240],
            "description": str(description)[:1200], "content_sha256": item.get("sha256") or fingerprint,
            "domain": domain, "function": function, "facets": sorted(set(facets)),
            "trust": "session-observed", "lifecycle": "discovered",
            "version_ref": data.get("snapshot", {}).get("captured_at"),
            "aliases": [], "permissions": [],
            "tags": sorted(set(TOKEN_RE.findall((str(name) + " " + str(description)).lower())))[:80]
        })
    return rows

def search_skills_sh(query: str, limit: int = 8) -> tuple[list[dict], str]:
    """Read-only skills.sh search. Requires a request-scoped Vercel OIDC token."""
    token = os.environ.get("VERCEL_OIDC_TOKEN")
    if not token:
        return [], "auth_required"
    params = urllib.parse.urlencode({"q": query, "limit": max(1, min(limit, 200))})
    request = urllib.request.Request(
        "https://skills.sh/api/v1/skills/search?" + params,
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return [], f"http_{exc.code}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return [], "unavailable"
    rows = []
    for item in payload.get("data", []):
        identity = item.get("id")
        if not identity:
            continue
        name = item.get("name") or item.get("slug") or identity
        source = item.get("source") or ""
        installs = item.get("installs")
        duplicate = bool(item.get("isDuplicate", False))
        description = f"skills.sh candidate; source={source}; installs={installs}; duplicate={duplicate}"
        metadata = json.dumps(item, sort_keys=True, separators=(",", ":")).encode()
        rows.append({
            "id": "skills-sh:" + identity,
            "kind": "skill",
            "source_id": "skills-sh",
            "locator": identity,
            "name": str(name)[:240],
            "description": description[:1200],
            "content_sha256": digest(metadata),
            "domain": "agentic",
            "function": "skill-discovery",
            "facets": ["external", "skill", "vendor" if source else "community"],
            "trust": "community-reference",
            "lifecycle": "discovered",
            "version_ref": item.get("hash"),
            "aliases": [],
            "permissions": [],
            "tags": sorted(set(TOKEN_RE.findall((query + " " + str(name) + " " + source).lower())))[:80],
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
      version_ref TEXT, tags TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    try:
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS capability_fts USING fts5(id UNINDEXED,name,description,tags,tokenize='unicode61')")
    except sqlite3.OperationalError:
        con.execute("CREATE TABLE IF NOT EXISTS capability_fts (id TEXT PRIMARY KEY,name TEXT,description TEXT,tags TEXT)")
    con.execute("""CREATE TABLE IF NOT EXISTS discovery_event (
      event_id TEXT PRIMARY KEY, capability_id TEXT NOT NULL, event TEXT NOT NULL,
      content_sha256 TEXT, source_id TEXT NOT NULL, recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS capability_edge (
      edge_id TEXT PRIMARY KEY, from_id TEXT NOT NULL, to_id TEXT NOT NULL,
      relation TEXT NOT NULL, evidence_sha256 TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(from_id,to_id,relation)
    )""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_capability_domain ON capability(domain,function)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_capability_trust ON capability(trust,lifecycle)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_capability_edge_from ON capability_edge(from_id,relation)")
    return con

def upsert(con: sqlite3.Connection, rows: list[dict]) -> dict:
    changed = 0
    for row in rows:
        old = con.execute("SELECT content_sha256 FROM capability WHERE id=?", (row["id"],)).fetchone()
        event = "added" if old is None else ("changed" if old[0] != row["content_sha256"] else "seen")
        con.execute("""INSERT INTO capability
          (id,kind,source_id,locator,name,description,content_sha256,domain,function,facets,trust,lifecycle,version_ref,tags)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
          ON CONFLICT(id) DO UPDATE SET kind=excluded.kind,source_id=excluded.source_id,
          locator=excluded.locator,name=excluded.name,description=excluded.description,
          content_sha256=excluded.content_sha256,domain=excluded.domain,function=excluded.function,
          facets=excluded.facets,trust=excluded.trust,lifecycle=excluded.lifecycle,
          version_ref=excluded.version_ref,tags=excluded.tags,updated_at=CURRENT_TIMESTAMP""",
          (row["id"],row["kind"],row["source_id"],row["locator"],row["name"],row["description"],
           row["content_sha256"],row["domain"],row["function"],json.dumps(row["facets"]),
           row["trust"],row["lifecycle"],row["version_ref"]," ".join(row["tags"])))
        con.execute("DELETE FROM capability_fts WHERE id=?", (row["id"],))
        con.execute("INSERT INTO capability_fts(id,name,description,tags) VALUES (?,?,?,?)",
                    (row["id"],row["name"],row["description"]," ".join(row["tags"])))
        if event != "seen":
            event_id = digest(f"{row['id']}|{event}|{row['content_sha256']}".encode())
            con.execute("INSERT OR IGNORE INTO discovery_event(event_id,capability_id,event,content_sha256,source_id) VALUES (?,?,?,?,?)",
                        (event_id,row["id"],event,row["content_sha256"],row["source_id"]))
            changed += 1
    con.execute("DELETE FROM capability_edge WHERE relation='content_identical'")
    duplicates = con.execute("""SELECT a.id,b.id,a.content_sha256
        FROM capability a JOIN capability b
        ON a.content_sha256=b.content_sha256 AND a.id < b.id
        WHERE a.content_sha256 IS NOT NULL""").fetchall()
    for left,right,fingerprint in duplicates:
        edge_id = digest(f"{left}|{right}|content_identical|{fingerprint}".encode())
        con.execute("""INSERT OR IGNORE INTO capability_edge
            (edge_id,from_id,to_id,relation,evidence_sha256) VALUES (?,?,?,?,?)""",
            (edge_id,left,right,"content_identical",fingerprint))
    con.commit()
    return {"scanned":len(rows),"changed":changed,
            "relationships":con.execute("SELECT count(*) FROM capability_edge").fetchone()[0],
            "total":con.execute("SELECT count(*) FROM capability").fetchone()[0]}

def search(con: sqlite3.Connection, query: str, limit: int = 8) -> list[dict]:
    terms = [term for term in TOKEN_RE.findall(query.lower()) if len(term) > 1]
    if not terms:
        return []
    match = " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)
    try:
        hits = con.execute("""SELECT c.id,c.kind,c.name,c.description,c.locator,c.domain,c.function,c.trust,c.lifecycle,bm25(capability_fts) AS rank
          FROM capability_fts f JOIN capability c ON c.id=f.id WHERE capability_fts MATCH ?
          ORDER BY rank LIMIT ?""", (match,limit)).fetchall()
    except sqlite3.OperationalError:
        pattern = "%" + terms[0] + "%"
        hits = con.execute("""SELECT id,kind,name,description,locator,domain,function,trust,lifecycle,0
          FROM capability WHERE name LIKE ? OR description LIKE ? OR tags LIKE ? LIMIT ?""",
          (pattern,pattern,pattern,limit)).fetchall()
    fields = ["id","kind","name","description","locator","domain","function","trust","lifecycle","rank"]
    return [dict(zip(fields,row)) for row in hits]

def export_ledger(con: sqlite3.Connection, path: Path) -> int:
    path.parent.mkdir(parents=True,exist_ok=True)
    rows = con.execute("""SELECT event_id,capability_id,event,content_sha256,source_id,recorded_at
                          FROM discovery_event ORDER BY recorded_at,event_id""").fetchall()
    with path.open("w",encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(dict(zip(("event_id","capability_id","event","content_sha256","source_id","recorded_at"),row)),sort_keys=True)+"\n")
    return len(rows)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command",required=True)
    scan = sub.add_parser("scan",help="Index local skills and optional session metadata exports")
    scan.add_argument("--root",default=".")
    scan.add_argument("--db",default=".cache/capability-index.sqlite")
    scan.add_argument("--ledger",default=".cache/capability-discovery-ledger.jsonl")
    scan.add_argument("--plugin-skills-json")
    scan.add_argument("--tool-actions-json")
    find = sub.add_parser("find",help="Search metadata only; hydrate full source after selection")
    find.add_argument("query")
    find.add_argument("--db",default=".cache/capability-index.sqlite")
    find.add_argument("--limit",type=int,default=8)
    find.add_argument("--skills-sh",action="store_true",help="Add read-only skills.sh search; requires VERCEL_OIDC_TOKEN")
    args = parser.parse_args()
    if args.command == "scan":
        root = Path(args.root).resolve()
        rows = scan_repository(root)
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
    if args.skills_sh:
        remote_rows, external_status = search_skills_sh(args.query,args.limit)
        if remote_rows:
            upsert(con,remote_rows)
    hits = search(con,args.query,args.limit)
    print(json.dumps({"query":args.query,"count":len(hits),"external_skills_sh":external_status,"results":hits},ensure_ascii=False,sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
