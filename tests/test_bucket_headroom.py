"""QUE #5230 bucket-headroom watcher: derived thresholds, projection,
state transitions, dedupe, unreadable naming, drill. Fixtures only."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ops"))
import bucket_headroom as bh

T0 = 1_800_000_000
APPS = [(5535733, "termux-fleet-collector"), (5537873, "termux-fleet-publisher"),
        (5539430, "termux-fleet-reviewer"), (5539499, "termux-fleet-gate"),
        (5539639, "termux-fleet-lifecycle"), (5560920, "termux-fleet-swarm"),
        (5564430, "termux-fleet-crossreference"), (5565297, "termux-fleet-repostory"),
        (5602904, "termux-fleet-delphioracle"), (5602878, "termux-fleet-moneyball")]


def process_doc():
    doc = {}
    for app_id, slug in APPS:
        doc[slug] = {"app_id": app_id, "slug": slug}
    doc["dupe"] = {"app_id": 5535733, "slug": "termux-fleet-collector"}
    return doc


def apps():
    return bh.enumerate_apps(process_doc())


def read(bucket, remaining, used, ts, reset=None, limit=5000):
    return {"bucket": bucket, "kind": "pat", "source": "fixture",
            "limit": limit, "used": used, "remaining": remaining,
            "reset": reset if reset is not None else T0 + 3600,
            "read_ts": ts, "read_at": bh.iso(ts)}


def feed_with(bucket, state, read_row):
    return {"schema": bh.FEED_SCHEMA, "buckets": [
        {"bucket": bucket, "state": state, "read": read_row, "projection": None}]}


def test_enumerate_apps_dedupes_by_app_id():
    found = apps()
    assert len(found) == 10
    assert found[0]["app_id"] == 5535733
    assert {a["slug"] for a in found} == {slug for _, slug in APPS}


def test_normalize_rate_limit_shape():
    payload = {"resources": {"core": {"limit": 5000, "used": 1254,
                                      "remaining": 3746, "reset": T0 + 3600}}}
    row = bh.normalize_rate_limit(payload, "pat-core", "pat", "fixture", T0)
    assert row["limit"] == 5000 and row["remaining"] == 3746
    assert row["reset"] == T0 + 3600 and row["read_at"] == bh.iso(T0)


def test_low_remaining_without_burn_does_not_page():
    # The anti-hardcode proof: remaining=100 is below any plausible
    # fixed count threshold, but with zero observed burn there is no
    # projected exhaustion before reset -> no page, no event.
    prev = feed_with("pat-core", "ok", read("pat-core", 100, 4900, T0))
    feed, events, page = bh.evaluate([read("pat-core", 100, 4900, T0 + 600)],
                                     apps(), prev, T0 + 600)
    row = next(b for b in feed["buckets"] if b["bucket"] == "pat-core")
    assert row["state"] == "ok" and events == [] and page["action"] == "none"


def test_projection_crossing_pages_despite_high_remaining():
    prev = feed_with("pat-core", "ok", read("pat-core", 4900, 100, T0))
    feed, events, page = bh.evaluate([read("pat-core", 2900, 2100, T0 + 600)],
                                     apps(), prev, T0 + 600)
    row = next(b for b in feed["buckets"] if b["bucket"] == "pat-core")
    assert row["state"] == "alert"
    assert row["projection"]["crosses"] is True
    assert len(events) == 1
    ev = events[0]
    assert ev["schema"] == "que-governor-event/v1"
    assert ev["kind"] == "headroom_alert" and ev["verdict"] == "alert"
    # threshold is the bucket's own live limit, read in the same response
    assert ev["detail"]["threshold"] == 5000 == ev["detail"]["limit"]
    assert page["action"] == "create_or_update" and page["raised"] == ["pat-core"]


def test_repeat_poll_while_alerting_dedupes():
    prev = feed_with("pat-core", "ok", read("pat-core", 4900, 100, T0))
    feed1, events1, _ = bh.evaluate([read("pat-core", 2900, 2100, T0 + 600)],
                                    apps(), prev, T0 + 600)
    assert len(events1) == 1
    feed2, events2, page2 = bh.evaluate([read("pat-core", 900, 4100, T0 + 1200)],
                                        apps(), feed1, T0 + 1200)
    row = next(b for b in feed2["buckets"] if b["bucket"] == "pat-core")
    assert row["state"] == "alert"
    assert events2 == [] and page2["action"] == "none"


def test_cleared_transition_emits_recovered_event():
    prev = feed_with("pat-core", "alert", read("pat-core", 100, 4900, T0))
    # new window: reset moved, remaining restored -> baseline, ok
    feed, events, page = bh.evaluate(
        [read("pat-core", 4990, 10, T0 + 600, reset=T0 + 4200)], apps(), prev, T0 + 600)
    row = next(b for b in feed["buckets"] if b["bucket"] == "pat-core")
    assert row["state"] == "ok"
    assert len(events) == 1 and events[0]["verdict"] == "recovered"
    assert page["cleared"] == ["pat-core"]


def test_subthreshold_polls_produce_no_page_no_events():
    prev = feed_with("pat-core", "ok", read("pat-core", 4500, 500, T0))
    feed, events, page = bh.evaluate([read("pat-core", 4400, 600, T0 + 600)],
                                     apps(), prev, T0 + 600)
    row = next(b for b in feed["buckets"] if b["bucket"] == "pat-core")
    assert row["state"] == "ok" and events == [] and page["action"] == "none"
    assert feed["alerting"] == []


def test_exhausted_bucket_pages_immediately():
    feed, events, page = bh.evaluate([read("pat-core", 0, 5000, T0)],
                                     apps(), None, T0)
    row = next(b for b in feed["buckets"] if b["bucket"] == "pat-core")
    assert row["state"] == "alert" and len(events) == 1
    assert events[0]["detail"]["exhausted"] is True


def test_reset_window_change_resets_baseline():
    prev = feed_with("pat-core", "ok", read("pat-core", 4000, 1000, T0, reset=T0 + 600))
    feed, events, page = bh.evaluate(
        [read("pat-core", 500, 4500, T0 + 600, reset=T0 + 4200)], apps(), prev, T0 + 600)
    row = next(b for b in feed["buckets"] if b["bucket"] == "pat-core")
    assert row["projection"] is None and row["state"] == "ok" and events == []


def test_unreadable_apps_named_never_skipped():
    swarm_read = read("app-termux-fleet-swarm", 8000, 4500, T0, limit=12500)
    feed, events, page = bh.evaluate([swarm_read], apps(), None, T0)
    assert len(feed["buckets"]) == 12  # pat-core + github-token + 10 apps
    by_bucket = {b["bucket"]: b for b in feed["buckets"]}
    assert by_bucket["app-termux-fleet-swarm"]["state"] == "ok"
    assert by_bucket["app-termux-fleet-publisher"]["unreadable_reason"] == "sec03_unprovisioned"
    assert by_bucket["app-termux-fleet-collector"]["unreadable_reason"] == "no_read_supplied"
    assert by_bucket["pat-core"]["state"] == "unreadable"
    assert events == []


def test_drill_produces_one_synthetic_alert_and_dedupes():
    feed, events, page = bh.evaluate([], apps(), None, T0, drill=True, session="drill-1")
    drill_events = [e for e in events if e["detail"]["bucket"] == "synthetic-drill"]
    assert len(drill_events) == 1
    assert drill_events[0]["detail"]["synthetic_test"] is True
    assert page["synthetic"] is True and "synthetic-drill" in page["raised"]
    feed2, events2, page2 = bh.evaluate([], apps(), feed, T0 + 600, drill=True)
    assert [e for e in events2 if e["detail"]["bucket"] == "synthetic-drill"] == []
    assert page2["action"] == "none"


def test_collect_marks_absent_mintable_tokens():
    reads = bh.collect({}, T0)
    by_bucket = {r["bucket"]: r for r in reads}
    assert by_bucket["app-termux-fleet-swarm"]["unreadable_reason"] == "mint_unavailable"
    assert "pat-core" not in by_bucket  # absent PAT is evaluate's named gap


def test_main_evaluate_writes_feed_events_page(tmp_path):
    reads = {"reads": [read("pat-core", 0, 5000, T0)]}
    (tmp_path / "reads.json").write_text(json.dumps(reads))
    (tmp_path / "process.json").write_text(json.dumps(process_doc()))
    rc = bh.main(["evaluate", "--reads", str(tmp_path / "reads.json"),
                  "--process", str(tmp_path / "process.json"),
                  "--feed-out", str(tmp_path / "feed.json"),
                  "--events-out", str(tmp_path / "events.jsonl"),
                  "--page-out", str(tmp_path / "page.json"),
                  "--events-dir", str(tmp_path / "events"),
                  "--now", str(T0)])
    assert rc == 0
    feed = json.loads((tmp_path / "feed.json").read_text())
    assert feed["schema"] == "bucket-headroom/v1" and feed["alerting"] == ["pat-core"]
    batch = tmp_path / "events" / f"governor-events-{bh.iso(T0)[:10]}.jsonl"
    lines = batch.read_text().strip().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["kind"] == "headroom_alert"


# ---- probe semantics (Cadence countersign #5152 c.6842945679) ----

def unknown_row(bucket="gemini-api-free"):
    return {"bucket": bucket, "state": "unreadable",
            "headroom": {"kind": "unknown", "value": None, "unit": "requests",
                         "as_of": bh.iso(T0), "valid_until": None},
            "probe_episode": {"episode_id": f"{bucket}@unknown-1", "probed": False}}


def probe_event(bucket="gemini-api-free", outcome="success", draw=7,
                authoritative=None, dimension="daily_requests", reset_at=None):
    headroom = bh.probe_headroom(outcome, token_draw=draw,
                                 authoritative_remaining=authoritative,
                                 quota_dimension=dimension, reset_at=reset_at,
                                 observed_at=bh.iso(T0))
    return bh.build_probe_event(
        ts=T0, instance_key="probe-fixture", provider="google",
        account_ref="acct-fixture", model="gemini-fixture", route="cli",
        bucket_id=bucket, quota_dimension=dimension,
        source={"type": "probe", "ref": "fixture", "observed_at": bh.iso(T0),
                "reset_window": "daily", "reset_tz": "America/Los_Angeles"},
        probe={"run_id": "r1", "request_count": 1, "token_draw": draw,
               "retry_count": 0},
        outcome=outcome, headroom=headroom, coverage_scope="exact-bucket",
        prev_hash=None)


def test_feed_rows_carry_typed_headroom():
    feed, _, _ = bh.evaluate([read("pat-core", 3000, 2000, T0)], apps(), None, T0)
    by_bucket = {b["bucket"]: b for b in feed["buckets"]}
    exact = by_bucket["pat-core"]["headroom"]
    assert exact["kind"] == "exact" and exact["value"] == 3000
    assert exact["valid_until"] == bh.iso(T0 + 3600)
    unknown = by_bucket["github-token"]["headroom"]
    assert unknown["kind"] == "unknown" and unknown["value"] is None


def test_probe_success_is_lower_bound_not_exact():
    row, verdict = bh.apply_probe(unknown_row(), probe_event())
    assert verdict == "converted"
    assert row["headroom"]["kind"] == "lower_bound"
    assert row["headroom"]["value"] == 7  # the probe draw itself, nothing more
    assert row["measured"]["via"] == "quota_probe"


def test_probe_success_with_authoritative_remaining_is_exact():
    row, verdict = bh.apply_probe(unknown_row(),
                                  probe_event(authoritative=13))
    assert verdict == "converted" and row["headroom"]["kind"] == "exact"
    assert row["headroom"]["value"] == 13


def test_probe_quota_terminal_identified_dimension_zero_until_reset():
    ev = probe_event(outcome="quota_terminal", reset_at=bh.iso(T0 + 3600))
    row, verdict = bh.apply_probe(unknown_row(), ev)
    assert verdict == "converted"
    assert row["headroom"]["kind"] == "zero_until_reset"
    assert row["headroom"]["value"] == 0
    assert row["headroom"]["valid_until"] == bh.iso(T0 + 3600)


def test_probe_quota_terminal_without_dimension_does_not_convert():
    ev = probe_event(outcome="quota_terminal", dimension=None)
    row, verdict = bh.apply_probe(unknown_row(), ev)
    assert verdict == "evidence_only"
    assert row["headroom"]["kind"] == "unknown"
    assert row["probe_episode"]["probed"] is True  # episode probe consumed


def test_probe_transient_and_inconclusive_are_evidence_only():
    for outcome in ("transient_rate_limit", "auth_error", "route_error",
                    "inconclusive"):
        row, verdict = bh.apply_probe(unknown_row(), probe_event(outcome=outcome))
        assert verdict == "evidence_only", outcome
        assert row["headroom"]["kind"] == "unknown"


def test_one_probe_per_unknown_episode():
    row, verdict = bh.apply_probe(unknown_row(), probe_event(outcome="inconclusive"))
    assert verdict == "evidence_only"
    row2, verdict2 = bh.apply_probe(row, probe_event())
    assert verdict2 == "refused_duplicate_probe"
    assert row2["headroom"]["kind"] == "unknown"


def test_probe_exact_bucket_binding():
    row, verdict = bh.apply_probe(unknown_row("bucket-a"),
                                  probe_event(bucket="bucket-b"))
    assert verdict == "bucket_mismatch"
    assert row["probe_episode"]["probed"] is False


def test_probe_event_hash_chain():
    e1 = probe_event()
    e2 = bh.build_probe_event(
        ts=T0 + 60, instance_key="probe-fixture", provider="google",
        account_ref="acct-fixture", model="gemini-fixture", route="cli",
        bucket_id="gemini-api-free", quota_dimension="daily_requests",
        source={"type": "probe", "ref": "fixture", "observed_at": bh.iso(T0 + 60),
                "reset_window": "daily", "reset_tz": "America/Los_Angeles"},
        probe={"run_id": "r2", "request_count": 1, "token_draw": 7,
               "retry_count": 0},
        outcome="inconclusive",
        headroom=bh.probe_headroom("inconclusive", observed_at=bh.iso(T0 + 60)),
        coverage_scope="exact-bucket", prev_hash=e1["hash"])
    assert e2["prev_hash"] == e1["hash"] and e2["hash"] != e1["hash"]
    assert e1["schema"] == "quota-probe-event/v1" and e1["kind"] == "quota_probe"
    for field in ("event_id", "instance_key", "bucket_id", "quota_dimension",
                  "source", "probe", "outcome", "headroom", "coverage_scope",
                  "prev_hash", "hash"):
        assert field in e1


def test_record_probe_cli_end_to_end(tmp_path):
    feed, _, _ = bh.evaluate([], apps(), None, T0)
    feed_path = tmp_path / "feed.json"
    feed_path.write_text(json.dumps(feed))
    probe = {"provider": "github-pat", "account_or_project_ref": "owner",
             "model": None, "route": "/rate_limit", "bucket_id": "pat-core",
             "quota_dimension": "core", "instance_key": "watcher-fixture",
             "source": {"type": "probe", "ref": "fixture",
                        "observed_at": bh.iso(T0), "reset_window": "hourly",
                        "reset_tz": "UTC"},
             "probe": {"run_id": "rp1", "request_count": 1, "token_draw": 1,
                       "retry_count": 0},
             "outcome": "success", "coverage_scope": "exact-bucket"}
    probe_path = tmp_path / "probe.json"
    probe_path.write_text(json.dumps(probe))
    ledger = tmp_path / "ledger.jsonl"
    out = tmp_path / "feed-out.json"
    rc = bh.main(["record-probe", "--feed", str(feed_path),
                  "--probe", str(probe_path), "--ledger", str(ledger),
                  "--feed-out", str(out), "--now", str(T0)])
    assert rc == 0
    lines = ledger.read_text().strip().splitlines()
    assert len(lines) == 1
    new_feed = json.loads(out.read_text())
    row = next(b for b in new_feed["buckets"] if b["bucket"] == "pat-core")
    assert row["headroom"]["kind"] == "lower_bound" and row["headroom"]["value"] == 1
    # second probe in the same episode: refused, ledger unchanged
    out2 = tmp_path / "feed-out2.json"
    rc = bh.main(["record-probe", "--feed", str(out),
                  "--probe", str(probe_path), "--ledger", str(ledger),
                  "--feed-out", str(out2), "--now", str(T0 + 60)])
    assert rc == 0
    assert len(ledger.read_text().strip().splitlines()) == 1
