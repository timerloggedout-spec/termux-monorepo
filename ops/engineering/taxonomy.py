"""Engineering taxonomy validator and query CLI; standard library only."""
from __future__ import annotations
import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load_taxonomy(path=None):
    source=Path(path) if path else HERE/"taxonomy.json"
    return json.loads(source.read_text(encoding="utf-8"))

def validate(tax):
    errors=[]
    if tax.get("schema")!="engineering-taxonomy/v1": errors.append("schema must be engineering-taxonomy/v1")
    nodes=tax.get("nodes") or []
    by_id={}
    for node in nodes:
        node_id=node.get("id")
        if not isinstance(node_id,str) or not node_id: errors.append("every node needs a non-empty id"); continue
        if node_id in by_id: errors.append(f"duplicate node id {node_id!r}")
        by_id[node_id]=node
        if node.get("kind") not in ("category","tool"): errors.append(f"{node_id}: kind must be category|tool")
    axes=tax.get("axes") or {}
    for node_id,node in by_id.items():
        for parent in node.get("parents",[]):
            if parent not in by_id: errors.append(f"{node_id}: unknown parent {parent!r}")
        for axis,values in (node.get("tags") or {}).items():
            if axis not in axes: errors.append(f"{node_id}: unknown axis {axis!r}"); continue
            if not isinstance(values,list): errors.append(f"{node_id}: axis {axis!r} values must be a list"); continue
            for value in values:
                if value not in axes[axis]: errors.append(f"{node_id}: unknown {axis} value {value!r}")
        if node.get("kind")=="tool":
            metadata=node.get("metadata") or {}
            for field in ("license","license_class","access","payment_card_required","execution_target","probe_commands","source_url"):
                if field not in metadata: errors.append(f"{node_id}: missing metadata field {field!r}")
            if metadata.get("access") not in (axes.get("access") or []): errors.append(f"{node_id}: invalid access class")
            if not isinstance(metadata.get("probe_commands",[]),list): errors.append(f"{node_id}: probe_commands must be a list")
            if not (node.get("tags") or {}).get("tool_role"): errors.append(f"{node_id}: tool requires a tool_role tag")
    if "engineering" not in by_id or by_id.get("engineering",{}).get("parents")!=[]: errors.append("engineering root node is missing or has parents")
    WHITE,GRAY,BLACK=0,1,2
    colors={node_id:WHITE for node_id in by_id}
    def visit(node_id,trail):
        colors[node_id]=GRAY
        for parent in by_id[node_id].get("parents",[]):
            if parent not in by_id: continue
            if colors[parent]==GRAY: errors.append(f"parent cycle: {' -> '.join(trail+[node_id,parent])}")
            elif colors[parent]==WHITE: visit(parent,trail+[node_id])
        colors[node_id]=BLACK
    for node_id in by_id:
        if colors[node_id]==WHITE: visit(node_id,[])
    def reaches_root(node_id,seen=None):
        path=set() if seen is None else set(seen)
        if node_id=="engineering": return True
        if node_id in path: return False
        path.add(node_id)
        return any(parent in by_id and reaches_root(parent,path) for parent in by_id[node_id].get("parents",[]))
    for node_id in by_id:
        if node_id!="engineering" and not reaches_root(node_id): errors.append(f"{node_id}: does not descend from engineering")
    stages=tax.get("workflow_stages") or []
    for chain in tax.get("toolchains") or []:
        category=chain.get("category")
        if category not in by_id or by_id[category].get("kind")!="category": errors.append(f"toolchain {chain.get('id')!r}: unknown category {category!r}")
        last=-1
        for step in chain.get("stages",[]):
            stage=step.get("stage")
            if stage not in stages: errors.append(f"toolchain {chain.get('id')!r}: unknown stage {stage!r}"); continue
            index=stages.index(stage)
            if index<last: errors.append(f"toolchain {chain.get('id')!r}: stages out of order")
            last=index
            for tool_id in step.get("tools",[]):
                if tool_id not in by_id or by_id[tool_id].get("kind")!="tool": errors.append(f"toolchain {chain.get('id')!r}: {tool_id!r} is not a tool")
    matrix=tax.get("overlap_matrix") or {}
    for row_id,row in (matrix.get("rows") or {}).items():
        if row_id not in by_id: errors.append(f"overlap row {row_id!r} is not a node")
        for method,value in row.items():
            if method not in (matrix.get("methods") or []): errors.append(f"overlap {row_id}: unknown method {method!r}")
            if value not in (matrix.get("values") or []): errors.append(f"overlap {row_id}: invalid value {value!r}")
    return errors

def node(tax,node_id):
    for item in tax.get("nodes",[]):
        if item.get("id")==node_id:
            children=[candidate["id"] for candidate in tax["nodes"] if node_id in candidate.get("parents",[])]
            return {**item,"children":children}
    return None

def toolchain(tax,chain_id):
    return next((item for item in tax.get("toolchains",[]) if item.get("id")==chain_id),None)

def main(argv=None):
    args=list(sys.argv[1:] if argv is None else argv); tax=load_taxonomy(); command=args[0] if args else "validate"
    if command=="validate":
        errors=validate(tax); print("\n".join(errors) if errors else f"engineering-taxonomy/v1: valid ({len(tax['nodes'])} nodes, {len(tax['toolchains'])} toolchains)"); return 1 if errors else 0
    if command=="node" and len(args)==2: print(json.dumps(node(tax,args[1]),indent=2,sort_keys=True)); return 0
    if command=="toolchain" and len(args)==2: print(json.dumps(toolchain(tax,args[1]),indent=2,sort_keys=True)); return 0
    print(__doc__); return 2

if __name__=="__main__": sys.exit(main())
