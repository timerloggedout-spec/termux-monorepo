#!/usr/bin/env python3
"""Registration moniker registry tool — the 4n0n protocol's machine half.

One Role{Moniker} per challenge registration/platform, per
docs/ops/4N0N-REGISTRATION-PROTOCOL.md. The registry of record is
config/registration_monikers.json; the registration source of truth is
docs/ops/CHALLENGE-ENTRIES-LOG.md. This tool:

  check   validate the registry against the log, the assignment rule,
          and the Profile Registry (exit 1 on any drift; drift lines are
          machine-readable)
  assign  append entries for platforms the log has activated (a platform
          named in log section 1 or 4) that have no registry entry yet —
          moniker derived by rule; the entry references the platform's
          profile in docs/ops/PROFILE-REGISTRY.md by pointer and carries
          no profile data of its own (one home per fact)
  render  regenerate the registry table inside the protocol doc from the
          JSON (between the registry:begin / registry:end markers)
  derive  print the assignment for one platform_id (the registry entry
          if one exists, else the rule-v2 result) - the account-creation
          lane's instant lookup path; ratified into the registry by PR

Moniker assignment rule v2 (deterministic): entries are processed in
platform_id sort order; moniker = the 4n0n stem "n0n" + the platform_id's
words capitalized and joined, dropping filler words (STOPWORDS: ai, io,
center) in non-first positions ("aws-builder-center" -> "n0nAwsBuilder",
"lablab-ai" -> "n0nLablab", "builder-io" -> "n0nBuilder"). On collision
with a different platform_id, append the smallest integer >= 2 that
frees the token. Canonical form: <role>{<moniker>}[platform:<platform_id>]
with role "entrant" (challenge platforms) or "account" (provider
accounts). The result is username-grade: alphanumeric, letter-led,
short - the account-creation lane uses it verbatim as the signup
username, pulled from this registry, never invented at a form.

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

ROLES = {"entrant", "account"}
DEFAULT_ROLE = {"log": "entrant", "fleet": "account"}
STEM = "n0n"
STOPWORDS = {"ai", "io", "center"}
SCHEMA = "registration-monikers/3"
PROFILE_REGISTRY = "docs/ops/PROFILE-REGISTRY.md"

# (alias string, platform_id, platform display name, kind, class)
# class "log":   detected in / attributed from the challenge log
#                (activation = named in its sections 1/4).
# class "fleet": fleet platforms registered by their owning lane
#                (provider accounts for the account-creation lane);
#                never log-detected, never stale-checked against it.
ALIASES = [
    ("AWS Builder Center", "aws-builder-center", "AWS Builder Center", "platform", "log"),
    ("Builder.io", "builder-io", "Builder.io", "platform", "log"),
    ("lablab.ai", "lablab-ai", "lablab.ai", "platform", "log"),
    ("Vultr", "vultr", "Vultr", "platform", "log"),
    ("Devpost", "devpost", "Devpost", "platform", "log"),
    ("Kiro", "kiro", "Kiro", "identity-provider", "log"),
    ("PayPal", "paypal", "PayPal", "platform", "log"),
    ("Lexsi", "lexsi", "Lexsi", "platform", "log"),
    ("Hugging Face", "hugging-face", "Hugging Face", "platform", "log"),
    ("Cohere", "cohere", "Cohere", "provider", "fleet"),
    ("Aion", "aion", "Aion", "provider", "fleet"),
    ("LLM7", "llm7", "LLM7", "provider", "fleet"),
    ("Requesty", "requesty", "Requesty", "provider", "fleet"),
    ("Routeway", "routeway", "Routeway", "provider", "fleet"),
    ("UnoRouter", "uno-router", "UnoRouter", "provider", "fleet"),
    ("SeaLion", "sea-lion", "SeaLion", "provider", "fleet"),
    ("Kilo", "kilo", "Kilo", "provider", "fleet"),
    ("ZAI", "zai", "ZAI", "provider", "fleet"),
    ("ModelScope", "model-scope", "ModelScope", "provider", "fleet"),
    ("SiliconFlow", "silicon-flow", "SiliconFlow", "provider", "fleet"),
    ("iFlytek", "iflytek", "iFlytek", "provider", "fleet"),
    ("xKiro", "xkiro", "xKiro", "provider", "fleet"),
    ("Dream In Production", "dream-in-production", "Dream In Production", "page", "fleet"),
    ("Receipts Count", "receipts-count", "Receipts Count", "page", "fleet"),
    ("Code, Not Card", "code-not-card", "Code, Not Card", "page", "fleet"),
]
ALIAS_BY_ID = {pid: (alias, name, kind, aclass)
               for alias, pid, name, kind, aclass in ALIASES}
LOG_ALIASES = [(a, p) for a, p, _n, _k, c in ALIASES if c == "log"]

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

ENTRY_STATUSES = {"active", "registering", "pending", "blocked-owner-gate"}
# Profile data (handles, display names, completeness) lives ONLY in the
# Profile Registry. An entry carrying any of these keys is duplication
# and fails check.
PROFILE_DATA_KEYS = {"public_handle", "handle_state", "display_name",
                     "profile_url", "avatar", "bio"}


def derive_moniker(platform_id, taken):
    """Deterministic moniker (rule v2) given {moniker_lower: pid}."""
    words = [w for w in platform_id.split("-") if w]
    core = [w for i, w in enumerate(words) if i == 0 or w not in STOPWORDS]
    base = STEM + "".join(w.capitalize() for w in core)
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
    return {pid for alias, pid in LOG_ALIASES if alias in active_text}


def attribute_packets(log_text):
    """{packet_ref: [platform_id, ...]} by alias presence in packet text."""
    out = {}
    for ref, text in packet_sections(log_text).items():
        out[ref] = sorted({pid for alias, pid in LOG_ALIASES if alias in text})
    return out


def expected_monikers(entries):
    """Recompute every moniker by the rule, in platform_id sort order."""
    taken, expected = {}, {}
    for entry in sorted(entries, key=lambda e: e["platform_id"]):
        m = derive_moniker(entry["platform_id"], taken)
        expected[entry["platform_id"]] = m
        taken[m.lower()] = entry["platform_id"]
    return expected


def profile_headings(profiles_text):
    """Heading labels of the Profile Registry's profile sections."""
    return [m.group(1).strip() for m in
            re.finditer(r"(?m)^####\s+(.+)$", profiles_text)]


