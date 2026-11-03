#!/usr/bin/env python3
"""Swarm admission for issue-template filings (QUE Tranche 4 machinery).

Owner contract (2026-11-03): "Issue Templates trigger swarm fleet" --
a filing IS a dispatch, declared at the template, and it reaches the
swarm only THROUGH QUE ADMISSION (dispatch-tiers v2: tier -> after ->
chain -> flow projection). Nothing spawns raw off an issue form.

This script is the admission evaluator. It:

  1. scans .github/ISSUE_TEMPLATE/*.yml for SWARM-DISPATCH blocks
     (schema issue-dispatch/v1 -- see docs/ops/ISSUE-TEMPLATE-DISPATCH.md)
  2. matches the filing to its template (the template's declared
     labels, or its title prefix -- the same keying the #3577 intake
     uses, so API-filed replicas of a form behave identically)
  3. evaluates admission in the v2 guard order:
       tier (from the block)
       -> after-classes: any incomplete run of an after-class pattern
          (wedged ancients >= 7 days excluded -- they hold no runner
          and would defer the fleet forever)
       -> chain stage: prior-stage nodes of the declared chain with
          incomplete runs in scope
       -> flow projection: current queued depth vs the tier's
          saturation threshold (tiers 1-2 never flow-defer)
  4. emits the decision + the receipt stamp (the filing's first fleet
     comment) for the workflow to post, and the label to apply
     (swarm-admitted | deferred-by-tier).

Fail-soft is the design: any evaluation error defers with the reason
stamped, never admits blind and never drops the filing.

Stdlib only. The API transport is injectable for tests.
"""

import json
import re
import sys
from datetime import datetime, timedelta, timezone

BLOCK_BEGIN = "SWARM-DISPATCH-BEGIN"
BLOCK_END = "SWARM-DISPATCH-END"
ANCIENT_DAYS = 7

# Flow thresholds (v1, of record in the spec): queued depth at/above
# which a tier self-defers. Tiers 1-2 never flow-defer.
FLOW_THRESHOLDS = {3: 800, 4: 400}


def parse_block(text):
    """Extract the SWARM-DISPATCH block from a template file's text.

    Returns a dict of the block's key: value lines, or None.
    """
    if BLOCK_BEGIN not in text or BLOCK_END not in text:
        return None
    seg = text.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0]
    block = {}
    for line in seg.splitlines():
        line = line.strip().lstrip("#").strip()
        m = re.match(r"^([a-z_]+):\s*(.+)$", line)
        if m:
            block[m.group(1)] = m.group(2).strip()
    if "lane" not in block or "payload_class" not in block:
        return None
    block["que_tier"] = int(block.get("que_tier", "4"))
    block["after"] = [p.strip() for p in block.get("after", "").split(",") if p.strip()]
    return block


def template_identity(text):
    """The labels + title prefix a template declares (form header)."""
    labels = []
    m = re.search(r"^labels:\s*\[([^\]]*)\]", text, re.M)
    if m:
        labels = [x.strip().strip('"\'') for x in m.group(1).split(",") if x.strip()]
    prefix = ""
    m = re.search(r'^title:\s*"([^"]*)"', text, re.M)
    if m:
        prefix = m.group(1).split("<")[0].strip()
    return labels, prefix


def match_template(registry, issue_labels, issue_title):
    """registry: {filename: (block, labels, prefix)}. First match wins,
    in filename order for determinism."""
    for fname in sorted(registry):
        block, labels, prefix = registry[fname]
        if labels and any(l in issue_labels for l in labels):
            return fname, block
        if prefix and issue_title.startswith(prefix):
            return fname, block
    return None, None


def _incomplete(runs, patterns, now):
    """Runs matching any pattern (case-insensitive substring on the
    workflow name) that are queued/in_progress and not ancient."""
    out = []
    for r in runs:
        if r.get("status") not in ("queued", "in_progress"):
            continue
        created = r.get("created_at", "")
        try:
            dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if now - dt >= timedelta(days=ANCIENT_DAYS):
                continue
        except ValueError:
            pass
        name = (r.get("name") or "").lower()
        if any(p.lower() in name for p in patterns):
            out.append(r)
    return out


