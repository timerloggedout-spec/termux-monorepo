#!/usr/bin/env python3
"""DO build ∧ validate one mesh request line (schema ops/mesh/REQUESTS-SCHEMA.md).

Input: env MR_* (workflow_dispatch) ∨ MR_ISSUE_BODY (issue labeled mesh:request, `key: value` lines).
Output: one JSON line on stdout; GITHUB_OUTPUT gets target, kind, id. Allowlist only; invalid ⇒ exit 1.
"""
import json, os, re, sys, uuid, datetime

TARGETS = {"hark-vm", "actions", "codespaces", "cloudshell", "muse-vm", "any"}
KINDS = {"eval", "export", "hygiene", "probe"}
PRIORITIES = {"T1", "T2", "T3", "T4"}
REF_RX = re.compile(r"^[A-Za-z0-9._/#:@-]{0,200}$")

def fields():
    body = os.environ.get("MR_ISSUE_BODY", "")
    if body:
        f = {}
        for raw in body.splitlines():
            m = re.match(r"^\s*(?:###\s*)?(target|kind|ref|args|priority)\s*:\s*(.*)$", raw, re.I)
            if m:
                f[m.group(1).lower()] = m.group(2).strip().strip("`")
        return f, f"issue#{os.environ.get('MR_ISSUE_NUMBER', '?')}"
    return ({k: os.environ.get(f"MR_{k.upper()}", "") for k in ("target", "kind", "ref", "args", "priority")},
            os.environ.get("MR_FROM", "dispatch"))

def fail(msg):
    print(f"::error title=mesh-request::{msg}")
    sys.exit(1)

def main():
    f, origin = fields()
    target = (f.get("target") or "").lower()
    kind = (f.get("kind") or "").lower()
    priority = (f.get("priority") or "T4").upper()
    ref = f.get("ref") or ""
    if target not in TARGETS: fail(f"target ∉ allowlist: {target!r}")
    if kind not in KINDS: fail(f"kind ∉ allowlist: {kind!r}")
    if priority not in PRIORITIES: fail(f"priority ∉ T1–T4: {priority!r}")
    if not REF_RX.match(ref): fail("ref ⊥ (charset ∨ length)")
    raw_args = f.get("args") or "{}"
    if len(raw_args) > 2000: fail("args > 2000 chars")
    try:
        args = json.loads(raw_args)
    except json.JSONDecodeError:
        fail("args ⊥ JSON")
    if not isinstance(args, dict): fail("args ∉ object")
    line = {
        "id": str(uuid.uuid4()),
        "ts_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "from": origin, "target": target, "kind": kind, "ref": ref, "args": args, "priority": priority,
    }
    print(json.dumps(line, ensure_ascii=False, separators=(",", ":")))
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"target={target}\nkind={kind}\nid={line['id']}\n")

if __name__ == "__main__":
    main()
