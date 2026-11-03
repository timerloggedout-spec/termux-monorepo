"""StudySprint geography — RFP-D1-6 builds ④⑤ (issue #4158).

Consumes build A's calendar/location records (study_calendar):

4. **Maps** — location records for classes + assessments (open
   data first: the records come from the student's own calendar,
   not a scraped directory), plus route + travel-time assistance
   to the assessment room. Travel times come from an INJECTED
   provider; the offline default estimates from injected
   coordinates (haversine at walking speed) so tests and the demo
   never touch a network.
5. **Temple routes on real geography** — the method of loci laid
   over the student's actual campus path: waypoints become loci,
   term-bank items are placed along the walk (study_memory's
   palace builder), an audio-cue script narrates the walk, and
   voice-input transcripts customize the route (rename a waypoint,
   move an item) as data — no live device dependency in this
   layer.

Claims ceiling: the geography leg inherits build A's ceiling
(logistics support) AND the loci ceiling from the memory batch —
ordered/concrete recall, not understanding.

Offline and deterministic given explicit inputs.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timedelta, timezone

from study_calendar import CLAIMS_CEILING as LOGISTICS_CEILING
from study_memory import LOCI_CLAIMS_CEILING, build_palace

GEO_RECEIPT_SCHEMA = "studysprint-geo-receipt/v1"
WALKING_KMH = 5.0


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _receipt(kind: str, now: datetime, **fields) -> dict:
    out = {"schema": GEO_RECEIPT_SCHEMA, "kind": kind,
           "observed_at": _iso(now),
           "claims_ceiling": LOGISTICS_CEILING}
    out.update(fields)
    return out


# ---------------------------------------------------------------- maps

def location_records(calendar: dict) -> list:
    """Deduped location records from a calendar: every building/
    room the student actually has to be in, with what happens
    there."""
    records = {}
    for c in calendar.get("classes") or []:
        loc = c.get("location")
        if loc:
            rec = records.setdefault(
                loc, {"location": loc, "building": c.get("building"),
                      "room": c.get("room"), "used_by": []})
            rec["used_by"].append(f"class:{c.get('course')}")
    for a in calendar.get("assessments") or []:
        loc = a.get("location")
        if loc:
            rec = records.setdefault(
                loc, {"location": loc, "building": a.get("building"),
                      "room": a.get("room"), "used_by": []})
            rec["used_by"].append(
                f"{a.get('kind')}:{a.get('course')}")
    return [records[k] for k in sorted(records)]


def haversine_minutes(a: tuple, b: tuple,
                      kmh: float = WALKING_KMH) -> float:
    """Offline travel estimate between (lat, lon) pairs."""
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2)
         * math.sin((lon2 - lon1) / 2) ** 2)
    km = 6371.0 * 2 * math.asin(math.sqrt(h))
    return round(km / kmh * 60.0, 1)


def route_to_assessment(assessment: dict, origin: str,
                        now: datetime, travel_fn=None,
                        coords: dict | None = None,
                        buffer_minutes: int = 10) -> dict:
    """Plan the trip to one assessment: travel time from the
    injected provider (or the coordinate estimate), a buffer, and
    the leave-by time. travel_fn(origin, destination) -> minutes
    is the provider seam (a maps API in production; fixtures in
    tests)."""
    destination = assessment.get("location", "")
    if travel_fn is not None:
        minutes = float(travel_fn(origin, destination))
        source = "provider"
    elif coords and origin in coords and destination in coords:
        minutes = haversine_minutes(coords[origin],
                                    coords[destination])
        source = "coordinate-estimate"
    else:
        raise ValueError(
            "route needs a travel_fn provider or coordinates for "
            f"both {origin!r} and {destination!r}")
    day = datetime.fromisoformat(str(assessment["date"])).date()
    hh, mm = str(assessment.get("time") or "09:00").split(":")
    starts = datetime(day.year, day.month, day.day, int(hh), int(mm),
                      tzinfo=now.tzinfo)
    depart = starts - timedelta(minutes=minutes + buffer_minutes)
    return _receipt(
        "route-plan", now, course=assessment.get("course"),
        assessment_kind=assessment.get("kind"), origin=origin,
        destination=destination, travel_minutes=minutes,
        buffer_minutes=buffer_minutes, source=source,
        assessment_starts=_iso(starts), depart_by=_iso(depart))


# ------------------------------------------------------- temple routes

def build_temple_route(waypoints, items, now: datetime) -> dict:
    """Lay the method of loci over a real campus path.

    waypoints: ordered [{name, location}] — the student's actual
    walk. items: term-bank entries placed one per waypoint, in
    order (study_memory.build_palace does the placing)."""
    names = [w["name"] for w in waypoints or []]
    palace = build_palace(
        ["Campus route"],
        {"Campus route": list(items or [])}, route=names)
    out = _receipt("temple-route", now, waypoints=waypoints,
                   placements=palace["placements"])
    out["claims_ceiling"] = LOCI_CLAIMS_CEILING
    return out


def audio_cues(temple_route: dict) -> list:
    """The walk's audio-cue script: one cue per placement, phrased
    for listening while walking ('At the library steps, picture
    ...'). Data only — a TTS/device layer speaks it."""
    cues = []
    for p in temple_route.get("placements") or []:
        cues.append({
            "seq": p["position"],
            "at": p["locus"],
            "cue": (f"At the {p['locus']}, picture this: "
                    f"{p['item']}. Let it stick to the place."),
        })
    return cues


_RENAME = re.compile(r"^(?:rename|call)\s+(.+?)\s+(?:to\s+)?(.+)$",
                     re.IGNORECASE)
_MOVE = re.compile(r"^move\s+(.+?)\s+to\s+(.+)$", re.IGNORECASE)


def apply_voice_customization(temple_route: dict, transcript: str,
                              now: datetime) -> dict:
    """Voice input as data: parse one spoken edit command into a
    route edit record. Supported: 'rename <waypoint> to <name>' /
    'call <waypoint> <name>' and 'move <item> to <waypoint>'.
    Returns the edited route + the edit receipt; unknown commands
    are reported, never silently dropped."""
    text = str(transcript or "").strip()
    route = {**temple_route,
             "waypoints": [dict(w) for w in
                           temple_route.get("waypoints") or []],
             "placements": [dict(p) for p in
                            temple_route.get("placements") or []]}
    m = _MOVE.match(text)
    if m:
        item, target = m.group(1).strip(), m.group(2).strip()
        for p in route["placements"]:
            if p["item"].lower() == item.lower():
                p["locus"] = target
                return _receipt("voice-edit", now, applied=True,
                                edit={"kind": "move", "item": item,
                                      "to": target},
                                route=route)
        return _receipt("voice-edit", now, applied=False,
                        reason=f"item not on the route: {item!r}",
                        route=route)
    m = _RENAME.match(text)
    if m:
        # waypoint names contain spaces: resolve the old name by
        # matching a known waypoint as the transcript's prefix
        rest = text.split(None, 1)[1] if " " in text else ""
        old = new = None
        for w in sorted(route["waypoints"],
                        key=lambda w: -len(w["name"])):
            name = w["name"]
            if rest.lower().startswith(name.lower()):
                tail = rest[len(name):].strip()
                if tail.lower().startswith("to "):
                    tail = tail[3:].strip()
                old, new = name, tail
                break
        if old is None or not new:
            old, new = m.group(1).strip(), m.group(2).strip()
        hit = False
        for w in route["waypoints"]:
            if w["name"].lower() == old.lower():
                w["name"] = new
                hit = True
        for p in route["placements"]:
            if p["locus"].lower() == old.lower():
                p["locus"] = new
        if hit:
            return _receipt("voice-edit", now, applied=True,
                            edit={"kind": "rename", "from": old,
                                  "to": new},
                            route=route)
        return _receipt("voice-edit", now, applied=False,
                        reason=f"waypoint not on the route: {old!r}",
                        route=route)
    return _receipt("voice-edit", now, applied=False,
                    reason="unrecognized voice command",
                    transcript=text, route=route)


def surface_calendar_geo(doc: dict, now: datetime,
                         topics=(), base_per_day: float = 6.0) -> dict:
    """Assemble the surface state for the calendar + geography
    binding (parity iteration 1, #4414): intake, briefings,
    frequency plan, quiet-hours probes, location records,
    assessment routes, and the temple route — one JSON-ready
    dict every surface renders (TUI at runtime; the web bundle
    at build time, disclosed there as build-time state).

    The doc may carry the surface extension fields `coords`
    ({location: [lat, lon]}), `origin` (where routes start),
    and `waypoints` (the temple walk); without coords, routes
    are omitted rather than faked — the surfaces render the
    locations and say why no route is drawn. Quiet hours are
    probed honestly: one synthetic notification inside today's
    (or the next) class block and one outside it, run through
    apply_quiet_hours itself.
    """
    from study_calendar import (apply_quiet_hours, assessment_briefings,
                                frequency_plan, intake_calendar)

    cal = intake_calendar(doc, now)
    briefings = assessment_briefings(cal, now)
    plan = frequency_plan(cal, base_per_day, now)["plan"]

    # Quiet-hours probes: find the first class block today or in
    # the next 7 days; probe inside it and clear of it.
    probes, probe_day = [], None
    for offset in range(8):
        day = (now + timedelta(days=offset)).date()
        blocks = []
        for c in cal["classes"]:
            if day.weekday() in (c.get("days") or []):
                hh, mm = str(c["start"]).split(":")
                blocks.append(datetime(day.year, day.month, day.day,
                                       int(hh), int(mm),
                                       tzinfo=now.tzinfo))
        if blocks:
            probe_day = day
            probes = [
                {"id": "probe-in-class",
                 "at": blocks[0] + timedelta(minutes=15)},
                {"id": "probe-outside",
                 "at": blocks[0] - timedelta(hours=2)},
            ]
            break
    quiet = None
    if probes:
        raw = apply_quiet_hours(cal, probes, now)

        def _ser(note):
            out = dict(note)
            out["at"] = _iso(out["at"])
            if "release_at" in out:
                out["release_at"] = _iso(out["release_at"])
            return out

        quiet = {"probe_day": probe_day.isoformat(),
                 "delivered": [_ser(n) for n in raw["delivered"]],
                 "batched": [_ser(n) for n in raw["batched"]],
                 "suppressed": raw["suppressed"]}

    coords = {k: tuple(v) for k, v in (doc.get("coords") or {}).items()}
    origin = doc.get("origin")
    routes = []
    if coords and origin:
        for a in cal["assessments"]:
            try:
                routes.append(route_to_assessment(
                    a, origin, now, coords=coords))
            except ValueError:
                pass  # a location without coords: no route, no fake

    waypoints = doc.get("waypoints") or []
    temple, cues = None, []
    if waypoints:
        items = [{"term": t} for t in list(topics)[:len(waypoints)]]
        temple = build_temple_route(waypoints, items, now)
        cues = audio_cues(temple)

    return {
        "classes": cal["classes"],
        "assessments": cal["assessments"],
        "briefings": briefings,
        "frequency_plan": plan,
        "quiet_hours": quiet,
        "locations": location_records(cal),
        "routes": routes,
        "temple_route": temple,
        "audio_cues": cues,
        "origin": origin,
        "claims_ceiling": LOGISTICS_CEILING,
    }


__all__ = ["location_records", "haversine_minutes",
           "route_to_assessment", "build_temple_route",
           "audio_cues", "apply_voice_customization",
           "surface_calendar_geo", "GEO_RECEIPT_SCHEMA"]
