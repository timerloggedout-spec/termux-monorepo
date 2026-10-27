#!/usr/bin/env python3
"""Registration moniker registry tool — the 4n0n protocol's machine half.

One Role{Moniker} per challenge registration/platform, per
docs/ops/4N0N-REGISTRATION-PROTOCOL.md. The registry of record is
config/registration_monikers.json; the registration source of truth is
docs/ops/CHALLENGE-ENTRIES-LOG.md. This tool:

  check   validate the registry against the log and the assignment rule
          (exit 1 on any drift; drift lines are machine-readable)
  assign  append entries for platforms the log has activated (a platform
          named in log section 1 or 4) that have no registry entry yet —
          moniker derived by rule, public_handle always null (a handle is
          a provisioning fact and is never invented)
  render  regenerate the registry table inside the protocol doc from the
          JSON (between the registry:begin / registry:end markers)

Moniker assignment rule (deterministic): entries are processed in
platform_id sort order; moniker = "entrant" + the platform_id's words
capitalized and joined ("aws-builder-center" -> "entrantAwsBuilderCenter").
On collision with a different platform_id, append the smallest integer
>= 2 that frees the token. Canonical form:
entrant{<moniker>}[platform:<platform_id>].

Platform detection vocabulary (ALIASES below) is curated: a platform
named in the log's candidate section (section 3) only is NOT activated —
candidates are not registrations. A platform outside the vocabulary
produces no auto-assignment; adding its alias line is a one-line
curated PR, never an invented handle.

Stdlib only.
"""
import argparse
import json
import re
import sys

ROLE = "entrant"
SCHEMA = "registration-monikers/1"

# (alias string as it appears in the challenge log, platform_id,
#  platform display name, kind)
ALIASES = [
    ("AWS Builder Center", "aws-builder-center", "AWS Builder Center", "platform"),
    ("Builder.io", "builder-io", "Builder.io", "platform"),
    ("lablab.ai", "lablab-ai", "lablab.ai", "platform"),
    ("Vultr", "vultr", "Vultr", "platform"),
    ("Devpost", "devpost", "Devpost", "platform"),
    ("Kiro", "kiro", "Kiro", "identity-provider"),
    ("PayPal", "paypal", "PayPal", "platform"),
    ("Lexsi", "lexsi", "Lexsi", "platform"),
    ("Hugging Face", "hugging-face", "Hugging Face", "platform"),
]
ALIAS_BY_ID = {pid: (alias, name, kind) for alias, pid, name, kind in ALIASES}

DEFAULT_HANDLING = {
    "owner_lane": "challenge-entries",
    "receipts_route": (
        "Platform confirmations land in the owner's Gmail; the owning lane "
        "cites them into docs/ops/CHALLENGE-ENTRIES-LOG.md (sections 1/2) "
        "by PR and syncs this registry in the same PR."
    ),
    "submission_authority": (
        "The owning lane prepares artifacts under the moniker; submission "
        "follows the challenge log's standing boundary: no new account, no "
        "payment, no owner-gated step, and the challenge is already "
        "entered or owner-approved."
    ),
    "escalation": [
        "Owner-gated steps (account creation/sign-in, forced personal-name "
        "fields, profile completion, payment instruments) surface to main "
        "chat as owner decision items - never worked around."
    ],
}

HANDLE_STATES = {"recorded", "none-exists", "pending-registration",
                 "blocked-owner-gate", "unknown-verify"}
ENTRY_STATUSES = {"active", "registering", "pending", "blocked-owner-gate"}


def derive_moniker(platform_id, taken):
    """Deterministic moniker for platform_id given {moniker_lower: pid}."""
    base = ROLE + "".join(w.capitalize() for w in platform_id.split("-") if w)
    candidate, n = base, 2
    while taken.get(candidate.lower()) not in (None, platform_id):
        candidate = f"{base}{n}"
        n += 1
    return candidate


def canonical(entry):
    return f"{entry['role']}{{{entry['moniker']}}}[platform:{entry['platform_id']}]"


