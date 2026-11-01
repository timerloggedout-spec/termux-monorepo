"""nc-1 evaluator tests — ordered stack, honesty rules, class exclusion."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "doe"))
import nc1_evaluator as ev  # noqa: E402

TAU = {"chat": 0.25, "github": 0.25, "docs": 0.25, "records": 0.33}
DENSE = "PR #2865 merged d3bf60dae3 ✓ gate ✓ tokens 12 ref #1734 run 41255317900"
PROSE = ("This is a long explanatory paragraph that walks through the "
         "reasoning in ordinary sentences without carrying identifiers "
         "or outcomes or references of any kind at all whatsoever.")


def unit(uid, stratum, label, text, **kw):
    u = {"unit_id": uid, "stratum": stratum, "label": label, "text": text,
         "l1_verdict": None, "l1_at": None, "l1_evidence": "none"}
    u.update(kw)
    u["_tokens"] = len(text.split())
    return u


def test_ordered_arms_and_cascade():
    units = [
        unit("c-drift", "chat", "drift", PROSE),
        unit("c-ok", "chat", "compliant", DENSE),
        unit("d-drift", "docs", "drift", PROSE),   # only L3 reaches docs
        unit("d-ok", "docs", "compliant", DENSE),
    ]
    flags = ev.layer_flags(units, TAU, {})
    l1 = ev.run_arm(units, flags, ["L1"])
    full = ev.run_arm(units, flags, ["L1", "L2", "L3"])
    assert l1["units_covered"] == 2                      # chat only
    assert l1["fn_uncovered"] == 1                       # docs drift out of reach
    assert full["tp"] == 2 and full["fp"] == 0
    assert full["recall_global"] == 1.0
    assert full["tokens_scanned"] > l1["tokens_scanned"]


def test_pan_class_excluded_but_counted():
    units = [
        unit("p1", "github", "prose_about_notation", PROSE),
        unit("g-ok", "github", "compliant", DENSE),
    ]
    flags = ev.layer_flags(units, TAU, {})
    full = ev.run_arm(units, flags, ["L1", "L2", "L3"])
    assert full["tp"] == 0 and full["fp"] == 0           # pan never in binary
    assert full["prose_about_notation_flagged"] == 1     # diagnostic count


def test_escape_not_established_without_explicit_l1():
    units = [unit("c-drift", "chat", "drift", PROSE)]
    flags = ev.layer_flags(units, TAU, {})
    full = ev.run_arm(units, flags, ["L1", "L2", "L3"])
    esc = ev.escape_and_latency(units, full["_flagged"])
    assert esc["escape_rate"] is None
    assert esc["status"] == "NOT_ESTABLISHED"


def test_escape_with_explicit_l1():
    units = [
        unit("c-drift", "chat", "drift", PROSE,
             l1_verdict="pass", l1_evidence="explicit",
             correction_latency_s=120),
        unit("c-ok", "chat", "compliant", DENSE,
             l1_verdict="pass", l1_evidence="explicit"),
    ]
    flags = ev.layer_flags(units, TAU, {})
    full = ev.run_arm(units, flags, ["L1", "L2", "L3"])
    esc = ev.escape_and_latency(units, full["_flagged"])
    assert esc["escape_rate"] == 1.0                     # L1 passed it, FULL caught it
    assert esc["correction_latency"] == 120


def test_l1_feed_join_escape_and_latency():
    units = [
        unit("c-drift", "chat", "drift", PROSE,
             join_key="chatX@2026-10-31T19:00:00Z",
             corrected_at="2026-10-31T19:05:00Z"),
        unit("c-seq", "chat", "drift", PROSE,
             source_ref="doe-expert chat seq 37755"),  # v1 seq ref: never joins
    ]
    feed = [{"chat_id": "chatX", "handoff_ts": "2026-10-31T19:00:00Z",
             "verdict": "confirm", "ts": "2026-10-31T19:01:00Z"}]
    joins = ev.apply_l1_feed(units, feed)
    assert joins == 1
    assert units[0]["l1_evidence"] == "explicit"
    assert units[0]["l1_verdict"] == "pass"          # confirm = intake passed it
    assert units[0]["correction_latency_s"] == 240.0  # corrected_at - feed ts
    assert units[1]["l1_evidence"] == "none"
    flags = ev.layer_flags(units, TAU, {})
    full = ev.run_arm(units, flags, ["L1", "L2", "L3"])
    esc = ev.escape_and_latency(units, full["_flagged"])
    assert esc["escape_rate"] == 1.0                  # passed at L1, caught by FULL
    assert esc["correction_latency"] == 240.0


def test_l1_feed_reject_is_intake_flag():
    units = [unit("c-drift", "chat", "drift", PROSE, join_key="cY@t1")]
    joins = ev.apply_l1_feed(units, [{"unit_ref": "cY@t1",
                                      "verdict": "reject", "ts": "t0"}])
    assert joins == 1 and units[0]["l1_verdict"] == "drift"
    esc = ev.escape_and_latency(units, {})
    assert esc["escape_rate"] is None                 # no L1-passed drift in class


def test_records_density_variant_flags_skeleton():
    skeleton = json.dumps({"provider": "x", "evidence": "not-established",
                           "status": "unknown", "value": None})
    populated = json.dumps({"provider": "x", "evidence": "api-verified",
                            "count": 42, "run": 41255317900})
    units = [unit("r-drift", "records", "drift", skeleton),
             unit("r-ok", "records", "compliant", populated)]
    flags = ev.layer_flags(units, TAU, {})
    full = ev.run_arm(units, flags, ["L1", "L2", "L3"])
    assert full["tp"] == 1 and full["fp"] == 0


if __name__ == "__main__":
    for name, fn in sorted(dict(globals()).items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
