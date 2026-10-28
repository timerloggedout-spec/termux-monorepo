#!/usr/bin/env python3
"""APK cross-reference intake: parse an apk-xref issue form body into the
cross-reference record (docs/ops/APK-XREF-TEMPLATES.md).

Deterministic, stdlib-only, no network, no LLM (research-intake precedent).
Two kinds, from .github/ISSUE_TEMPLATE/apk-cross-reference*.yml:
  request  — paired repo brief + artifact source; wakes the Foundry run.
  findings — manifest/endpoints/claims/divergences-as-results + verdict.
A filing is identified as findings when it carries a verdict field.
Validation: paired/cross-reference issue refs (#NNNN or issue URL),
package-id shape when present, submitter Role{Moniker} pattern, and —
for findings — both divergence directions present ('none found' is a
valid explicit value). Secret VALUES are refused (names only plane).
"""
import argparse, json, re, sys

SECRET_VALUE_RE = re.compile(
    r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN)")
ISSUE_REF_RE = re.compile(r"^(#\d+|https://github\.com/[^/]+/[^/]+/issues/\d+)$")
PACKAGE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z0-9_]+)+$")
SUBMITTER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*\{[A-Za-z0-9][A-Za-z0-9_-]*\}$")
VERDICTS = {"match", "divergences-found", "no-artifact-found"}

FORM_FIELDS = {
    "target id": "target_id", "paired repo brief": "paired_repo_brief",
    "cross-reference issue": "xref_issue", "target repo url": "target",
    "artifact source": "artifact_source", "artifact version + build": "artifact_version",
    "package id": "package_id", "authorization basis": "basis",
    "scope domains": "scope_domains", "side effect": "side_effect",
    "state-changing authorization": "state_changing", "probe budget": "probe_budget",
    "execution venue": "venue", "evidence expectation": "evidence_expectation",
    "evidence expectation met": "evidence_expectation",
    "source claims to check": "claims_to_check",
    "manifest permissions": "manifest_permissions",
    "endpoints actually observed": "endpoints_observed",
    "source claims checked": "claims_checked",
    "divergences — repo to apk": "divergences_repo_to_apk",
    "divergences — apk to repo": "divergences_apk_to_repo",
    "verdict": "verdict", "submitter role{moniker}": "submitter",
    "notes for the dispatcher": "notes", "notes": "notes",
}


def parse_form(body):
    fields, current = {}, None
    for line in (body or "").splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            current = FORM_FIELDS.get(m.group(1).strip().lower())
            if current:
                fields.setdefault(current, [])
            continue
        if current:
            fields[current].append(line)
    return {k: "\n".join(v).strip() for k, v in fields.items()
            if "\n".join(v).strip() not in ("", "_No response_")}


def lines(value):
    return [s.strip() for s in (value or "").splitlines() if s.strip()]


def build_record(f):
    if SECRET_VALUE_RE.search(json.dumps(f)):
        raise ValueError("secret VALUE refused: names only")
    target_id = (f.get("target_id") or "").strip()
    submitter = (f.get("submitter") or "").strip()
    if not target_id:
        raise ValueError("target_id is required")
    if not SUBMITTER_RE.match(submitter):
        raise ValueError(f"submitter must be Role{{Moniker}}, got {submitter!r}")
    pkg = (f.get("package_id") or "").strip()
    kind = "findings" if (f.get("verdict") or "").strip() else "request"
    base = {"schema": "apk-xref/v1", "kind": kind, "target_id": target_id,
            "artifact_source": (f.get("artifact_source") or "").strip(),
            "artifact_version": (f.get("artifact_version") or "").strip(),
            "package_id": pkg, "evidence_expectation": (f.get("evidence_expectation") or "").strip(),
            "submitter": submitter, "notes": f.get("notes") or ""}
    if pkg and pkg != "none" and not PACKAGE_RE.match(pkg):
        raise ValueError(f"package_id shape invalid: {pkg!r}")
    if kind == "request":
        ref = (f.get("paired_repo_brief") or "").strip()
        if not ISSUE_REF_RE.match(ref):
            raise ValueError("paired_repo_brief must be an issue reference (#NNNN or issue URL)")
        if (f.get("side_effect") or "read").strip() == "write" and (f.get("state_changing") or "no").strip() != "yes":
            raise ValueError("write filing requires state-changing authorization = yes")
        base.update({"paired_repo_brief": ref, "target": (f.get("target") or "").strip(),
                     "authorization_basis": f.get("basis") or "",
                     "scope_domains": [s.strip() for s in (f.get("scope_domains") or "").split(",") if s.strip()],
                     "side_effect": (f.get("side_effect") or "read").strip(),
                     "state_changing": (f.get("state_changing") or "no").strip(),
                     "probe_budget": (f.get("probe_budget") or "").strip(),
                     "venue": (f.get("venue") or "").strip(),
                     "claims_to_check": lines(f.get("claims_to_check"))})
    else:
        ref = (f.get("xref_issue") or "").strip()
        if not ISSUE_REF_RE.match(ref):
            raise ValueError("xref_issue must be an issue reference (#NNNN or issue URL)")
        verdict = f["verdict"].strip()
        if verdict not in VERDICTS:
            raise ValueError(f"verdict must be one of {sorted(VERDICTS)}")
        if not pkg:
            raise ValueError("findings require package_id")
        if verdict == "no-artifact-found" and pkg == "none":
            base["package_id"] = ""  # no artifact exists; evidence lives in notes
        for key in ("divergences_repo_to_apk", "divergences_apk_to_repo"):
            if not lines(f.get(key)):
                raise ValueError(f"{key} is required ('none found' is a valid explicit value)")
        base.update({"xref_issue": ref, "verdict": verdict,
                     "manifest_permissions": lines(f.get("manifest_permissions")),
                     "endpoints_observed": lines(f.get("endpoints_observed")),
                     "claims_checked": lines(f.get("claims_checked")),
                     "divergences_repo_to_apk": lines(f.get("divergences_repo_to_apk")),
                     "divergences_apk_to_repo": lines(f.get("divergences_apk_to_repo"))})
    return base


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("body_file")
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args(argv)
    try:
        rec = build_record(parse_form(open(a.body_file).read()))
    except ValueError as e:
        print(f"apk-xref intake refused: {e}", file=sys.stderr)
        return 2
    if a.markdown:
        print(f"## APK cross-reference intake — {rec['kind']}\n")
        print(f"- target: `{rec['target_id']}`")
        ref = rec.get("paired_repo_brief") or rec.get("xref_issue")
        print(f"- paired issue: {ref}")
        if rec["kind"] == "findings":
            print(f"- verdict: `{rec['verdict']}`")
        print()
        print("```json")
    print(json.dumps(rec, indent=1, sort_keys=True))
    if a.markdown:
        print("```")
    return 0


if __name__ == "__main__":
    sys.exit(main())