def split_sections(log_text):
    """{section_number: text} for '## N.' headed sections of the log."""
    parts = re.split(r"(?m)^## (\d+)\.", log_text)
    sections = {}
    for i in range(1, len(parts) - 1, 2):
        sections[int(parts[i])] = parts[i + 1]
    return sections


def packet_sections(log_text):
    """{packet_ref: section_text} for '### Dn' packets in log section 4."""
    sec4 = split_sections(log_text).get(4, "")
    parts = re.split(r"(?m)^### (D\d+)\b", sec4)
    packets = {}
    for i in range(1, len(parts) - 1, 2):
        packets[parts[i]] = parts[i + 1]
    return packets


def activated_platforms(log_text):
    """platform_ids whose alias appears in log section 1 or 4."""
    sections = split_sections(log_text)
    active_text = sections.get(1, "") + "\n" + sections.get(4, "")
    return {pid for alias, pid, _n, _k in ALIASES if alias in active_text}


def attribute_packets(log_text):
    """{packet_ref: [platform_id, ...]} by alias presence in packet text."""
    out = {}
    for ref, text in packet_sections(log_text).items():
        out[ref] = sorted({pid for alias, pid, _n, _k in ALIASES if alias in text})
    return out


def expected_monikers(entries):
    """Recompute every moniker by the rule, in platform_id sort order."""
    taken, expected = {}, {}
    for entry in sorted(entries, key=lambda e: e["platform_id"]):
        m = derive_moniker(entry["platform_id"], taken)
        expected[entry["platform_id"]] = m
        taken[m.lower()] = entry["platform_id"]
    return expected


def check(registry, log_text):
    """Return a list of drift/problem lines ([] == registry is sound)."""
    problems = []
    entries = registry.get("entries")
    if registry.get("schema") != SCHEMA or not isinstance(entries, list):
        return ["hard: registry schema missing or entries not a list"]
    ids = [e.get("platform_id") for e in entries]
    if len(ids) != len(set(ids)):
        problems.append("hard: duplicate platform_id in registry")
    expected = expected_monikers(entries)
    seen_monikers = {}
    for e in entries:
        pid = e.get("platform_id")
        for key in ("platform", "kind", "role", "moniker", "public_handle",
                    "handle_state", "status", "registrations", "handling"):
            if key not in e:
                problems.append(f"hard: {pid}: missing field {key}")
        if e.get("role") != ROLE:
            problems.append(f"hard: {pid}: role is {e.get('role')!r}, must be {ROLE!r}")
        if pid in ALIAS_BY_ID and e.get("platform") != ALIAS_BY_ID[pid][1]:
            problems.append(f"hard: {pid}: platform name drift")
        if e.get("moniker") != expected.get(pid):
            problems.append(
                f"hard: {pid}: moniker {e.get('moniker')!r} != rule-derived "
                f"{expected.get(pid)!r}")
        low = str(e.get("moniker", "")).lower()
        if low in seen_monikers and seen_monikers[low] != pid:
            problems.append(f"hard: {pid}: moniker collides with {seen_monikers[low]}")
        seen_monikers[low] = pid
        if e.get("handle_state") not in HANDLE_STATES:
            problems.append(f"hard: {pid}: bad handle_state {e.get('handle_state')!r}")
        if e.get("handle_state") == "recorded" and not e.get("public_handle"):
            problems.append(f"hard: {pid}: handle_state recorded but no handle")
        if e.get("handle_state") != "recorded" and e.get("public_handle"):
            problems.append(f"hard: {pid}: handle present but state is "
                            f"{e.get('handle_state')!r} (handles are recorded facts)")
        if e.get("status") not in ENTRY_STATUSES:
            problems.append(f"hard: {pid}: bad status {e.get('status')!r}")
        if pid in ALIAS_BY_ID and ALIAS_BY_ID[pid][0] not in log_text:
            problems.append(f"hard: {pid}: platform alias absent from the log (stale entry)")
    active = activated_platforms(log_text)
    for pid in sorted(active - set(ids)):
        problems.append(f"missing-entry:{pid}")
    claims = {}
    for e in entries:
        for reg in e.get("registrations", []):
            claims.setdefault(reg.get("ref"), []).append(e["platform_id"])
            if not re.search(rf"\b{re.escape(str(reg.get('ref')))}\b", log_text):
                problems.append(f"hard: {e['platform_id']}: ref {reg.get('ref')} "
                                "not found in the log")
    for ref in packet_sections(log_text):
        if ref not in claims:
            problems.append(f"unclaimed-packet:{ref}")
    return problems


