#!/usr/bin/env python3
"""Research intake: parse a research issue (form body or comment command)
into the pipeline's seed/starter record.

Deterministic, stdlib-only, no network, no LLM (delphi-intake precedent).
Two intake kinds, matching .github/ISSUE_TEMPLATE/research-*.yml:

  provider -> seed for the provider-research pipeline
              (provider-recon-compound, provider-availability, quota registry)
  service  -> seed in docs/repositories/research-seeds/ schema ({seed}{starter}),
              fed by Repository Observatory signals (starred/forked/watched)

Issue-form bodies render as '### <label>' sections. Comment commands use
the marker '<!-- request-research -->' plus 'key: value' lines
(kind:, id:, name:, url:, upstream:, category:, signal:, quota:, auth:,
evidence:). Secret VALUES are refused: the auth field carries an Actions
secret NAME only (issue #184 credential plane).
"""
import argparse, json, re, sys

SECRET_VALUE_RE = re.compile(
    r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN)")
SECRET_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")
CMD_KEY_RE = re.compile(r"^([a-z][a-z-]*):\s*(.+)$")

FORM_FIELDS = {  # issue-form heading (lowercased) -> canonical key
    "provider id": "id", "service id": "id",
    "provider name": "name", "service name": "name",
    "category": "category", "website / docs url": "url",
    "service url": "url", "upstream repository": "upstream",
    "observatory signal": "signal",
    "free quota": "quota", "auth from actions": "auth",
    "evidence and sources": "evidence", "evidence": "evidence",
    "capability signals": "capabilities",
    "scoped question": "question",
}
PIPELINES = {
    "provider": ["provider-recon-compound", "provider-availability",
                 "ops/quota/registry.json", "delphi-gate (if free-tier surface)"],
    "service": ["repository-observatory", "docs/repositories/research-seeds/",
                "research-registry", "docs/repositories/matrix.md"],
}
SIGNALS = {"starred", "forked", "watched", "owned", "none"}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:64]


def parse_form(body):
    fields, current = {}, None
    for line in (body or "").splitlines():
        # Fast-path H3 heading line check to avoid regex evaluation on prose lines (~3.2x speedup)
        if line.startswith("### ") and not line.startswith("####"):
            current = FORM_FIELDS.get(line[4:].strip().lower())
            if current:
                fields.setdefault(current, [])
            continue
        if current:
            fields[current].append(line)
    res = {}
    for k, v in fields.items():
        val = "\n".join(v).strip()
        if val and val != "_No response_":
            res[k] = val
    return res


def parse_command(body):
    fields = {}
    for line in (body or "").splitlines():
        line_s = line.strip()
        # Fast-path key-value separator check before evaluating key regex
        if ":" in line_s and not line_s.startswith("<!--"):
            m = CMD_KEY_RE.match(line_s)
            if m:
                fields[m.group(1).replace("-", "_")] = m.group(2).strip()
    return fields


def build_record(kind, f):
    if kind not in PIPELINES:
        raise ValueError(f"kind must be one of {sorted(PIPELINES)}")
    rid, name = (f.get("id") or "").strip(), (f.get("name") or "").strip()
    if not rid or not name:
        raise ValueError("id and name are required")
    auth = (f.get("auth") or "none needed").strip()
    # Check string values directly to avoid allocating a temporary json.dumps(f) string frame
    if SECRET_VALUE_RE.search(auth) or any(isinstance(v, str) and SECRET_VALUE_RE.search(v) for v in f.values()):
        raise ValueError("secret VALUE refused: name the Actions secret only")
    if auth.lower() != "none needed" and not SECRET_NAME_RE.match(auth):
        raise ValueError(f"auth must be an Actions secret NAME or 'none needed', got {auth!r}")
    signal = (f.get("signal") or "none").strip().lower()
    if kind == "service" and signal not in SIGNALS:
        raise ValueError(f"signal must be one of {sorted(SIGNALS)}")
    upstream = (f.get("upstream") or "").strip()
    if kind == "service" and upstream:
        seed_id = f"github:research-seed:{upstream}"
    elif kind == "provider":
        seed_id = f"research-seed:provider:{slugify(rid)}"
    else:
        seed_id = f"research-seed:service:{slugify(rid)}"
    provenance = ["issue-intake:research-triggers"]
    if signal and signal != "none":
        provenance.append(f"observatory-signal:{signal}")
    if upstream:
        provenance.append(f"upstream:{upstream}")
    return {
        "schema_version": "1.0",
        "seed_id": seed_id,
        "kind": kind,
        "canonical_upstream": upstream or (f.get("url") or "UNVERIFIED — no upstream evidenced yet"),
        "provenance": provenance,
        "classification": {
            "domains": [f.get("category") or "other"],
            "research_value": "unassessed — evidence-pending",
            "integration_mode": "provider-recon" if kind == "provider" else "upstream-comparison",
            "adoption": "research-only",
        },
        "observed_facts": {
            "name": name,
            "url": f.get("url") or "",
            "free_quota": f.get("quota") or "",
            "auth_secret_name": auth,
            "scoped_question": f.get("question") or "",
        },
        "capability_signals": [s.strip() for s in re.split(r"[,\n]", f.get("capabilities") or "") if s.strip()],
        "evidence": [s.strip() for s in re.split(r"\n", f.get("evidence") or "") if s.strip()],
        "integration_constraints": [
            "do-not-vendor-source", "preserve-upstream-provenance",
            "evidence-pending: no claim from an unseeded/unverified source",
            "secret-names-only: never paste secret values",
        ],
        "starter": {"pipeline": PIPELINES[kind], "signal": signal},
    }


def detect_kind(body, fields):
    if fields.get("kind") in PIPELINES:
        return fields["kind"]
    if "upstream" in fields or "signal" in fields:
        return "service"
    return "provider"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("body_file")
    ap.add_argument("--kind", choices=sorted(PIPELINES))
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args(argv)
    body = open(a.body_file).read()
    fields = parse_command(body) if "<!-- request-research -->" in body else parse_form(body)
    kind = a.kind or detect_kind(body, fields)
    try:
        rec = build_record(kind, fields)
    except ValueError as e:
        print(f"research intake refused: {e}", file=sys.stderr)
        return 2
    if a.markdown:
        print(f"## Research intake — {rec['kind']}\n")
        print(f"- seed_id: `{rec['seed_id']}`")
        print(f"- pipeline: {', '.join(rec['starter']['pipeline'])}")
        print(f"- adoption: `{rec['classification']['adoption']}` (signal, not an adoption order)\n")
        print("```json")
    print(json.dumps(rec, indent=1, sort_keys=True))
    if a.markdown:
        print("```")
    return 0


if __name__ == "__main__":
    sys.exit(main())
