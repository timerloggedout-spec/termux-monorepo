import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import que_item_fields as f  # noqa: E402


def mandate(**kw):
    base = dict(policy_version="queue.dispatch-tiers/v2@deadbeef", scope="project-task.yml",
                strength="explicit", matched_rules=["project-task.yml"], source="github",
                receiving_scope="issues.new", sender="timerloggedout-spec", trigger_id="issue#1")
    base.update(kw)
    return f.make_mandate(**base)


def test_mandate_is_immutable_and_round_trips():
    m = mandate()
    with pytest.raises(TypeError):
        m["scope"] = "wider"  # type: ignore[index]
    body = "stamp text\n\n" + f.render_block(m)
    blocks = f.parse_blocks(body)
    assert len(blocks) == 1 and blocks[0]["strength"] == "explicit"
    assert f.mandate_changed(blocks[0], m) == []


def test_wider_scope_is_a_new_item():
    assert f.mandate_changed(mandate(), mandate(scope="everything")) == ["scope"]


def test_strength_rules():
    assert f.strength_for_sender("dependabot[bot]") == "inferred"
    assert f.strength_for_sender("timerloggedout-spec") == "explicit"
    with pytest.raises(f.FieldError):
        mandate(strength="maybe")
    with pytest.raises(f.FieldError):
        mandate(strength="inferred", matched_rules=[])


def test_policy_version_stable():
    assert f.policy_version("x/v1", b"a") == f.policy_version("x/v1", b"a")
    assert f.policy_version("x/v1", b"a") != f.policy_version("x/v1", b"b")


def test_report_enum_attention_and_stamp():
    r = f.make_report("blocked", "needs a token", receipt=["#1"],
                      attention={"question": "Mint the PAT?", "options": ["yes", "no"]})
    assert f.reply_stamp("que-superagent", r) == (
        "blocked que-superagent · verified receipt #1 · owner action: Mint the PAT?")
    ok = f.make_report("ready", "merged", receipt=["#2", "abc1234"])
    assert f.reply_stamp("x", ok).startswith("live x")
    assert f.stamp_state(f.make_report("failed", "boom")) == "down"
    with pytest.raises(f.FieldError):
        f.make_report("done", "x")
    with pytest.raises(f.FieldError):
        f.make_report("ready", "x", attention={"question": ""})


def test_hitl_rate_counts_only_structured_attention():
    rs = [f.make_report("progress", "asking you: ok?"),  # prose question ≠ attention
          f.make_report("blocked", "x", attention={"question": "ok?"})]
    assert f.hitl_rate(rs) == 0.5
    assert f.hitl_rate([]) == 0.0


def test_latest_and_bad_json_skipped():
    body = (f.render_block(f.make_report("progress", "a")) + "\n<!-- que-report/v1\n{bad\n-->\n"
            + f.render_block(f.make_report("ready", "b")))
    assert f.latest(f.parse_blocks(body), f.REPORT_SCHEMA)["summary"] == "b"
