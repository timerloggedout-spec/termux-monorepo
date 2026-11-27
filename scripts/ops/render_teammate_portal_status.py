#!/usr/bin/env python3
"""Render the Teammate Portal (hackathon-desk) reference + status page.

Reads the proposal docs and ITEMS.md done-board from the checkout and the
live PR / dispatch-issue state from the GitHub API (read-only), and writes
static HTML. Contract: docs/ops/REVIEW-PUBLISHING.md.
"""
import argparse, datetime as dt, html, json, os, pathlib, re, subprocess

import markdown

DOCS = {
    "plan": ("Implementation plan", "docs/superpowers/plans/2026-11-24-hackathon-desk.md"),
    "spec": ("Design spec", "docs/superpowers/specs/2026-11-24-hackathon-desk-design.md"),
    "manifest": ("Manifest", "docs/proposals/active/hackathon-desk/MANIFEST.md"),
    "items": ("Items (done-board source)", "docs/proposals/active/hackathon-desk/ITEMS.md"),
    "icm-route": ("ICM route", "docs/proposals/active/hackathon-desk/ICM-ROUTE.md"),
}
CSS = ("body{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;line-height:1.5}"
       "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:.35rem;vertical-align:top}"
       ".s-done{background:#e6f4ea}.s-blocked{background:#fdecea}.s-pending{background:#fff8e1}"
       "a:focus,button:focus{outline:3px solid #1a73e8}")


def page(title, body, locale="en"):
    direction = "rtl" if locale == "ur" else "ltr"
    base = "../" if locale == "ur" else "./"
    nav = (
        '<nav aria-label="Language">'
        f'<span>{html.escape("زبان" if locale == "ur" else "Language")}</span> '
        f'<a href="{base}index.html" lang="en" hreflang="en">English</a> · '
        f'<a href="{base}ur/index.html" lang="ur" hreflang="ur" aria-current="{"page" if locale == "ur" else "false"}">اردو</a>'
        '</nav>'
    )
    rtl_css = "body{direction:rtl;text-align:right} main{unicode-bidi:plaintext} code,pre,a[dir=ltr]{direction:ltr;unicode-bidi:isolate}"
    style = CSS + (rtl_css if locale == "ur" else "")
    return (f'<!doctype html><html lang="{locale}" dir="{direction}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>{style}</style></head>'
            f'<body><main>{nav}{body}</main></body></html>')


def gh(path):
    try:
        return json.loads(subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout)
    except Exception:
        return None


def items(md):
    rows = []
    for line in md.splitlines():
        m = re.match(r"\|\s*(HD-\d+)\s*\|(.*)\|(.*)\|(.*)\|\s*$", line)
        if m:
            rows.append([c.strip() for c in (m.group(1), m.group(2), m.group(3), m.group(4))])
    return rows


