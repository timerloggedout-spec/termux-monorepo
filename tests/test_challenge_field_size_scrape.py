"""Offline parser tests for scripts/challenge/field_size_scrape.py.

Fixtures mirror the live page shapes verified 2026-10-28 (server-rendered
counts on AWS Builder Center + Devpost, embedded JSON on lablab.ai).
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "field_size_scrape", ROOT / "scripts/challenge/field_size_scrape.py")
fss = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fss)


def test_builder_center_participants():
    html = "<header>Strands Decider</header><span>5917 participants</span>"
    assert fss.parse_builder_center(html) == {"participants": 5917}


def test_builder_center_no_count():
    assert fss.parse_builder_center("<html>none</html>") == {"participants": None}


def test_builder_center_prize_text_is_not_a_project_count():
    # "The top 5 projects each receive..." must never parse as a field size.
    html = "<b>Prizes:</b> The top 5 projects each receive $100 in AWS credits"
    assert fss.parse_builder_center(html) == {"participants": None}


def test_devpost_participants():
    html = '<a href="/participants">Participants (1909)</a>'
    assert fss.parse_devpost(html) == {"participants": 1909}


def test_devpost_gallery_unpublished_is_zero():
    html = "The hackathon managers haven't published this gallery yet"
    assert fss.parse_devpost_gallery(html)["projects"] == 0


def test_devpost_gallery_pagination_total():
    html = "<div>49 – 53 of 53</div>"
    assert fss.parse_devpost_gallery(html) == {"projects": 53}


def test_lablab_initial_participants():
    html = '{"eventState":"upcoming","initialParticipants":1617,"x":1}'
    assert fss.parse_lablab(html) == {"participants": 1617}


def test_apply_update_status_ladder():
    ev = {"field_size": {"status": "open_task", "participants": None, "projects": None},
          "metrics_internal": {"win_probability": {"inputs": {}}}}
    fss.apply_update(ev, {"participants": 10}, "2026-10-28T00:00:00Z")
    assert ev["field_size"]["status"] == "partial"
    fss.apply_update(ev, {"projects": 3}, "2026-10-28T00:00:00Z")
    assert ev["field_size"]["status"] == "established"
    assert ev["metrics_internal"]["win_probability"]["inputs"]["participants"] == 10


def test_apply_update_never_nulls_known_projects():
    ev = {"field_size": {"status": "established", "participants": 252, "projects": 40}}
    fss.apply_update(ev, {"participants": 253}, "2026-10-28T00:00:00Z")
    assert ev["field_size"]["projects"] == 40
    assert ev["field_size"]["status"] == "established"
