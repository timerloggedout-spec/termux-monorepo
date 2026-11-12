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

The queue picture comes from the collector feeds in the checkout
(#4979: ops/que/feeds/, freshness-gated at 2 collector cycles); the
live paginated census is only the stale-feed fallback, its failures
are stamped with the failed status+page and API error class, and a
picture failure never defers a non-flow tier (dispatch-tiers v2
admits tiers 1-3 at any depth).

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

# Queue picture of record (#4979): the collector feeds in the checkout
# (ops/que/feeds/, published by que-feed-collect.yml on a */10 cron),
# freshness-gated at 2 collector cycles. The live paginated census is
# only the stale-feed fallback.
COLLECTOR_CYCLE_SECONDS = 600
FEED_FRESH_SECONDS = 2 * COLLECTOR_CYCLE_SECONDS

# dispatch-tiers v2 flood rules (ops/quota/dispatch-tiers.json): tiers
# 1-3 are "admitted at any depth"; only tier 4 self-defers on queued
# depth. A non-flow tier's verdict therefore does not consume the queue
# picture, and a picture failure must not defer it (#4979 point 3).
NON_FLOW_TIERS = {1, 2, 3}


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


def _parse_ts(text):
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def picture_from_feeds(feeds_dir, now, max_age_seconds=FEED_FRESH_SECONDS):
    """The collector-feed picture, or None when missing/stale.

    Reads queue-by-tier.json (as-of = generated_at) + state.json
    (active runs) from the checkout. Fresh = generated_at within
    max_age_seconds of now (the #4979 gate: <= 2 collector cycles).
    """
    import pathlib

    try:
        by_tier = json.loads((pathlib.Path(feeds_dir) / "queue-by-tier.json").read_text())
        state = json.loads((pathlib.Path(feeds_dir) / "state.json").read_text())
    except Exception:
        return None
    generated = _parse_ts(by_tier.get("generated_at"))
    if generated is None or (now - generated).total_seconds() > max_age_seconds:
        return None
    runs = [
        {"name": v.get("workflow"), "status": v.get("status"), "created_at": v.get("created_at", "")}
        for v in (state.get("active") or {}).values()
    ]
    return runs, {"source": "collector-feeds", "as_of": by_tier["generated_at"]}


def _feeds_stale_detail(feeds_dir, now, max_age_seconds):
    import pathlib

    try:
        by_tier = json.loads((pathlib.Path(feeds_dir) / "queue-by-tier.json").read_text())
        generated = by_tier.get("generated_at")
        gen_dt = _parse_ts(generated)
        if gen_dt is not None:
            age = int((now - gen_dt).total_seconds())
            return f"collector feeds stale (as-of {generated}, age {age}s > gate {max_age_seconds}s)"
        return "collector feeds unreadable (no generated_at)"
    except Exception:
        return "collector feeds missing/unreadable in checkout"


def resolve_picture(feeds_dir, runs_path, now, max_age_seconds=FEED_FRESH_SECONDS):
    """Resolve the queue picture: fresh collector feeds first, the
    live fallback picture second (#4979 points 1-2).

    Returns {status: "ok", runs, source, as_of} or
    {status: "unavailable", detail} where detail NAMES the failure:
    the failed status+page and API error class of the live fallback,
    plus the feed staleness that forced the fallback.
    """
    import pathlib

    feed = picture_from_feeds(feeds_dir, now, max_age_seconds)
    if feed is not None:
        runs, meta = feed
        return {"status": "ok", "runs": runs, **meta}
    stale = _feeds_stale_detail(feeds_dir, now, max_age_seconds)
    try:
        raw = json.loads(pathlib.Path(runs_path).read_text())
    except Exception:
        return {"status": "unavailable",
                "detail": f"{stale}; no live fallback picture was collected"}
    if isinstance(raw, list):
        return {"status": "ok", "runs": raw, "source": "live-fallback", "as_of": None}
    if isinstance(raw, dict) and isinstance(raw.get("runs"), list):
        return {"status": "ok", "runs": raw["runs"],
                "source": raw.get("picture_source", "live-fallback"),
                "as_of": raw.get("collected_at")}
    if isinstance(raw, dict) and raw.get("collection_error"):
        err = raw["collection_error"]
        if isinstance(err, dict):
            cause = (f"live fallback failed at status={err.get('failed_status')} "
                     f"page={err.get('failed_page')} "
                     f"(error class: {err.get('error_class')})")
        else:
            cause = "live fallback collection error (legacy sentinel, no detail recorded)"
        return {"status": "unavailable", "detail": f"{stale}; {cause}"}
    return {"status": "unavailable",
            "detail": f"{stale}; live fallback picture had an unrecognized shape"}


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
    pic = facts.get("picture")
    if pic:
        if pic.get("source") == "unavailable":
            parts.append(
                f"picture: unavailable — {pic.get('detail', 'cause not recorded')}"
                + (" · tolerated for this tier under #4979 (dispatch-tiers v2: tiers 1-3 "
                   "admit at any depth; the verdict does not consume the queue picture; "
                   "after/chain legs saw an empty picture)"
                   if pic.get("tolerated") else ""))
        else:
            parts.append(f"picture: {pic.get('source')} · as-of {pic.get('as_of') or 'not recorded'}")
    if reasons:
        parts.append("**deferred because:** " + "; ".join(reasons))
        parts.append("Fail-soft of record: the filing stays queued as `deferred-by-tier`; the QUE admission drain re-evaluates it — nothing was spawned.")
    else:
        parts.append("The route named above executes under its own intake; this stamp is the admission receipt of record (QUE measurement-plane transition: enqueued → admitted).")
    parts.append(f"admission run: {run_url}")
    return "\n\n".join(parts)


def picture_gate(argv):
    """Workflow gate: are the checkout's collector feeds fresh?

    Prints fresh|stale and (with --github-output) writes feeds_fresh +
    feeds_as_of. The workflow spends live API calls on the fallback
    census only when this gate says stale (#4979 point 1).
    """
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--feeds-dir", default="ops/que/feeds")
    ap.add_argument("--max-feed-age-seconds", type=int, default=FEED_FRESH_SECONDS)
    ap.add_argument("--now", default="")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args(argv)
    now = _parse_ts(a.now) if a.now else datetime.now(timezone.utc)
    feed = picture_from_feeds(a.feeds_dir, now, a.max_feed_age_seconds) if now else None
    fresh = feed is not None
    print("fresh" if fresh else "stale")
    if a.github_output:
        with open(a.github_output, "a") as fh:
            fh.write(f"feeds_fresh={'true' if fresh else 'false'}\n")
            fh.write(f"feeds_as_of={feed[1]['as_of'] if fresh else ''}\n")
    return 0


def main(argv):
    if argv and argv[0] == "picture-gate":
        return picture_gate(argv[1:])
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--templates-dir", required=True)
    ap.add_argument("--tiers", required=True)
    ap.add_argument("--runs-file", required=True, help="live fallback picture (JSON), read only when the collector feeds are stale")
    ap.add_argument("--feeds-dir", default="ops/que/feeds")
    ap.add_argument("--max-feed-age-seconds", type=int, default=FEED_FRESH_SECONDS)
    ap.add_argument("--now", default="", help="ISO timestamp override (tests)")
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
            now = _parse_ts(a.now) if a.now else datetime.now(timezone.utc)
            picture = resolve_picture(a.feeds_dir, a.runs_file, now,
                                      a.max_feed_age_seconds)
            if picture["status"] == "ok":
                decision, reasons, facts = evaluate(
                    block, tiers_doc, picture["runs"], now=now)
                facts["picture"] = {"source": picture["source"],
                                    "as_of": picture.get("as_of")}
            elif block["que_tier"] in NON_FLOW_TIERS:
                # #4979 point 3: a non-flow tier's verdict does not
                # consume the queue picture (dispatch-tiers v2 admits
                # tiers 1-3 at any depth), so a picture failure must
                # not defer it. Evaluate against an empty picture and
                # stamp the tolerance with the named cause.
                decision, reasons, facts = evaluate(block, tiers_doc, [], now=now)
                facts["picture"] = {"source": "unavailable",
                                    "detail": picture["detail"],
                                    "tolerated": True}
            else:
                # Flow tier + no picture: DEFER, naming the cause
                # (failed status+page + API error class, #4979 point 2)
                # instead of the old generic sentinel text.
                decision = "DEFERRED"
                reasons = [f"queue picture unavailable: {picture['detail']}"]
                facts = {"tier": block["que_tier"], "queued_depth": -1,
                         "after": {}, "chain": {},
                         "picture": {"source": "unavailable",
                                     "detail": picture["detail"]}}
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
