"""/v1/skills — list and read local skill definitions."""
import os, re, sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

HOME = Path.home()
TOKEN_FILE = HOME / ".deepcli" / "hub.token"
SKILL_ROOTS = [
    HOME / ".agents" / "skills",
    HOME / ".claude" / "skills",
    HOME / ".pi" / "skills",
]
MAX_BODY_BYTES = 256 * 1024

router = APIRouter(prefix="/v1/skills", tags=["skills"])
_bearer = HTTPBearer(auto_error=False)


def _auth(creds: HTTPAuthorizationCredentials = Depends(_bearer)):
    expected = os.environ.get("HUB_TOKEN")
    if not expected and TOKEN_FILE.exists():
        expected = TOKEN_FILE.read_text().strip()
    if not expected:
        raise HTTPException(500, "hub token not configured")
    if creds is None or creds.credentials != expected:
        raise HTTPException(401, "invalid token")


_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(text: str):
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, text[m.end():]


def _skills():
    seen = {}
    for root in SKILL_ROOTS:
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if not d.is_dir():
                continue
            skill_md = d / "SKILL.md"
            if not skill_md.exists():
                # some skills use lowercase
                skill_md = d / "skill.md"
            if not skill_md.exists():
                continue
            try:
                raw = skill_md.read_text(errors="replace")
            except Exception:
                continue
            fm, body = _parse_frontmatter(raw)
            name = fm.get("name") or d.name
            if name in seen:
                continue
            seen[name] = {
                "name": name,
                "dir": str(d),
                "path": str(skill_md),
                "description": fm.get("description", ""),
                "body_size": len(body),
                "has_assets": (d / "assets").is_dir() if (d / "assets").exists() else False,
                "has_references": (d / "references").is_dir() if (d / "references").exists() else False,
            }
    return sorted(seen.values(), key=lambda s: s["name"])


@router.get("/list", dependencies=[Depends(_auth)])
@router.post("/list", dependencies=[Depends(_auth)])
def list_skills():
    return {"skills": _skills()}


@router.get("/read/{name}", dependencies=[Depends(_auth)])
@router.post("/read/{name}", dependencies=[Depends(_auth)])
def read_skill(name: str, include_body: bool = True):
    for s in _skills():
        if s["name"] == name:
            md_path = Path(s["path"])
            text = md_path.read_text(errors="replace")
            fm, body = _parse_frontmatter(text)
            resp = {
                "name": s["name"],
                "description": s["description"],
                "dir": s["dir"],
            }
            if include_body:
                body = body[:MAX_BODY_BYTES]
                resp["body"] = body
            # list sibling assets/references
            d = Path(s["dir"])
            extras = []
            for sub in ("assets", "references", "scripts", "templates"):
                sp = d / sub
                if sp.is_dir():
                    for f in sorted(sp.iterdir()):
                        if f.is_file():
                            extras.append(f"{sub}/{f.name}")
            resp["files"] = extras[:50]
            return resp
    raise HTTPException(404, f"skill not found: {name}")
