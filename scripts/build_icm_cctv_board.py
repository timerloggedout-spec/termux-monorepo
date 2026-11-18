#!/usr/bin/env python3
"""Generate the static ICM CCTV board from canonical Markdown screen cards."""
from __future__ import annotations
import argparse
import html
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/timerloggedout-spec/termux-monorepo"
SITE = "https://timerloggedout-spec.github.io/tribute/icm-cctv.html"


def cards_from(root: Path) -> list[dict[str, str]]:
    cards = []
    for path in sorted(root.rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---\n"):
            raise ValueError(f"{path}: missing frontmatter")
        _, meta, body = raw.split("---", 2)
        fields = {}
        for line in meta.splitlines():
            match = re.match(r"^([\w-]+):\s*(.*?)\s*$", line)
            if match:
                fields[match.group(1)] = match.group(2).strip("\"'")
        for key in ("id", "title", "status", "source"):
            if not fields.get(key):
                raise ValueError(f"{path}: missing {key}")
        fields["body"] = body.strip()
        fields["path"] = (path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.relative_to(root)).as_posix()
        cards.append(fields)
    cards.sort(key=lambda c: (int(c.get("stage", "999")) if c.get("stage", "").isdigit() else 999, c["id"]))
    if not cards:
        raise ValueError(f"No cards found under {root}")
    return cards


def md(text: str) -> str:
    value = html.escape(text, quote=True)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    return value


def build(root: Path, sha: str) -> str:
    cards = cards_from(root)
    rendered = []
    counts: dict[str, int] = {}
    for c in cards:
        status = html.escape(c["status"], quote=True)
        counts[status] = counts.get(status, 0) + 1
        paragraphs = "".join(f"<p>{md(p.strip())}</p>" for p in re.split(r"\n\s*\n", c["body"]) if p.strip())
        stage = html.escape(c.get("stage", "—"), quote=True)
        title = html.escape(c["title"], quote=True)
        ident = html.escape(c["id"], quote=True)
        source = html.escape(c["source"], quote=True)
        path = html.escape(c["path"], quote=True)
        rendered.append(f"""<article class="card"><div class="top"><span>Stage {stage}</span><span class="status {status}">{status}</span></div>
<h3>{title}</h3><code>{ident}</code>{paragraphs}
<dl><dt>Canonical source</dt><dd><a href="{REPO}/blob/master/docs/icm/{source}">{source}</a></dd>
<dt>Card file</dt><dd><a href="{REPO}/blob/master/{path}">{path}</a></dd></dl></article>""")
    summary = " · ".join(f"{n} {status}" for status, n in sorted(counts.items()))
    source_sha = html.escape(sha or "local/unset", quote=True)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Static, file-backed ICM visual review board. Canonical ICM records remain in the repository.">
<link rel="canonical" href="{SITE}"><link rel="stylesheet" href="./dashboard.css"><title>ICM CCTV · Visual Review Board</title>
<style>
body{{background:#0b0d10;color:#edf2f7;font:15px/1.6 system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:1.5rem}}
.hero{{padding:1.5rem 0;border-bottom:1px solid #26384a}}.eyebrow{{color:#e8c66a;text-transform:uppercase;letter-spacing:.12em;font-size:.78rem}}
h1{{font-size:clamp(2rem,5vw,3.2rem);margin:.2rem 0}}.muted{{color:#a0adba}}.summary{{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0}}
.pill,.status,.top span{{border:1px solid #26384a;border-radius:999px;padding:.2rem .65rem;font-size:.78rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:1rem;margin:1.2rem 0}}
.card,.research{{background:#121820;border:1px solid #26384a;border-radius:12px;padding:1rem;min-width:0}}
.top{{display:flex;justify-content:space-between;gap:.5rem}}h3{{margin:.7rem 0 .1rem}}code,a{{color:#8fc9ff;overflow-wrap:anywhere}}
.card p{{color:#d1d9e0}}dl{{display:grid;grid-template-columns:110px minmax(0,1fr);gap:.3rem .8rem;border-top:1px solid #26384a;padding-top:.8rem;font-size:.82rem}}
dt{{color:#a0adba}}dd{{margin:0;overflow-wrap:anywhere}}.done{{color:#8ee0ae}}.blocked{{color:#f0bf79}}
.notice{{border-left:3px solid #e8c66a;background:#171b20;padding:.7rem 1rem;margin:1rem 0}}
footer{{border-top:1px solid #26384a;padding:1rem 0;color:#a0adba;font-size:.82rem}}@media(max-width:560px){{main{{padding:1rem}}dl{{grid-template-columns:1fr}}}}
</style><script src="./site-nav.js" defer></script></head><body><main>
<header class="hero"><div class="eyebrow">Interpretable Context Methodology · file-backed visual review</div><h1>ICM CCTV</h1>
<p class="muted">A static visual mirror of repository-native ICM screen cards and human checkpoints. Source records remain authoritative.</p>
<div class="summary"><span class="pill">{len(cards)} canonical screen cards</span><span class="pill">{summary}</span><span class="pill">Source SHA {source_sha}</span></div></header>
<section class="notice"><strong>Static review surface.</strong> This board renders reviewed Markdown cards. It provides no live camera/video feeds, provider polling, file watcher, WebSocket, response writer, device access, or runtime routing control.</section>
<section><h2>ICM screen cards</h2><div class="grid">{''.join(rendered)}</div></section>
<section class="research"><h2>Research lineage · Jake Van Clief</h2>
<p>The repository’s ICM knowledge layer cites Jake Van Clief, David McDermott, and Kay Kumar (2026), <em>The Cost of Remembering: Filesystem Memory Against Long Context on LongMemEval</em>. The local knowledge card describes the work as empirical support for filesystem-backed memory and selective context loading.</p>
<p><a href="{REPO}/blob/master/docs/icm/objects/knowledge/cost-of-remembering.md">Canonical ICM knowledge card</a> · <a href="https://github.com/RinDig/cost-of-remembering">Upstream research repository</a></p></section>
<section><h2>Canonical contracts</h2><ul>
<li><a href="{REPO}/blob/master/docs/icm/_tv/README.md">ICM CCTV card and response-cage contract</a></li>
<li><a href="{REPO}/blob/master/docs/icm/objects/operations/optional-visual-review.md">Optional visual review</a></li>
<li><a href="{REPO}/blob/master/docs/icm/routing/CONTEXT.md">Provider routing governance</a></li>
<li><a href="{REPO}/blob/master/docs/ops/ICM-CCTV.md">Ops dashboard projection contract</a></li>
<li><a href="{REPO}/tree/master/docs/icm/_tv/screens">All canonical ICM screen cards</a></li>
</ul></section><footer>ICM CCTV · generated from canonical card files · source SHA {source_sha} · <a href="{REPO}">repository</a></footer>
</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cards-dir", type=Path, default=ROOT / "docs/icm/_tv/screens")
    parser.add_argument("--output", type=Path, default=ROOT / "apps/tribute-dashboard/icm-cctv.html")
    parser.add_argument("--source-sha", default=os.environ.get("GITHUB_SHA", "local/unset"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = build(args.cards_dir, args.source_sha)
    if args.check:
        print(f"ICM CCTV board: {rendered.count('<article class=\"card\">')} cards rendered")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output} ({rendered.count('<article class=\"card\">')} cards)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
