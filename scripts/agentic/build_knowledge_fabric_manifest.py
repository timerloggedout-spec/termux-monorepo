#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def build(repositories: list[dict], *, include_devin: bool) -> dict:
    entries = []
    for item in repositories:
        if item.get("archived") or item.get("disabled"):
            continue
        full_name = item["full_name"]
        entries.append({
            "repo": full_name,
            "default_branch": item.get("default_branch"),
            "fork": bool(item.get("fork")),
            "wiki_enabled": bool(item.get("has_wiki")),
            "github_wiki_url": f"https://github.com/{full_name}/wiki",
            "deepwiki_url": f"https://deepwiki.com/{full_name}",
            "devinwiki": {
                "requested": include_devin,
                "status": "provider-check-required" if include_devin else "not-requested",
            },
            "deepwiki_rs": {
                "engine": "sopaco/deepwiki-rs",
                "release": "1.6.0",
                "mode": "remote-cli",
                "status": "validation-and-explicit-generation",
            },
            "wiki_rs": {
                "adapter": "sw-vibe-coding/wiki-rs",
                "mode": "remote-git-workspace",
                "status": "validation-and-manifest",
            },
        })
    return {"schema_version":"2","source":"github-installation-repositories","count":len(entries),"repositories":entries}

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--repos",required=True); p.add_argument("--output",required=True); p.add_argument("--include-devin",action="store_true")
    a=p.parse_args()
    source=json.loads(Path(a.repos).read_text(encoding="utf-8"))
    if not isinstance(source,list): raise SystemExit("--repos must contain a JSON array")
    Path(a.output).write_text(json.dumps(build(source,include_devin=a.include_devin),indent=2)+"
",encoding="utf-8")

if __name__=="__main__":
    main()