def assign(registry, log_text):
    """Append entries for activated platforms lacking one. Returns added ids."""
    ids = {e["platform_id"] for e in registry["entries"]}
    missing = sorted(activated_platforms(log_text) - ids)
    if not missing:
        return []
    packets = attribute_packets(log_text)
    taken = {e["moniker"].lower(): e["platform_id"] for e in registry["entries"]}
    added = []
    for pid in missing:
        _alias, name, kind = ALIAS_BY_ID[pid]
        moniker = derive_moniker(pid, taken)
        taken[moniker.lower()] = pid
        regs = [{"ref": ref, "event": "", "aspect": "participant",
                 "status": "in-progress"}
                for ref, owners in sorted(packets.items()) if pid in owners]
        registry["entries"].append({
            "platform_id": pid,
            "platform": name,
            "kind": kind,
            "role": ROLE,
            "moniker": moniker,
            "public_handle": None,
            "handle_state": "unknown-verify",
            "status": "pending",
            "registrations": regs,
            "handling": json.loads(json.dumps(DEFAULT_HANDLING)),
            "notes": ["Auto-assigned by scripts/registration_monikers/registry.py; "
                      "handle_state stays unknown-verify until a lane records "
                      "the platform-side fact."],
        })
        added.append(pid)
    registry["entries"].sort(key=lambda e: e["platform_id"])
    return added


def render_table(registry):
    lines = [
        "| Platform | Role{Moniker} | Public handle | Status | Registrations | Owning lane |",
        "|---|---|---|---|---|---|",
    ]
    for e in sorted(registry["entries"], key=lambda x: x["platform_id"]):
        handle = e["public_handle"] if e["public_handle"] else f"— ({e['handle_state']})"
        regs = ", ".join(r["ref"] for r in e["registrations"]) or "—"
        lines.append(
            f"| {e['platform']} | `{canonical(e)}` | {handle} | {e['status']} "
            f"| {regs} | {e['handling']['owner_lane']} |")
    return "\n".join(lines)


def render_doc(doc_text, registry):
    begin, end = "<!-- registry:begin -->", "<!-- registry:end -->"
    if begin not in doc_text or end not in doc_text:
        raise SystemExit("doc is missing the registry markers")
    table = render_table(registry)
    return re.sub(re.escape(begin) + r".*?" + re.escape(end),
                  begin + "\n\n" + table + "\n\n" + end, doc_text, flags=re.S)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["check", "assign", "render"])
    ap.add_argument("--registry", default="config/registration_monikers.json")
    ap.add_argument("--log", default="docs/ops/CHALLENGE-ENTRIES-LOG.md")
    ap.add_argument("--doc", default="docs/ops/4N0N-REGISTRATION-PROTOCOL.md")
    args = ap.parse_args(argv)

    registry = json.load(open(args.registry))
    log_text = open(args.log).read()

    if args.mode == "check":
        problems = check(registry, log_text)
        for p in problems:
            print(p)
        print(f"check: {len(problems)} problem(s), "
              f"{len(registry.get('entries', []))} entries")
        return 1 if problems else 0
    if args.mode == "assign":
        added = assign(registry, log_text)
        if added:
            json.dump(registry, open(args.registry, "w"), indent=2)
            open(args.registry, "a").write("\n")
        print(json.dumps({"added": added}))
        return 0
    if args.mode == "render":
        doc = render_doc(open(args.doc).read(), registry)
        open(args.doc, "w").write(doc)
        print("rendered registry table into", args.doc)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