def klass(state):
    s = state.lower()
    if s.startswith(("implemented", "done", "verified", "merged")):
        return "s-done"
    if s.startswith("blocked"):
        return "s-blocked"
    return "s-pending"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--source-ref", required=True)
    ap.add_argument("--source-sha", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for key, (title, path) in DOCS.items():
        p = pathlib.Path(path)
        body = markdown.markdown(p.read_text(), extensions=["tables", "fenced_code"]) if p.exists() else "<p>Missing at this ref.</p>"
        (out / f"{key}.html").write_text(page(f"Teammate Portal · {title}", f'<p><a href="./">← Status</a></p>{body}'))
    rows = items(pathlib.Path(DOCS["items"][1]).read_text()) if pathlib.Path(DOCS["items"][1]).exists() else []
    done = sum(1 for r in rows if klass(r[3]) == "s-done")
    pr = gh(f"repos/{a.repo}/pulls/{a.pr}") or {}
    pr_state = "merged" if pr.get("merged_at") else (pr.get("state") or "unknown")
    issues = gh(f"repos/{a.repo}/issues?labels=teammate-portal&state=all&per_page=20") or []
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    tr = "".join(
        f'<tr class="{klass(r[3])}"><td>{html.escape(r[0])}</td><td>{html.escape(r[1])}</td>'
        f"<td>{html.escape(r[2])}</td><td><strong>{html.escape(r[3])}</strong></td></tr>" for r in rows)
    it = "".join(
        f'<li><a href="{html.escape(i["html_url"])}">#{i["number"]}</a> {html.escape(i["title"])} — '
        f'{html.escape(i["state"])}; labels: {html.escape(", ".join(l["name"] for l in i.get("labels", [])))}</li>'
        for i in issues if "pull_request" not in i) or "<li>None filed yet.</li>"
    docs = "".join(f'<li><a href="{k}.html">{html.escape(t)}</a></li>' for k, (t, _) in DOCS.items())
    body = (
        "<h1>Teammate Portal — reference &amp; status</h1>"
        "<p>Opportunities ∧ challenges ∧ hackathons. Proposal <code>hackathon-desk</code>. "
        "Standalone surface, separate from Tribute.</p>"
        f'<p role="status">Done <strong>{done}/{len(rows)}</strong> · PR '
        f'<a href="https://github.com/{a.repo}/pull/{a.pr}">#{a.pr}</a> {html.escape(pr_state)} · '
        f"source <code>{html.escape(a.source_ref)}</code> @ <code>{a.source_sha[:7]}</code> · rendered {now}</p>"
        "<h2>Done-board</h2><table><thead><tr><th>ID</th><th>Work item</th><th>Acceptance evidence</th>"
        f"<th>State</th></tr></thead><tbody>{tr}</tbody></table>"
        f"<h2>Dispatch (label <code>teammate-portal</code>)</h2><ul>{it}</ul>"
        f"<h2>Reference</h2><ul>{docs}</ul>"
        "<h2>Route</h2><p>Project-task filing ⇒ swarm-admission ⇒ project-task-dispatch ⇒ build-dispatch ⇒ PR ⇒ "
        "this page via <code>teammate-portal-status-publish.yml</code>. Contract: "
        f'<a href="https://github.com/{a.repo}/blob/master/docs/ops/REVIEW-PUBLISHING.md">REVIEW-PUBLISHING</a>.</p>'
    )
    (out / "index.html").write_text(page("Teammate Portal · reference & status", body, "en"))

    # Publish a parallel Urdu shell; source documents remain explicitly English fallbacks.
    urdu_dir = out / "ur"
    urdu_dir.mkdir(parents=True, exist_ok=True)
    urdu_body = body
    replacements = [
        ("Teammate Portal — reference &amp; status", "ٹیم میٹ پورٹل — حوالہ اور صورتحال"),
        ("Opportunities ∧ challenges ∧ hackathons.", "مواقع، چیلنجز اور ہیکاتھون۔"),
        ("Standalone surface, separate from Tribute.", "یہ ایک الگ پورٹل ہے اور Tribute سے علیحدہ ہے۔"),
        ("Done <strong>", "مکمل <strong>"),
        ("source <code>", "ماخذ <code>"),
        ("<h2>Done-board</h2>", "<h2>مکمل کام</h2>"),
        ("<h2>Dispatch (label", "<h2>کام کی ترسیل (لیبل"),
        ("<h2>Reference</h2>", "<h2>حوالہ</h2>"),
        ("<h2>Route</h2>", "<h2>طریقۂ کار</h2>"),
        ("<p>None filed yet.</p>", "<p>ابھی کوئی درخواست درج نہیں ہوئی۔</p>")
    ]
    for source, translated in replacements:
        urdu_body = urdu_body.replace(source, translated)
    urdu_body = (
        '<p lang="ur" dir="rtl">یہ صفحہ اردو میں دستیاب ہے۔ حوالہ جاتی دستاویزات فی الحال انگریزی میں ہیں۔ '
        '<a href="../plan.html" lang="en" dir="ltr">English reference documents</a></p>' + urdu_body
    )
    for key, (_, _) in DOCS.items():
        urdu_body = urdu_body.replace(f'href="{key}.html"', f'href="../{key}.html"')
    (urdu_dir / "index.html").write_text(
        page("ٹیم میٹ پورٹل — حوالہ اور صورتحال", urdu_body, "ur")
    )


if __name__ == "__main__":
    main()
