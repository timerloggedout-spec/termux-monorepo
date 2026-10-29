#!/usr/bin/env python3
"""Cross-plane link pass — an ADDITIONAL VIEW over the existing
observation-plane indexes, never a new source of truth.

Reads the committed plane indexes (GitHub repository-index, X x-index,
research-seed files, the repository index's issue_intake, and the
challenge coordinator) and derives a deterministic edge list
(graph-edges/v1) plus a summary (graph-index/v1) and a Markdown
projection. It makes NO API calls and edits NO plane index: planes stay
single-writer by their owning lanes, and this view is regenerated from
them by .github/workflows/cross-plane-graph.yml.

Lane responsibility (2026-10-29): source structures stay with their
owning lanes — challenge entries lane owns coordinator.json records,
the OSINT seat owns coverage/snapshots, the DB lane owns the Neon
participant store. This graph lane owns ONLY the import/view layer.

Entity ids are the ids the planes already emit:
  github:repository:{owner}/{repo}   (repository-index record `id`)
  x:tweet:{tweet_id}                 (x-index record `id`)
  github:research-seed:{owner}/{repo} / research-seed:{slug} (seed_id)
plus view-minted namespaces for entities planes name but do not id:
  github:user:{login}  x:user:{handle}  topic:{slug}  domain:{slug}
  challenge:event:{id}  challenge:participant:{event}/{key}
  challenge:project:{event}/{slug}  challenge:judge:{slug}
  challenge:organizer:{slug}

Edge record (one JSON object per line in edges.jsonl):
  {src, dst, type, evidence:{plane, record, method, observed_at}}
Directions are actor-first: src --type--> dst reads as a sentence.

Privacy / integrity rules:
- X bookmark records are metadata-only in their plane; this pass never
  reads or stores tweet text. URL extraction runs only over a like
  record's public excerpt.
- Challenge `metrics_internal` (win_probability etc.) is NEVER read:
  internal metrics render only in the Admin panel, never in a public
  graph view. The challenge pass skips that key by construction.
- Participant identity edges (`same_author_as`) are emitted only from a
  participant's own published public_links.github — explicit evidence,
  never name-matching. 4n0n unlinkability is untouched: our entrants'
  records carry no such public link by design.
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

BUILDER = "termux-monorepo.cross_plane_link@1.1"
GH_REPO_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
OWNER_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

def repo_id(full_name): return f"github:repository:{full_name}"
def gh_user(login): return f"github:user:{login}"
def x_user(handle): return f"x:user:{handle}"
def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s or "unknown"

class EdgeSet:
    def __init__(self): self.edges = {}
    def add(self, src, dst, typ, plane, record, method, observed_at):
        if not src or not dst or src == dst: return
        key = (src, dst, typ)
        if key not in self.edges:
            self.edges[key] = {"src": src, "dst": dst, "type": typ,
                               "evidence": {"plane": plane, "record": record,
                                            "method": method, "observed_at": observed_at}}
    def sorted(self):
        return [self.edges[k] for k in sorted(self.edges)]

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def pass_github(payload, es):
    observed = payload.get("observed_at")
    auth = payload.get("authenticated_user")
    repos = set()
    for rec in payload.get("repositories") or []:
        rid = rec.get("id") or repo_id(rec["full_name"])
        repos.add(rec["full_name"])
        if rec.get("owner"):
            es.add(rid, gh_user(rec["owner"]), "authored_by",
                   "github", rec["full_name"], "record_owner_field", observed)
        for prov in rec.get("provenance") or []:
            if auth and prov in ("owned", "starred", "watching"):
                es.add(gh_user(auth), rid, prov,
                       "github", rec["full_name"], f"provenance_{prov}", observed)
        for topic in rec.get("topics") or []:
            es.add(rid, f"topic:{topic}", "about_topic",
                   "github", rec["full_name"], "record_topics_field", observed)
        for dom in (rec.get("classification") or {}).get("domains") or []:
            es.add(rid, f"domain:{dom}", "in_domain",
                   "github", rec["full_name"], "classification_domains", observed)
        if rec.get("upstream") and OWNER_REPO_RE.match(rec["upstream"]):
            es.add(rid, repo_id(rec["upstream"]), "fork_of",
                   "github", rec["full_name"], "record_upstream_field", observed)
    for entry in payload.get("issue_intake") or []:
        seed = entry.get("seed_id")
        up = (entry.get("upstream") or "").strip()
        if seed and up and OWNER_REPO_RE.match(up):
            es.add(seed, repo_id(up), "mentions_repo",
                   "github", seed, "issue_intake_upstream", observed)
    return repos

def pass_x(payload, es, repo_names):
    observed = payload.get("observed_at")
    account = payload.get("account") or {}
    own = account.get("username") or account.get("handle")
    skipped_actor = 0
    for rec in payload.get("records") or []:
        tid = rec.get("id") or f"x:tweet:{rec.get('tweet_id')}"
        if rec.get("author_handle"):
            es.add(tid, x_user(rec["author_handle"]), "authored_by",
                   "x", tid, "record_author_handle", observed)
        for sig in rec.get("signals") or []:
            if own:
                es.add(x_user(own), tid, {"like": "liked", "bookmark": "bookmarked"}.get(sig, sig),
                       "x", tid, f"signal_{sig}", observed)
            else:
                skipped_actor += 1
        text = rec.get("text_excerpt") or ""
        for owner, name in GH_REPO_RE.findall(text):
            name = name.rstrip(".,)")
            if f"{owner}/{name}" in repo_names:
                es.add(tid, repo_id(f"{owner}/{name}"), "mentions_repo",
                       "x", tid, "excerpt_github_url_resolved_to_index", observed)
    return skipped_actor

def pass_seeds(seeds_dir, es, observed):
    n = 0
    if not seeds_dir or not Path(seeds_dir).is_dir(): return n
    for path in sorted(Path(seeds_dir).glob("*.json")):
        try: seed = load_json(path)
        except Exception: continue
        sid = seed.get("seed_id")
        if not sid: continue
        n += 1
        up = (seed.get("canonical_upstream") or "").strip()
        if OWNER_REPO_RE.match(up):
            es.add(sid, repo_id(up), "upstream",
                   "research-seeds", sid, "seed_canonical_upstream", observed)
        local_fork = (seed.get("local_fork") or "").strip()
        if local_fork and OWNER_REPO_RE.match(local_fork) and OWNER_REPO_RE.match(up):
            es.add(repo_id(local_fork), repo_id(up), "fork_of",
                   "research-seeds", sid, "seed_local_fork+fork_parent", observed)
        for item in seed.get("repos") or []:
            r = (item or {}).get("repo") or ""
            if OWNER_REPO_RE.match(r):
                es.add(sid, repo_id(r), "mentions_repo",
                       "research-seeds", sid, "seed_repos_list", observed)
        for dom in (seed.get("classification") or {}).get("domains") or []:
            es.add(sid, f"domain:{dom}", "in_domain",
                   "research-seeds", sid, "classification_domains", observed)
    return n

def _participant_key(p):
    for field in ("id", "handle", "username", "name", "team_name", "url"):
        v = (p.get(field) or "")
        if isinstance(v, str) and v.strip(): return slugify(v)
    return "sha256:" + hashlib.sha256(
        json.dumps(p, sort_keys=True).encode()).hexdigest()[:16]

def _gh_login_from_link(link):
    if not link: return None
    m = re.search(r"github\.com/([A-Za-z0-9-]+)", str(link))
    if m: return m.group(1)
    s = str(link).strip().lstrip("@")
    return s if re.fullmatch(r"[A-Za-z0-9-]+", s) else None

def _project_edges(es, eid, event_id, project, owner_entity, observed):
    """project may be a dict {name,url,...} or a plain string."""
    if not project: return
    if isinstance(project, str): project = {"name": project}
    name = project.get("name") or project.get("title") or project.get("url") or ""
    if not name: return
    pid = f"challenge:project:{eid}/{slugify(name)}"
    if owner_entity:
        es.add(owner_entity, pid, "entered_with",
               "challenge", pid, "participant_project", observed)
    es.add(pid, event_id, "submitted_to",
           "challenge", pid, "project_of_event", observed)
    url = project.get("url") or project.get("repo") or ""
    for owner, repo in GH_REPO_RE.findall(str(url)):
        es.add(pid, repo_id(f"{owner}/{repo.rstrip('.,)')}"), "hosted_at",
               "challenge", pid, "project_url_github", observed)

def pass_challenge(payload, es):
    """Import participant|competitor OSINT structures from the challenge
    coordinator (ops/challenge/coordinator.json). Shape-tolerant, like
    scripts/challenge/participant_event.py. NEVER reads metrics_internal."""
    observed = payload.get("updated_at") or payload.get("observed_at")
    counts = {"events": 0, "participants": 0, "judges": 0, "organizers": 0}
    for ev in payload.get("events") or []:
        if not isinstance(ev, dict): continue
        eid = ev.get("id") or ev.get("slug") or ev.get("key") or slugify(ev.get("name") or "event")
        event_id = f"challenge:event:{eid}"
        counts["events"] += 1
        for org in ev.get("organizers") or []:
            if isinstance(org, str): org = {"name": org}
            oname = org.get("name")
            if not oname: continue
            counts["organizers"] += 1
            es.add(f"challenge:organizer:{slugify(oname)}", event_id, "organizes",
                   "challenge", event_id, f"organizer_role_{org.get('role') or 'unknown'}", observed)
        for judge in ev.get("judges") or []:
            if isinstance(judge, str): judge = {"name": judge}
            jname = judge.get("name") or (judge.get("persona") or {}).get("name")
            if not jname: continue
            counts["judges"] += 1
            es.add(f"challenge:judge:{slugify(jname)}", event_id, "judges",
                   "challenge", event_id, "event_judges_list", observed)
        for proj in ev.get("projects") or []:
            _project_edges(es, eid, event_id, proj, None, observed)
        people = list(ev.get("participants") or []) + list(ev.get("competitors") or [])
        for p in people:
            if not isinstance(p, dict): continue
            counts["participants"] += 1
            pkey = _participant_key(p)
            pid = f"challenge:participant:{eid}/{pkey}"
            es.add(pid, event_id, "competes_in",
                   "challenge", pid, "event_participants_list", observed)
            _project_edges(es, eid, event_id, p.get("project"), pid, observed)
            links = ((p.get("persona") or {}).get("public_links") or {})
            login = _gh_login_from_link(links.get("github"))
            if login:
                es.add(pid, gh_user(login), "same_author_as",
                       "challenge", pid, "participant_public_links_github_explicit", observed)
            for win in p.get("past_wins") or []:
                wname = (win or {}).get("event")
                if wname:
                    es.add(pid, f"challenge:event:{slugify(wname)}", "won",
                           "challenge", pid, "participant_past_wins", observed)
    return counts

def build(repo_index_path, x_index_path, seeds_dir, challenge_path=None):
    es = EdgeSet()
    sources = {}
    repo_payload = load_json(repo_index_path)
    sources["github"] = {"path": "workspace/llm_map/repositories/repository-index.json",
                         "observed_at": repo_payload.get("observed_at"),
                         "snapshot_hash": repo_payload.get("snapshot_hash"),
                         "records": len(repo_payload.get("repositories") or [])}
    repo_names = pass_github(repo_payload, es)
    skipped_actor = 0
    if x_index_path and Path(x_index_path).exists():
        x_payload = load_json(x_index_path)
        sources["x"] = {"path": "workspace/llm_map/social/x-index.json",
                        "observed_at": x_payload.get("observed_at"),
                        "snapshot_hash": x_payload.get("snapshot_hash"),
                        "records": len(x_payload.get("records") or []),
                        "status": x_payload.get("status")}
        skipped_actor = pass_x(x_payload, es, repo_names)
    observed = repo_payload.get("observed_at")
    n_seeds = pass_seeds(seeds_dir, es, observed)
    sources["research_seeds"] = {"path": "docs/repositories/research-seeds", "records": n_seeds}
    if challenge_path and Path(challenge_path).exists():
        ch = load_json(challenge_path)
        counts = pass_challenge(ch, es)
        sources["challenge"] = {"path": "ops/challenge/coordinator.json",
                                "observed_at": ch.get("updated_at") or ch.get("observed_at"),
                                "records": counts}
    edges = es.sorted()
    blob = "".join(json.dumps(e, sort_keys=True) + "\n" for e in edges).encode()
    entities = {}
    by_type = {}
    for e in edges:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
        for endpoint in (e["src"], e["dst"]):
            parts = endpoint.split(":")
            key = ":".join(parts[:2]) if len(parts) >= 2 and parts[0] in ("github", "x", "challenge") else parts[0]
            entities[key] = entities.get(key, 0) + 1
    summary = {
        "schema_version": "graph-index/v1",
        "builder": BUILDER,
        "observed_at": observed,
        "view_of": "existing observation-plane indexes; derived, never a source of truth",
        "sources": sources,
        "counts": {"edges": len(edges), "edge_types": by_type,
                   "entity_endpoints_by_namespace": entities,
                   "x_actor_edges_skipped_account_unknown": skipped_actor},
        "snapshot_hash": hashlib.sha256(blob).hexdigest(),
    }
    return edges, summary

def render_markdown(edges, summary):
    lines = ["# Cross-Plane Graph — projection (additional view)",
             "",
             "> Canonical data: `workspace/llm_map/graph/edges.jsonl` + `graph-index.json`, derived by `scripts/graph/cross_plane_link.py` from the plane indexes. This is a view over existing planes, never a source of truth; signals are research signals, never adoption orders.",
             "",
             f"Observed (repository index): `{summary['observed_at']}` · Edges: **{summary['counts']['edges']}**",
             "", "## Edges by type", ""]
    for t, c in sorted(summary["counts"]["edge_types"].items(), key=lambda kv: -kv[1]):
        lines.append(f"- **{t}:** {c}")
    lines += ["", "## Cross-plane / seed / challenge edges", "",
              "| Src | Type | Dst | Method |", "|---|---|---|---|"]
    for e in edges:
        if e["evidence"]["plane"] != "github" or e["type"] in ("mentions_repo", "upstream", "fork_of"):
            lines.append(f"| `{e['src']}` | {e['type']} | `{e['dst']}` | {e['evidence']['method']} |")
    lines.append("")
    return "\n".join(lines)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-index", required=True)
    ap.add_argument("--x-index")
    ap.add_argument("--seeds-dir")
    ap.add_argument("--challenge-index")
    ap.add_argument("--output", required=True, help="edges.jsonl path")
    ap.add_argument("--summary", required=True, help="graph-index.json path")
    ap.add_argument("--markdown", required=True)
    a = ap.parse_args(argv)
    edges, summary = build(a.repo_index, a.x_index, a.seeds_dir, a.challenge_index)
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    Path(a.output).write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in edges), encoding="utf-8")
    Path(a.summary).write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    Path(a.markdown).parent.mkdir(parents=True, exist_ok=True)
    Path(a.markdown).write_text(render_markdown(edges, summary), encoding="utf-8")
    print(f"edges={len(edges)} types={summary['counts']['edge_types']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
