"""_v1_namespace — parse bank names and agent namespaces.

BANK-NAMING.md (8 slots):
  <project>::<method>::<vendor>::<family>::<model>::<settings>::<role>::<comp>

Agent provenance (5 shared slots + optional tag):
  <vendor>::<family>::<model>::<settings>::<role>[#moniker]

The middle five slots are identical between the two shapes. A bank
name carries prefix (project::method) and suffix (::comp). An agent
namespace is that middle slice with an optional tag.

Public API:
    parse_any(s)  -> dict with "shape" and every slot it can find
    shared(s)     -> {"vendor","family","model","settings","role"}
    build_bank(**slots)
    build_agent(**slots)
"""

BANK_SLOTS  = ["project","method","vendor","family","model","settings","role","comp"]
AGENT_SLOTS = ["vendor","family","model","settings","role"]
SHARED      = ["vendor","family","model","settings","role"]


def _split_tag(s):
    if "#" in s:
        base, tag = s.split("#", 1)
        return base, tag
    return s, None


def parse_any(s):
    if not s:
        return {}
    base, moniker = _split_tag(s)
    parts = base.split("::")
    out = {}
    if len(parts) == 8:
        out = dict(zip(BANK_SLOTS, parts))
        out["shape"] = "bank"
    elif len(parts) == 5:
        out = dict(zip(AGENT_SLOTS, parts))
        out["shape"] = "agent"
    elif len(parts) == 2 and parts[1] == "primary":
        out = {"project": parts[0], "method": "primary", "shape": "primary"}
    elif len(parts) == 2 and parts[1] == "mvt":
        out = {"project": parts[0], "method": "mvt", "shape": "bank-partial"}
    else:
        out = {"shape": "unknown", "raw": s, "slot_count": len(parts)}
    if moniker:
        out["moniker"] = moniker
    return out


def shared(s):
    d = parse_any(s)
    return {k: d.get(k) for k in SHARED}


def build_bank(project, method, vendor, family, model, settings, role, comp="base"):
    return "::".join([project, method, vendor, family, model, settings, role, comp])


def build_agent(vendor, family, model, settings, role, moniker=None):
    base = "::".join([vendor, family, model, settings, role])
    if moniker:
        base += "#" + re.sub(r"[^a-z0-9-]", "-", moniker.lower())[:32]
    return base
