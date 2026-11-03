"""Offline tests for the geography leg (study_geo.py, #4158).

Location records from build A's calendar, route planning via an
injected provider and via coordinates, temple routes on a campus
path, audio cues, and voice customization as data.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from study_calendar import intake_calendar  # noqa: E402
from study_geo import (apply_voice_customization, audio_cues,  # noqa: E402
                       build_temple_route, haversine_minutes,
                       location_records, route_to_assessment)

NOW = datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc)

DOC = {
    "classes": [{"course": "BIO 101", "days": ["Tue"],
                 "start": "10:00", "end": "11:15",
                 "building": "Science Hall", "room": "204"}],
    "assessments": [{"course": "BIO 101", "kind": "final",
                     "date": "2026-12-10", "time": "18:00",
                     "building": "Gym Annex", "room": "B"}],
}


def test_location_records_dedupe():
    cal = intake_calendar(DOC, NOW)
    recs = location_records(cal)
    locs = {r["location"] for r in recs}
    assert locs == {"Science Hall 204", "Gym Annex B"}
    gym = [r for r in recs if r["location"] == "Gym Annex B"][0]
    assert gym["used_by"] == ["final:BIO 101"]


def test_route_with_provider_and_coords():
    cal = intake_calendar(DOC, NOW)
    final = cal["assessments"][0]
    plan = route_to_assessment(final, "Dorm", NOW,
                               travel_fn=lambda a, b: 17.0)
    assert plan["travel_minutes"] == 17.0
    assert plan["source"] == "provider"
    assert plan["depart_by"].endswith("17:33:00Z")  # 18:00 - 17 - 10
    coords = {"Dorm": (40.0, -75.0), "Gym Annex B": (40.01, -75.0)}
    est = route_to_assessment(final, "Dorm", NOW, coords=coords)
    assert est["travel_minutes"] == \
        haversine_minutes(coords["Dorm"], coords["Gym Annex B"])
    assert est["source"] == "coordinate-estimate"
    try:
        route_to_assessment(final, "Dorm", NOW)
    except ValueError as e:
        assert "travel_fn" in str(e)
    else:
        raise AssertionError("route without provider/coords must raise")


def test_temple_route_cues_and_voice_edits():
    route = build_temple_route(
        [{"name": "dorm door", "location": "Dorm"},
         {"name": "library steps", "location": "Library"},
         {"name": "lab bench", "location": "Science Hall 204"}],
        [{"term": "Cell membrane"}, {"term": "Nucleus"},
         {"term": "Mitochondria"}], NOW)
    assert [p["locus"] for p in route["placements"]] == \
        ["dorm door", "library steps", "lab bench"]
    assert route["claims_ceiling"].startswith("ordered/concrete")
    cues = audio_cues(route)
    assert len(cues) == 3
    assert "library steps" in cues[1]["cue"]
    assert "Nucleus" in cues[1]["cue"]
    renamed = apply_voice_customization(
        route, "rename library steps to the big steps", NOW)
    assert renamed["applied"] is True
    assert renamed["route"]["waypoints"][1]["name"] == "the big steps"
    assert renamed["route"]["placements"][1]["locus"] == \
        "the big steps"
    moved = apply_voice_customization(
        route, "move Nucleus to lab bench", NOW)
    assert moved["applied"] is True
    assert moved["route"]["placements"][1]["locus"] == "lab bench"
    unknown = apply_voice_customization(route, "sing me a song", NOW)
    assert unknown["applied"] is False
    assert "unrecognized" in unknown["reason"]
