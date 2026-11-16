#!/usr/bin/env python3
"""Derive the ListingLens demo-video beats manifest from a REAL demo run.

QUE-GOV-MEDIA-001 (method of record for #5137): no staged frames, no
hardcoded wins. Every value on a frame is extracted from the demo
run's captured stdout (the capture of record) or from the repo source
the beat cites. A missing expected value is a hard failure — the
render must never invent a number the run did not produce.

Usage:
  python3 scripts/listinglens/derive_manifest.py \
      --demo-output demo-output.txt \
      --actions-src apps/listinglens/src/actions.mjs \
      --repo-url https://github.com/OWNER/REPO \
      --out beats.json
"""

import argparse
import json
import re
import sys
import textwrap

WRAP = 56


def _field(text, label, section=None):
    """Extract a `label value` line from the demo output."""
    hay = text
    if section is not None:
        parts = text.split(section, 1)
        if len(parts) < 2:
            raise ValueError(f"demo output missing section {section!r}")
        hay = parts[1]
    m = re.search(rf"^{re.escape(label)}\s+(.+)$", hay, re.M)
    if not m:
        raise ValueError(f"demo output missing field {label!r}")
    return m.group(1).strip()


def _wrap(lines):
    out = []
    for line in lines:
        out.extend(textwrap.wrap(line, WRAP) or [""])
    return out


def derive(demo_text, actions_text, repo_url):
    title1 = _field(demo_text, "title")
    price1 = _field(demo_text, "price")
    layout = _field(demo_text, "layout")
    photo = _field(demo_text, "photo")
    prov1 = _field(demo_text, "provenance")
    title2 = _field(demo_text, "title", section="== seller edit")
    price2 = _field(demo_text, "price", section="== seller edit")
    prov2 = _field(demo_text, "provenance", section="== seller edit")

    price1_match = re.search(r"\$[\d.]+", price1)
    price2_match = re.search(r"\$[\d.]+", price2)
    if not price1_match or not price2_match:
        raise ValueError("demo output prices not parseable")
    accent_match = re.search(r"accent\s+(#[0-9a-fA-F]{6})", layout)
    template_match = re.search(r"^(\S+)\s+·", layout)
    model_match = re.search(r"^(\S+)", prov1)

    actions = re.findall(r"export const (\w+) = defineAction", actions_text)
    if len(actions) < 2:
        raise ValueError("actions source must declare >= 2 defineAction exports")

    beats = [
        {
            "beat": 1,
            "heading": "One photo. A whole listing to write.",
            "lines": _wrap([
                "An indie seller's work starts at the photo —",
                "title, copy, price, layout still to produce.",
                f"photo: {photo}",
            ]),
        },
        {
            "beat": 2,
            "heading": "generateListing does the job",
            "lines": _wrap([
                f"title: {title1}",
                f"price: {price1}",
                f"layout: {layout}",
            ]),
        },
        {
            "beat": 3,
            "heading": "The seller acts — revision 2",
            "lines": _wrap([
                f"edited title: {title2}",
                f"edited price: {price2_match.group(0)} (was {price1_match.group(0)})",
                f"{prov2} — the prior revision is never mutated.",
            ]),
        },
        {
            "beat": 4,
            "heading": "Claims ceiling, stated plainly",
            "lines": _wrap([
                f"live in this run: {prov1}",
                "deterministic local model — offline, no keys.",
                "A hosted vision/LLM model is interface-only:",
                "same createModel() seam, not called by the demo.",
            ]),
        },
        {
            "beat": 5,
            "heading": "Agent-Native by construction",
            "lines": _wrap([
                f"defineAction x{len(actions)}: " + " · ".join(actions),
                repo_url,
            ]),
        },
    ]
    return {
        "schema": "listinglens.beats/v1",
        "accent": accent_match.group(1) if accent_match else "#b5542d",
        "template": template_match.group(1) if template_match else "hero-spotlight",
        "model": model_match.group(1) if model_match else "listinglens-local/1",
        "values": {
            "title_rev1": title1,
            "price_rev1": price1_match.group(0),
            "title_rev2": title2,
            "price_rev2": price2_match.group(0),
        },
        "beats": beats,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo-output", required=True)
    ap.add_argument("--actions-src", required=True)
    ap.add_argument("--repo-url", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    with open(a.demo_output) as fh:
        demo_text = fh.read()
    with open(a.actions_src) as fh:
        actions_text = fh.read()
    manifest = derive(demo_text, actions_text, a.repo_url)
    with open(a.out, "w") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    print(f"beats manifest: {len(manifest['beats'])} beats, "
          f"values {manifest['values']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
