#!/usr/bin/env python3
"""Render the Teammate Portal reference and status pages in English and Urdu.

Reads proposal documents from the selected source checkout and localization
assets from the repository-owned catalogs. The Urdu page remains a preview
until its manifest records human approval and publication.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import os
import pathlib
import re
import subprocess

import markdown

DOCS = {
    "plan": ("Implementation plan", "docs/superpowers/plans/2026-11-24-hackathon-desk.md"),
    "spec": ("Design spec", "docs/superpowers/specs/2026-11-24-hackathon-desk-design.md"),
    "manifest": ("Manifest", "docs/proposals/active/hackathon-desk/MANIFEST.md"),
    "items": ("Items (done-board source)", "docs/proposals/active/hackathon-desk/ITEMS.md"),
    "icm-route": ("ICM route", "docs/proposals/active/hackathon-desk/ICM-ROUTE.md"),
}
CSS = (
    "body{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;line-height:1.5}"
    "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:.35rem;vertical-align:top}"
    ".s-done{background:#e6f4ea}.s-blocked{background:#fdecea}.s-pending{background:#fff8e1}"
    ".review-status{padding:.75rem;border-inline-start:4px solid #b7791f;background:#fff8e1}"
    "a:focus,button:focus{outline:3px solid #1a73e8}"
)


def repository_root(root=None):
    configured = root or os.environ.get("POLYGLOT_REPO_ROOT")
    return pathlib.Path(configured).resolve() if configured else pathlib.Path(__file__).resolve().parents[2]


def load_manifest(root=None):
    path = repository_root(root) / "localization" / "manifests" / "teammate-portal.json"
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_hash(path):
    data = path.read_bytes()
    header = b"blob " + str(len(data)).encode("ascii") + bytes([0])
    return hashlib.sha1(header + data).hexdigest()


def translation_is_fresh(locale, root=None):
    if locale == "en":
        return True
    root_path = repository_root(root)
    try:
        manifest = load_manifest(root_path)
    except FileNotFoundError:
        return False
    translation = next(
        (item for item in manifest["translations"] if item["locale"] == locale),
        None,
    )
    if translation is None:
        return False
    source_catalog = root_path / translation.get(
        "source_catalog",
        "localization/catalogs/teammate-portal/en.json",
    )
    return bool(
        source_catalog.is_file()
        and translation["freshness"].get("state") == "fresh"
        and translation["freshness"].get("source_hash") == f"git-blob:{git_blob_hash(source_catalog)}"
    )


def load_catalog(locale, root=None):
    root_path = repository_root(root)
    catalog_dir = root_path / "localization" / "catalogs" / "teammate-portal"
    source_path = catalog_dir / "en.json"
    source_messages = json.loads(source_path.read_text(encoding="utf-8"))["messages"]
    if locale == "en" or not translation_is_fresh(locale, root_path):
        return source_messages

    target_path = catalog_dir / f"{locale}.json"
    if not target_path.is_file():
        return source_messages
    target_messages = json.loads(target_path.read_text(encoding="utf-8"))["messages"]
    return {**source_messages, **target_messages}


def review_notice(locale, root=None):
    try:
        manifest = load_manifest(root)
    except FileNotFoundError:
        return ""
    translation = next(
        (item for item in manifest["translations"] if item["locale"] == locale),
        None,
    )
    if translation is None:
        return ""
    review_status = translation["review"]["status"]
    publication_state = translation["publication"]
    if review_status == "approved" and publication_state == "published":
        return ""
    messages = load_catalog(locale, root)
    label = messages.get("status.review_required", "Translation review required")
    return (
        f'<p class="review-status" role="status" '
        f'data-review-status="{html.escape(review_status)}" '
        f'data-publication-state="{html.escape(publication_state)}">'
        f'{html.escape(label)} '
        f'<span class="review-state">{html.escape(review_status)} · {html.escape(publication_state)}</span></p>'
    )


def page(title, body, locale="en", title_key=None, root=None):
    content_locale = locale if translation_is_fresh(locale, root) else "en"
    direction = "rtl" if content_locale == "ur" else "ltr"
    english_href = "../index.html" if locale == "ur" else "./index.html"
    urdu_href = "./index.html" if locale == "ur" else "./ur/index.html"
    messages = load_catalog(locale, root)
    if title_key:
        title = messages.get(title_key, title)
    nav = (
        f'<nav aria-label="{html.escape(messages["nav.language"])}">'
        f'<span>{html.escape(messages["nav.language"])}</span> '
        f'<a href="{english_href}" lang="en" hreflang="en">{html.escape(messages["nav.english"])}</a> · '
        f'<a href="{urdu_href}" lang="ur" hreflang="ur" aria-current="{"page" if locale == "ur" else "false"}">'
        f'{html.escape(messages["nav.urdu"])}</a>'
        '</nav>'
    )
    notice = review_notice(locale, root) if locale != "en" else ""
    rtl_css = (
        'body{direction:rtl;text-align:right;font-family:"Noto Naskh Arabic","Noto Sans Arabic",system-ui,sans-serif}'
        'main{unicode-bidi:plaintext}code,pre,[dir="ltr"]{direction:ltr;unicode-bidi:isolate}'
    )
    style = CSS + (rtl_css if content_locale == "ur" else "")
    return (
        f'<!doctype html><html lang="{content_locale}" dir="{direction}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{html.escape(title)}</title><style>{style}</style></head>'
        f'<body><main>{nav}{notice}{body}</main></body></html>'
    )


def gh(path):
    try:
        return json.loads(
            subprocess.run(
                ["gh", "api", path],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        )
    except Exception:
        return None


def items(md):
    rows = []
    for line in md.splitlines():
        match = re.match(r"\|\s*(HD-\d+)\s*\|(.*)\|(.*)\|(.*)\|\s*$", line)
        if match:
            rows.append([cell.strip() for cell in (match.group(1), match.group(2), match.group(3), match.group(4))])
    return rows


def klass(state):
    value = state.lower()
    if value.startswith(("implemented", "done", "verified", "merged")):
        return "s-done"
    if value.startswith("blocked"):
        return "s-blocked"
    return "s-pending"


def render_body(messages, rows, done, pr_state, source_ref, source_sha, now, issues, docs, repo, pr):
    table_rows = "".join(
        f'<tr class="{klass(row[3])}"><td>{html.escape(row[0])}</td><td>{html.escape(row[1])}</td>'
        f'<td>{html.escape(row[2])}</td><td><strong>{html.escape(row[3])}</strong></td></tr>'
        for row in rows
    )
    issue_items = "".join(
        f'<li><a href="{html.escape(issue["html_url"])}">#{issue["number"]}</a> '
        f'{html.escape(issue["title"])} — {html.escape(issue["state"])}; labels: '
        f'{html.escape(", ".join(label["name"] for label in issue.get("labels", [])))}</li>'
        for issue in issues if "pull_request" not in issue
    ) or f'<li>{html.escape(messages["content.empty_dispatch"])}</li>'
    doc_items = "".join(
        f'<li><a href="{key}.html">{html.escape(title)}</a></li>'
        for key, (title, _) in DOCS.items()
    )
    status = (
        f'<p role="status">{html.escape(messages["status.done"])} <strong>{done}/{len(rows)}</strong> · '
        f'<span lang="en" dir="ltr">PR <a href="https://github.com/{repo}/pull/{pr}">#{pr}</a> {html.escape(pr_state)}</span> · '
        f'{html.escape(messages["status.source"])} '
        f'<span lang="en" dir="ltr"><code>{html.escape(source_ref)}</code> @ '
        f'<code>{html.escape(source_sha[:7])}</code> · {html.escape(now)}</span></p>'
    )
    return (
        f'<h1>{html.escape(messages["page.title"])}</h1>'
        f'<p>{html.escape(messages["page.description"])} {html.escape(messages["page.separation"])}</p>'
        f'{status}'
        f'<h2>{html.escape(messages["section.done_board"])}</h2>'
        '<div lang="en" dir="ltr"><table><thead><tr><th>ID</th><th>Work item</th>'
        f'<th>Acceptance evidence</th><th>State</th></tr></thead><tbody>{table_rows}</tbody></table></div>'
        f'<h2>{html.escape(messages["section.dispatch"])} '
        f'({html.escape(messages["section.dispatch_label"])})</h2>'
        f'<div lang="en" dir="ltr"><ul>{issue_items}</ul></div>'
        f'<h2>{html.escape(messages["section.reference"])}</h2>'
        f'<div lang="en" dir="ltr"><ul>{doc_items}</ul></div>'
        f'<h2>{html.escape(messages["section.route"])}</h2>'
        '<p lang="en" dir="ltr">Project-task filing ⇒ swarm-admission ⇒ project-task-dispatch ⇒ build-dispatch ⇒ PR ⇒ '
        'this page via <code>teammate-portal-status-publish.yml</code>. Contract: '
        f'<a href="https://github.com/{repo}/blob/master/docs/ops/REVIEW-PUBLISHING.md">REVIEW-PUBLISHING</a>.</p>'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", type=int, required=True)
    args = parser.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    for key, (title, path) in DOCS.items():
        source_path = pathlib.Path(path)
        body = (
            markdown.markdown(source_path.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
            if source_path.exists() else "<p>Missing at this ref.</p>"
        )
        (out / f"{key}.html").write_text(
            page(f"Teammate Portal · {title}", f'<p><a href="./">← Status</a></p>{body}'),
            encoding="utf-8",
        )

    items_path = pathlib.Path(DOCS["items"][1])
    rows = items(items_path.read_text(encoding="utf-8")) if items_path.exists() else []
    done = sum(1 for row in rows if klass(row[3]) == "s-done")
    pr_data = gh(f"repos/{args.repo}/pulls/{args.pr}") or {}
    pr_state = "merged" if pr_data.get("merged_at") else (pr_data.get("state") or "unknown")
    issues = gh(f"repos/{args.repo}/issues?labels=teammate-portal&state=all&per_page=20") or []
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    messages_en = load_catalog("en")
    messages_ur = load_catalog("ur")
    body_en = render_body(
        messages_en, rows, done, pr_state, args.source_ref, args.source_sha,
        now, issues, DOCS, args.repo, args.pr,
    )
    urdu_content = render_body(
        messages_ur, rows, done, pr_state, args.source_ref, args.source_sha,
        now, issues, DOCS, args.repo, args.pr,
    )
    if translation_is_fresh("ur"):
        body_ur = (
            f'<p lang="ur" dir="rtl">{html.escape(messages_ur["content.english_fallback"])}</p>'
            + urdu_content
        )
    else:
        body_ur = (
            f'<p lang="en" dir="ltr">{html.escape(messages_ur["content.english_fallback"])}</p>'
            f'<div lang="en" dir="ltr">{urdu_content}</div>'
        )
    (out / "index.html").write_text(
        page(messages_en["page.title"], body_en, "en", title_key="page.title"),
        encoding="utf-8",
    )
    urdu_dir = out / "ur"
    urdu_dir.mkdir(parents=True, exist_ok=True)
    (urdu_dir / "index.html").write_text(
        page(messages_ur["page.title"], body_ur, "ur", title_key="page.title"),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
