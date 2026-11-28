"""Read-only inventory probe for engineering CLI tools on Termux or a runner."""
from __future__ import annotations
import argparse,json,os,shutil,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from ops.engineering.taxonomy import load_taxonomy,validate

def build_report(taxonomy):
    tools=[]
    for node in taxonomy.get("nodes",[]):
        if node.get("kind")!="tool": continue
        meta=node.get("metadata") or {}; commands=meta.get("probe_commands") or []
        target=meta.get("execution_target","unknown")
        if target.startswith("vendor-"):
            matched=None; detection_state="external"; detected=None
        else:
            matched=next((command for command in commands if shutil.which(command)),None)
            detection_state="present" if matched is not None else "absent"
            detected=matched is not None
        tools.append({"id":node["id"],"name":node["name"],"detected":detected,"detection_state":detection_state,"matched_command":matched,"execution_target":target,"termux_runtime":meta.get("termux_runtime","unverified"),"license_class":meta.get("license_class","unknown"),"access":meta.get("access","unknown")})
    return {"schema":"engineering-toolchain-probe/v1","observed_at":datetime.now(timezone.utc).isoformat(),"runtime":"termux" if (os.environ.get("TERMUX_VERSION") or "com.termux" in os.environ.get("PREFIX","")) else sys.platform,"tools":tools,"summary":{"catalogued":len(tools),"detected":sum(1 for item in tools if item["detection_state"]=="present"),"local_missing":sum(1 for item in tools if item["detection_state"]=="absent"),"external":sum(1 for item in tools if item["detection_state"]=="external")}}

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
