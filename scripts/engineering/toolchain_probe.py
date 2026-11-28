"""Read-only inventory probe for engineering CLI tools on Termux or a runner."""
from __future__ import annotations
import argparse,json,shutil
from datetime import datetime,timezone
from ops.engineering.taxonomy import load_taxonomy,validate

def build_report(taxonomy):
    tools=[]
    for node in taxonomy.get("nodes",[]):
        if node.get("kind")!="tool": continue
        meta=node.get("metadata") or {}; commands=meta.get("probe_commands") or []
        matched=next((command for command in commands if shutil.which(command)),None)
        tools.append({"id":node["id"],"name":node["name"],"detected":matched is not None,"matched_command":matched,"execution_target":meta.get("execution_target","unknown"),"termux_runtime":meta.get("termux_runtime","unverified"),"license_class":meta.get("license_class","unknown"),"access":meta.get("access","unknown")})
    return {"schema":"engineering-toolchain-probe/v1","observed_at":datetime.now(timezone.utc).isoformat(),"runtime":"termux-or-linux","tools":tools,"summary":{"catalogued":len(tools),"detected":sum(1 for item in tools if item["detected"]),"unavailable":sum(1 for item in tools if not item["detected"])}}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--json",action="store_true"); args=parser.parse_args()
    taxonomy=load_taxonomy(); errors=validate(taxonomy)
    if errors: print("\n".join(errors)); return 1
    report=build_report(taxonomy)
    if args.json: print(json.dumps(report,indent=2,sort_keys=True))
    else:
        print(f"Engineering tools detected: {report['summary']['detected']}/{report['summary']['catalogued']}")
        for item in report["tools"]: print(f"{item['id']}: {'available' if item['detected'] else 'offload-or-install-required'}")
    return 0
if __name__=="__main__": raise SystemExit(main())
