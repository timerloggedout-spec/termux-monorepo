#!/usr/bin/env python3
"""Validate the exhaustive federated repository discovery snapshot (stdlib only)."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/ops/federated-app-repository-census.json"
SCHEMA = ROOT / "docs/ops/federated-app-repository-census.schema.json"
OWNER = "timerloggedout-spec"
def validate(data):
    errors=[]
    source=data.get("source",{})
    repos=data.get("repositories",[])
    names=[r.get("full_name") for r in repos if isinstance(r,dict)]
    if len(names)!=len(repos): errors.append("every repository must be an object")
    if len(names)!=len(set(names)): errors.append("duplicate repository full_name")
    if source.get("unique_repositories") != len(repos): errors.append("unique_repositories does not match repository records")
    if source.get("returned_records") < len(repos): errors.append("returned_records cannot be smaller than unique repository count")
    if source.get("owner") != OWNER: errors.append("unexpected census owner")
    for i,r in enumerate(repos):
        name=r.get("full_name","")
        if not re.fullmatch(r"[^/]+/[^/]+",name): errors.append(f"repositories[{i}].full_name must be owner/repository")
        elif name.split("/")[0].lower()!=OWNER: errors.append(f"repositories[{i}] is outside owner scope")
        if r.get("classification")!="discovered": errors.append(f"repositories[{i}] must remain discovered until adjudicated")
        if r.get("product_app_id") is not None: errors.append(f"repositories[{i}] cannot invent a product AppID")
        if r.get("evidence_status")!="repository-metadata-only": errors.append(f"repositories[{i}] requires metadata-only evidence status")
        if not r.get("default_branch"): errors.append(f"repositories[{i}] missing default branch")
        if not str(r.get("html_url","")).startswith("https://github.com/"): errors.append(f"repositories[{i}] invalid GitHub URL")
    queue=data.get("application_review_queue",[])
    qnames=[x.get("repository") for x in queue]
    if len(qnames)!=len(set(qnames)): errors.append("duplicate application review queue repository")
    if any(q not in set(names) for q in qnames): errors.append("review queue contains repository absent from census")
    return errors
def main():
    try:
        data=json.loads(DATA.read_text()); schema=json.loads(SCHEMA.read_text())
        import jsonschema
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(data,schema)
    except ImportError:
        print("jsonschema dependency is required",file=sys.stderr); return 2
    except Exception as exc:
        print(f"census schema/load failure: {exc}",file=sys.stderr); return 2
    errors=validate(data)
    if errors:
        for e in errors: print("ERROR:",e,file=sys.stderr)
        return 1
    print(f"Federated repository census valid: {len(data['repositories'])} repositories; {len(data['application_review_queue'])} review candidates")
    return 0
if __name__=="__main__": raise SystemExit(main())
