#!/usr/bin/env python3
"""Generate the static ICM CCTV board from canonical Markdown screen cards."""
from __future__ import annotations
import argparse
import html
import os
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/timerloggedout-spec/termux-monorepo"
SITE = "https://timerloggedout-spec.github.io/tribute/icm-cctv.html"


def cards_from(root: Path) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    canonical_root = (ROOT / "docs/icm").resolve()
    for path in sorted(root.rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---\n") or "\n---" not in raw[4:]:
            raise ValueError(f"{path}: missing delimited frontmatter")
        _, meta, body = raw.split("---", 2)
        fields: dict[str, str] = {}
        for line in meta.splitlines():
            match = re.match(r"^([\w-]+):\s*(.*?)\s*$", line)
            if match:
                fields[match.group(1)] = match.group(2).strip("\"'")
        for key in ("id", "title", "status", "source"):
            if not fields.get(key):
                raise ValueError(f"{path}: missing {key}")
        source = PurePosixPath(fields["source"])
        if source.is_absolute() or ".." in source.parts:
            raise ValueError(f"{path}: source must stay inside docs/icm")
        source_file = (canonical_root / Path(*source.parts)).resolve()
        if root.resolve().is_relative_to(canonical_root):
            if canonical_root not in source_file.parents:
                raise ValueError(f"{path}: canonical source must stay under docs/icm")
            if not source_file.is_file():
                raise ValueError(f"{path}: canonical source is missing: {fields['source']}")
        fields["body"] = body.strip()
        fields["path"] = (path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.relative_to(root)).as_posix()
        fields["stage"] = fields.get("stage", "999")
        fields["status_slug"] = re.sub(r"[^a-z0-9-]+", "-", fields["status"].lower()).strip("-")
        fields["source_url"] = f"{REPO}/blob/master/docs/icm/{source.as_posix()}"
        cards.append(fields)
    cards.sort(key=lambda c: (int(c["stage"]) if c["stage"].isdigit() else 999, c["id"]))
    if not cards:
        raise ValueError(f"Card directory is empty: {root}")
    ids = [card["id"] for card in cards]
    if len(ids) != len(set(ids)):
        raise ValueError("Card identifiers must be unique across the board")
    return cards


def inline_md(text: str) -> str:
    value = html.escape(text, quote=True)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\x60([^\x60]+)\x60", r"<code>\1</code>", value)
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', value)
    return value


def render_body(body: str) -> str:
    blocks: list[str] = []
    paragraph: list[str] = []
    bullets: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f"<p>{inline_md(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_bullets() -> None:
        if bullets:
            items = "".join(f"<li>{inline_md(item)}</li>" for item in bullets)
            blocks.append(f"<ul>{items}</ul>")
            bullets.clear()

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_bullets()
        elif stripped.startswith("- ") or stripped.startswith("* "):
            flush_paragraph()
            bullets.append(stripped[2:])
        else:
            flush_bullets()
            paragraph.append(stripped)
    flush_paragraph()
    flush_bullets()
    return "".join(blocks)


def build(root: Path, sha: str) -> str:
    cards = cards_from(root)
    counts: dict[str, int] = {}
    stages: dict[str, list[str]] = {}
    statuses = sorted({card["status"] for card in cards})
    for card in cards:
        counts[card["status"]] = counts.get(card["status"], 0) + 1
        stages.setdefault(card["stage"], []).append(card["id"])

    rendered: list[str] = []
    for card in cards:
        status = html.escape(card["status"], quote=True)
        status_slug = html.escape(card["status_slug"], quote=True)
        stage = html.escape(card["stage"], quote=True)
        title = html.escape(card["title"], quote=True)
        ident = html.escape(card["id"], quote=True)
        source = html.escape(card["source"], quote=True)
        source_url = html.escape(card["source_url"], quote=True)
        path = html.escape(card["path"], quote=True)
        search_text = html.escape(" ".join((card["title"], card["id"], card["status"], card["stage"], card["body"])), quote=True)
        rendered.append(f"""<article class="card" id="card-{ident}" data-status="{status_slug}" data-stage="{stage}" data-search="{search_text}">
<div class="top"><span>Stage {stage}</span><span class="status {status_slug}">{status}</span></div>
<h3>{title}</h3><code>{ident}</code>{render_body(card["body"])}
<dl><dt>Canonical source</dt><dd><a href="{source_url}">{source}</a></dd>
<dt>Card file</dt><dd><a href="{REPO}/blob/master/{path}">{path}</a></dd></dl></article>""")

    stage_nav = "".join(f'<a class="stage-link" href="#stage-{html.escape(stage, quote=True)}">Stage {html.escape(stage)}</a>' for stage in sorted(stages, key=lambda value: int(value) if value.isdigit() else 999))
    status_options = "".join(
        f'<option value="{re.sub(r"[^a-z0-9-]+", "-", status.lower()).strip("-")}">{html.escape(status)} ({counts[status]})</option>'
        for status in statuses
    )
    stage_sections = []
    for stage in sorted(stages, key=lambda value: int(value) if value.isdigit() else 999):
        stage_cards = "".join(
            item for item in rendered
            if re.search(rf'<article class="card" id="card-[^"]+" data-status="[^"]+" data-stage="{re.escape(stage)}"', item)
        )
        stage_sections.append(f'<section class="stage-section" id="stage-{html.escape(stage, quote=True)}"><h3 class="stage-heading">Stage {html.escape(stage)}</h3><div class="grid">{stage_cards}</div></section>')

    summary = " · ".join(f"{count} {status}" for status, count in sorted(counts.items()))
    source_sha = html.escape(sha or "local/unset", quote=True)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Static, file-backed ICM visual review board. Canonical ICM records remain in the repository.">
<link rel="canonical" href="{SITE}"><link rel="stylesheet" href="./dashboard.css"><title>ICM CCTV · Visual Review Board</title>
<style>
body{{background:#0b0d10;color:#edf2f7;font:15px/1.6 system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:1.5rem}}
.hero{{padding:1.5rem 0;border-bottom:1px solid #26384a}}.eyebrow{{color:#e8c66a;text-transform:uppercase;letter-spacing:.12em;font-size:.78rem}}
h1{{font-size:clamp(2rem,5vw,3.2rem);margin:.2rem 0}}.muted{{color:#a0adba}}.summary,.stage-nav{{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0}}
.pill,.status,.top span,.stage-link{{border:1px solid #26384a;border-radius:999px;padding:.2rem .65rem;font-size:.78rem}}
.stage-link{{color:#8fc9ff;text-decoration:none}}.stage-link:hover{{border-color:#8fc9ff}}
.toolbar{{display:grid;grid-template-columns:minmax(0,1fr) minmax(180px,240px);gap:.8rem;margin:1rem 0}}
.toolbar label{{display:grid;gap:.25rem;color:#a0adba;font-size:.82rem}}.toolbar input,.toolbar select{{width:100%;box-sizing:border-box;background:#121820;color:#edf2f7;border:1px solid #405266;border-radius:8px;padding:.7rem;font:inherit}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:1rem;margin:1rem 0}}
.card,.research{{background:#121820;border:1px solid #26384a;border-radius:12px;padding:1rem;min-width:0}}
.top{{display:flex;justify-content:space-between;gap:.5rem}}h3{{margin:.7rem 0 .1rem}}code,a{{color:#8fc9ff;overflow-wrap:anywhere}}
.card p,.card li{{color:#d1d9e0}}.card ul{{padding-left:1.2rem}}dl{{display:grid;grid-template-columns:110px minmax(0,1fr);gap:.3rem .8rem;border-top:1px solid #26384a;padding-top:.8rem;font-size:.82rem}}
dt{{color:#a0adba}}dd{{margin:0;overflow-wrap:anywhere}}.done{{color:#8ee0ae}}.blocked{{color:#f0bf79}}
.notice{{border-left:3px solid #e8c66a;background:#171b20;padding:.7rem 1rem;margin:1rem 0}}
.stage-section{{scroll-margin-top:1rem;margin:1.4rem 0}}.stage-heading{{border-bottom:1px solid #26384a;padding-bottom:.4rem}}
.empty{{display:none;color:#a0adba;padding:1rem;border:1px dashed #405266;border-radius:8px}}.card[hidden]{{display:none}}
footer{{border-top:1px solid #26384a;padding:1rem 0;color:#a0adba;font-size:.82rem}}
@media(max-width:560px){{main{{padding:1rem}}dl{{grid-template-columns:1fr}}.toolbar{{grid-template-columns:1fr}}}}
</style><script src="./site-nav.js" defer></script></head><body><main>
<header class="hero"><div class="eyebrow">Interpretable Context Methodology · file-backed visual review</div><h1>ICM CCTV</h1>
<p class="muted">A static visual mirror of repository-native ICM screen cards and human checkpoints. Source records remain authoritative.</p>
<div class="summary"><span class="pill">{len(cards)} canonical screen cards</span><span class="pill">{summary}</span><span class="pill">Source SHA {source_sha}</span></div>
<nav class="stage-nav" aria-label="Jump to stage">{stage_nav}</nav></header>
<section class="notice"><strong>Static review surface.</strong> This board renders reviewed Markdown cards. It provides no live camera/video feeds, provider polling, file watcher, WebSocket, response writer, device access, or runtime routing control.</section>
<section aria-labelledby="cards-heading"><h2 id="cards-heading">ICM screen cards</h2>
<div class="toolbar"><label for="card-search">Search cards<input id="card-search" type="search" placeholder="Search title, ID, status, or card text"></label>
<label for="status-filter">Filter by status<select id="status-filter"><option value="">All statuses</option>{status_options}</select></label></div>
<p id="result-count" class="muted" aria-live="polite">Showing {len(cards)} of {len(cards)} cards</p>
{''.join(stage_sections)}<p id="empty-state" class="empty">No cards match the current search and status filter.</p></section>
<section class="research"><h2>Research lineage · Jake Van Clief</h2>
<p>The repository’s ICM knowledge layer cites Jake Van Clief, David McDermott, and Kay Kumar (2026), <em>The Cost of Remembering: Filesystem Memory Against Long Context on LongMemEval</em>. The local knowledge card describes the work as empirical support for filesystem-backed memory and selective context loading.</p>
<p><a href="{REPO}/blob/master/docs/icm/objects/knowledge/cost-of-remembering.md">Canonical ICM knowledge card</a> · <a href="https://github.com/RinDig/cost-of-remembering">Upstream research repository</a></p></section>
<section><h2>Review sequence</h2><ol><li>Open the canonical source from the card.</li><li>Record evidence and decisions in the owning ICM artifact.</li><li>Update the card status and stage after the source review.</li><li>Route blocked checkpoints to the named human reviewer.</li></ol></section>
<section><h2>Canonical contracts</h2><ul>
<li><a href="{REPO}/blob/master/docs/icm/_tv/README.md">ICM CCTV card and response-cage contract</a></li>
<li><a href="{REPO}/blob/master/docs/icm/objects/operations/optional-visual-review.md">Optional visual review</a></li>
<li><a href="{REPO}/blob/master/docs/icm/routing/CONTEXT.md">Provider routing governance</a></li>
<li><a href="{REPO}/blob/master/docs/ops/ICM-CCTV.md">Ops dashboard projection contract</a></li>
<li><a href="{REPO}/tree/master/docs/icm/_tv/screens">All canonical ICM screen cards</a></li>
</ul></section><footer>ICM CCTV · generated from canonical card files · source SHA {source_sha} · <a href="{REPO}">repository</a></footer>
</main><script>
(() => {{
  const search = document.getElementById("card-search");
  const status = document.getElementById("status-filter");
  const cards = [...document.querySelectorAll(".card")];
  const count = document.getElementById("result-count");
  const empty = document.getElementById("empty-state");
  const stages = [...document.querySelectorAll(".stage-section")];
  const update = () => {{
    const query = search.value.trim().toLocaleLowerCase();
    const selected = status.value;
    let visible = 0;
    cards.forEach(card => {{
      const match = (!query || card.dataset.search.toLocaleLowerCase().includes(query))
        && (!selected || card.dataset.status === selected);
      card.hidden = !match;
      if (match) visible += 1;
    }});
    stages.forEach(stage => {{
      stage.hidden = !stage.querySelector(".card:not([hidden])");
    }});
    count.textContent = "Showing " + visible + " of " + cards.length + " cards";
    empty.style.display = visible ? "none" : "block";
  }};
  search.addEventListener("input", update);
  status.addEventListener("change", update);
}})();
</script></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cards-dir", type=Path, default=ROOT / "docs/icm/_tv/screens")
    parser.add_argument("--output", type=Path, default=ROOT / "apps/tribute-dashboard/icm-cctv.html")
    parser.add_argument("--source-sha", default=os.environ.get("GITHUB_SHA", "local/unset"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = build(args.cards_dir, args.source_sha)
    if args.check:
        print(f"ICM CCTV board: {rendered.count('<article class=\"card\"')} cards rendered")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output} ({rendered.count('<article class=\"card\"')} cards)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