def evaluate(block, tiers_doc, runs, now=None):
    """The v2 guard order. Returns (decision, reasons, facts)."""
    now = now or datetime.now(timezone.utc)
    tier = block["que_tier"]
    reasons = []
    facts = {"tier": tier, "queued_depth": 0, "after": {}, "chain": {}}

    queued = [r for r in runs if r.get("status") == "queued"]
    facts["queued_depth"] = len(queued)

    # after-classes
    for pat in block.get("after", []):
        inc = _incomplete(runs, [pat], now)
        facts["after"][pat] = len(inc)
        if inc:
            reasons.append(f"after-class '{pat}' has {len(inc)} incomplete run(s)")

    # chain stage (only when the block declares chain + stage)
    chain_name = block.get("chain") or ""
    stage_idx = block.get("chain_stage")
    if chain_name and stage_idx is not None:
        stage_idx = int(stage_idx)
        chains = {c["entry"]: c for c in tiers_doc.get("chains", [])}
        chain = chains.get(chain_name)
        if chain:
            prior = []
            for st in chain.get("stages", [])[:stage_idx]:
                prior += st.get("match", [])
            inc = _incomplete(runs, prior, now)
            facts["chain"] = {"entry": chain_name, "stage": stage_idx, "prior_incomplete": len(inc)}
            if inc:
                reasons.append(f"chain '{chain_name}' stage {stage_idx}: {len(inc)} prior-stage run(s) incomplete")
        else:
            reasons.append(f"chain '{chain_name}' not found in dispatch-tiers.json (fail-soft defer)")

    # flow projection
    thresh = FLOW_THRESHOLDS.get(tier)
    facts["flow_threshold"] = thresh
    if thresh is not None and facts["queued_depth"] >= thresh:
        reasons.append(f"flow: queued depth {facts['queued_depth']} >= tier-{tier} threshold {thresh}")

    decision = "DEFERRED" if reasons else "ADMITTED"
    return decision, reasons, facts


def stamp(fname, block, decision, reasons, facts, run_url):
    head = f"[MUSEai]@{{role:{{swarm-admission}}}} DISPATCH **{decision}**"
    parts = [
        head,
        f"template `{fname}` · lane {block['lane']} · tier {facts['tier']} · payload {block['payload_class']}",
        f"route: {block.get('route', '(none declared)')}",
        f"flow: queued depth {facts['queued_depth']}"
        + (f" (tier threshold {facts['flow_threshold']})" if facts.get("flow_threshold") else " (tier never flow-defers)"),
    ]
    if facts.get("after"):
        parts.append("after: " + " · ".join(f"{k} ✓ {v} incomplete" for k, v in facts["after"].items()))
    if facts.get("chain"):
        parts.append(f"chain: {facts['chain']}")
    if reasons:
        parts.append("**deferred because:** " + "; ".join(reasons))
        parts.append("Fail-soft of record: the filing stays queued as `deferred-by-tier`; the QUE admission drain re-evaluates it — nothing was spawned.")
    else:
        parts.append("The route named above executes under its own intake; this stamp is the admission receipt of record (QUE measurement-plane transition: enqueued → admitted).")
    parts.append(f"admission run: {run_url}")
    return "\n\n".join(parts)


def main(argv):
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--templates-dir", required=True)
    ap.add_argument("--tiers", required=True)
    ap.add_argument("--runs-file", required=True, help="JSON list of recent runs (queued + in_progress)")
    ap.add_argument("--issue-labels", default="")
    ap.add_argument("--issue-title", default="")
    ap.add_argument("--run-url", default="")
    ap.add_argument("--comment-out", required=True)
    ap.add_argument("--github-output", default="")
    a = ap.parse_args(argv)

    import pathlib

    registry = {}
    for p in sorted(pathlib.Path(a.templates_dir).glob("*.yml")):
        text = p.read_text()
        block = parse_block(text)
        if block:
            labels, prefix = template_identity(text)
            registry[p.name] = (block, labels, prefix)

    fname, block = match_template(
        registry,
        [x.strip() for x in a.issue_labels.split(",") if x.strip()],
        a.issue_title,
    )
    out = {}
    if not block:
        out = {"matched": "false"}
    else:
        # Fail-soft covers EVERYTHING past the match — including the
        # tiers/runs loads (proof run 41731985726: dispatch-tiers.json
        # not yet on master crashed the evaluator before the defer
        # path could stamp; a missing dependency must DEFER with the
        # reason, never crash silent).
        try:
            tiers_doc = json.loads(pathlib.Path(a.tiers).read_text())
            runs = json.loads(pathlib.Path(a.runs_file).read_text())
            if isinstance(runs, dict) and runs.get("collection_error"):
                # The queue picture could not be collected (proof
                # run 41737482551: an API error body mid-pagination
                # killed the collector step, and with it the
                # stamp). Unknown queue => DEFER with the reason,
                # never admit blind, never die silent.
                raise RuntimeError(
                    "queue picture unavailable: collection error")
            decision, reasons, facts = evaluate(block, tiers_doc, runs)
        except Exception as e:  # fail-soft: defer, never admit blind
            decision, reasons, facts = "DEFERRED", [f"admission evaluation error: {type(e).__name__}: {e}"], {"tier": block["que_tier"], "queued_depth": -1, "after": {}, "chain": {}}
        pathlib.Path(a.comment_out).write_text(stamp(fname, block, decision, reasons, facts, a.run_url))
        out = {
            "matched": "true",
            "decision": decision.lower(),
            "label": "swarm-admitted" if decision == "ADMITTED" else "deferred-by-tier",
            "template": fname,
        }
    if a.github_output:
        with open(a.github_output, "a") as fh:
            for k, v in out.items():
                fh.write(f"{k}={v}\n")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