def check(registry, log_text, profiles_text):
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
    headings = profile_headings(profiles_text)
    for e in entries:
        pid = e.get("platform_id")
        for key in ("platform", "kind", "role", "moniker", "profile_ref",
                    "status", "registrations", "handling"):
            if key not in e:
                problems.append(f"hard: {pid}: missing field {key}")
        for key in PROFILE_DATA_KEYS & set(e):
            problems.append(f"hard: {pid}: carries profile data key {key!r} - "
                            f"profile data lives only in {PROFILE_REGISTRY}")
        ref = e.get("profile_ref")
        if ref is None:
            if not e.get("profile_pending"):
                problems.append(f"hard: {pid}: profile_ref is null but no "
                                "profile_pending names the lane that will "
                                "register the profile")
        elif not any(h == ref or h.startswith(ref + " ") or
                     h.startswith(ref + " —") for h in headings):
            problems.append(f"hard: {pid}: profile_ref {ref!r} does not resolve "
                            f"to a profile heading in {PROFILE_REGISTRY}")
        if e.get("role") not in ROLES:
            problems.append(f"hard: {pid}: role is {e.get('role')!r}, "
                            f"must be one of {sorted(ROLES)}")
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
        if e.get("status") not in ENTRY_STATUSES:
            problems.append(f"hard: {pid}: bad status {e.get('status')!r}")
        if (pid in ALIAS_BY_ID and ALIAS_BY_ID[pid][3] == "log"
                and ALIAS_BY_ID[pid][0] not in log_text):
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
        _alias, name, kind, _aclass = ALIAS_BY_ID[pid]
        moniker = derive_moniker(pid, taken)
        taken[moniker.lower()] = pid
        regs = [{"ref": ref, "event": "", "aspect": "participant",
                 "status": "in-progress"}
                for ref, owners in sorted(packets.items()) if pid in owners]
        registry["entries"].append({
            "platform_id": pid,
            "platform": name,
            "kind": kind,
            "role": DEFAULT_ROLE["log"],
            "moniker": moniker,
            "profile_ref": name,
            "status": "pending",
            "registrations": regs,
            "handling": json.loads(json.dumps(DEFAULT_HANDLING)),
            "notes": ["Auto-assigned by scripts/registration_monikers/registry.py. "
                      "profile_ref names the platform's heading in "
                      "docs/ops/PROFILE-REGISTRY.md by convention; if no such "
                      "profile exists yet, check fails until the owning lane "
                      "registers it there. No profile data is carried here."],
        })
        added.append(pid)
    registry["entries"].sort(key=lambda e: e["platform_id"])
    return added


def render_table(registry):
    lines = [
        "| Platform | Role{Moniker} | Profile (Profile Registry heading) | Status | Registrations | Owning lane |",
        "|---|---|---|---|---|---|",
    ]
    for e in sorted(registry["entries"], key=lambda x: x["platform_id"]):
        regs = ", ".join(r["ref"] for r in e["registrations"]) or "—"
        profile = e["profile_ref"] or f"— (pending: {e.get('profile_pending', '?')})"
        lines.append(
            f"| {e['platform']} | `{canonical(e)}` | {profile} | {e['status']} "
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
    ap.add_argument("mode", choices=["check", "assign", "render", "derive"])
    ap.add_argument("--platform-id", help="derive mode: platform_id slug to assign")
    ap.add_argument("--role", choices=sorted(ROLES),
                    help="derive mode: role override (default: by alias class)")
    ap.add_argument("--registry", default="config/registration_monikers.json")
    ap.add_argument("--log", default="docs/ops/CHALLENGE-ENTRIES-LOG.md")
    ap.add_argument("--profiles", default=PROFILE_REGISTRY)
    ap.add_argument("--doc", default="docs/ops/4N0N-REGISTRATION-PROTOCOL.md")
    args = ap.parse_args(argv)

    registry = json.load(open(args.registry))
    log_text = open(args.log).read()

    if args.mode == "derive":
        if not args.platform_id:
            ap.error("derive mode requires --platform-id")
        pid = args.platform_id
        existing = {e["platform_id"]: e for e in registry["entries"]}
        if pid in existing:
            e = existing[pid]
            print(json.dumps({"platform_id": pid, "moniker": e["moniker"],
                              "canonical": canonical(e), "source": "registry"}))
            return 0
        taken = {e["moniker"].lower(): e["platform_id"]
                 for e in registry["entries"]}
        aclass = ALIAS_BY_ID.get(pid, (None, None, None, "fleet"))[3]
        role = args.role or DEFAULT_ROLE[aclass]
        moniker = derive_moniker(pid, taken)
        print(json.dumps({"platform_id": pid, "moniker": moniker,
                          "canonical": f"{role}{{{moniker}}}[platform:{pid}]",
                          "source": "rule-v2 (not yet in registry)"}))
        return 0
    if args.mode == "check":
        problems = check(registry, log_text, open(args.profiles).read())
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
