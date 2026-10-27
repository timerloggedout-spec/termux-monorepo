#!/usr/bin/env python3
"""Oracle Panel feed collector (oracle-panel-feed/v1).

Builds the dashboard Oracle Panel's data feed from the records of
truth — and nothing else:

  - docs/proposals/registry.yaml        (which proposals exist)
  - docs/proposals/active/<id>/         (generation provenance,
                                         UNVERIFIED points, ITEMS.md
                                         work items, briefs, a single
                                         generation's own evidence set)
  - docs/proposals/passes/<pass-id>/    (pass + cycle records,
                                         generation briefs)
  - ops/delphi/panel.json               (the settings every result
                                         was produced under)
  - outcome ledger issue comments       (delphi-generation-ballot /
                                         delphi-generation-calibration
                                         payloads, when fetchable)

Honesty contract (docs/ops/ORACLE-PANEL-FEED.md): the panel must
never show what the record doesn't hold. Ballot classes with no
ballots read as recorded (zero / absent) — never synthesized.
Rehearsals are not registered proposals and never enter the feed;
they are named in `excluded` with their label of record. UNVERIFIED
points and specified_not_run stages are first-class values.

Stdlib only. Auth for the ledger read: GH_TOKEN or GITHUB_TOKEN env,
or --ledger-comments <file> with a pre-fetched comments JSON.
Refresh pattern mirrors scripts/reviewer_metrics/collect.py: the
regenerated feed lands by PR, never by direct commit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "oracle-panel-feed/v1"
BALLOT_MARKER = "<!-- delphi-generation-ballot v1 -->"
CALIBRATION_MARKER = "<!-- delphi-generation-calibration v1 -->"


def parse_registry(text: str) -> list[dict]:
    """Subset reader for registry.yaml's stable shape.

    Captures each proposal's flat scalar fields; nested blocks
    (reviewers) are skipped by indentation. Fails loudly on an entry
    without an id — a registry the collector can't read must stop
    the feed, not produce a partial one presented as complete.
    """
    proposals: list[dict] = []
    current: dict | None = None
    in_proposals = False
    for line in text.splitlines():
        if re.match(r"^proposals:\s*$", line):
            in_proposals = True
            continue
        if in_proposals and re.match(r"^[a-z_]+:", line):
            break
        if not in_proposals:
            continue
        m = re.match(r"^  - ([a-z_]+):\s*(.*?)\s*$", line)
        if m:
            current = {}
            proposals.append(current)
            if m.group(2):
                current[m.group(1)] = m.group(2).strip("\"'")
            continue
        m = re.match(r"^    ([a-z_]+):\s*(.*?)\s*$", line)
        if m and current is not None:
            key, value = m.group(1), m.group(2)
            if value.startswith("["):
                current[key] = [v.strip() for v in
                                value.strip("[]").split(",") if v.strip()]
            elif value:
                current[key] = value.strip("\"'")
    for entry in proposals:
        if not entry.get("id"):
            raise ValueError("registry entry without an id — refusing to build a partial feed")
    return proposals


def registry_updated_at(text: str) -> str | None:
    m = re.search(r"^updated_at:\s*\"?([^\"\n]+)\"?\s*$", text, re.M)
    return m.group(1).strip() if m else None


def _section_bullets(manifest_text: str, heading: str) -> list[str]:
    bullets = []
    in_section = False
    for line in manifest_text.splitlines():
        if line.startswith("## "):
            in_section = heading in line
            continue
        if in_section and line.strip().startswith("- "):
            bullets.append(line.strip()[2:])
    return bullets


def unverified_points(manifest_text: str) -> list[str]:
    return [b.removeprefix("UNVERIFIED:").strip()
            for b in _section_bullets(manifest_text, "Unverified")
            if b.startswith("UNVERIFIED:")]


def summary_bullets(manifest_text: str) -> list[str]:
    """The MANIFEST ## Summary bullets, verbatim (evidence citations
    retained) — the proposal's description as the record wrote it."""
    return _section_bullets(manifest_text, "Summary")


def evidence_basis(prov: dict, evidence_doc: dict | None) -> dict:
    """What the proposal rests on, from the records only.

    The per-set facts (sha256, item count, assembly time) come from
    PROVENANCE. Source/claim-area composition is added only when
    the evidence set itself is in the repo (pass records); for a
    single generation whose set was not committed, those fields
    read null — never reconstructed.
    """
    sets = prov.get("evidence_sets") or []
    basis = {
        "sets": [{"sha256": s.get("sha256"), "items": s.get("items"),
                  "assembled_at": s.get("assembled_at")} for s in sets],
        "items": sum(s.get("items") or 0 for s in sets),
        "sources": None,
        "claim_areas": None,
    }
    if evidence_doc:
        items = evidence_doc.get("items") or []
        sources: dict[str, int] = {}
        areas: dict[str, int] = {}
        for item in items:
            src = (item.get("provenance") or {}).get("source") or "unknown"
            sources[src] = sources.get(src, 0) + 1
            claim = str(item.get("claim") or "")
            area = claim.replace(":", ".").split(".")[0]
            if area:
                areas[area] = areas.get(area, 0) + 1
        basis["sources"] = sources
        basis["claim_areas"] = areas
    return basis


CLASSES = ("HUMAN_COLLABORATOR", "MODEL_PROVIDER", "LOCAL_BASELINE")
PANEL_REF = "ops/delphi/panel.json"
SCORE_SCALE = "1-25 (DECISION-MATRIX Impact x Importance)"
WEIGHT_FORMULA = "w = base * (0.5 + gate_pass_rate) * (elo / 1500)"


def parse_items_md(text: str) -> list[dict]:
    """The ITEMS.md pipe table — the proposal's own work items,
    with states and exit conditions, as the record holds them."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0] in ("ID", ""):
            continue
        if set(cells[0]) <= set("-: "):
            continue
        rows.append({"id": cells[0], "item": cells[1],
                     "state": cells[2], "exit": cells[3]})
    return rows


def brief_points(brief_part: dict | None) -> list[dict] | None:
    """Brief summary points WITH their structured evidence refs —
    the generation brief is the record that carries them."""
    points = (brief_part or {}).get("summary_points") or []
    out = [{"text": p.get("text"),
            "evidence_refs": p.get("evidence_refs") or []}
           for p in points if isinstance(p, dict)]
    return out or None


def ballots_for(ballot: dict, pid: str) -> list[dict] | None:
    """The recorded ballots of a round, verbatim (slim shape).

    A round whose record carries no ballot list (the round-2
    receipt holds per-class aggregates only) reads null — the
    ballots are never reconstructed from aggregates."""
    raw = ballot.get("ballots")
    if not isinstance(raw, list):
        return None
    out = []
    for b in raw:
        scores = b.get("scores") or {}
        out.append({"voter": b.get("voter"),
                    "source_class": b.get("source_class"),
                    "score_of_this": scores.get(pid),
                    "scores": scores})
    return out


def ranking_basis(ballot: dict, candidate_ids: list[str],
                  round_no: int = 1) -> dict | None:
    """Why the ranked outcome is in the order it is — computed
    from the record, with the deciding rule cited from the code.

    cross_vote.rank() sorts by (-score, candidate_id): when the
    deciding class's scores tie, the outcome order is the
    tie-break, NOT a score difference, and the feed says so."""
    per_class = ballot.get("per_class") or {}
    if ballot.get("combined_ranking"):
        return {"scores_tied": None, "score_spread": None,
                "decided_by": "mean of per-class ranks across the "
                              "classes that cast ballots "
                              "(cross_vote.py combined ranking)"}
    present = [c for c, d in per_class.items()
               if isinstance(d, dict) and (d.get("ballots") or 0) > 0]
    if len(present) != 1:
        return None
    cls = present[0]
    scores = per_class[cls].get("scores") or {}
    vals = [scores[c] for c in candidate_ids if c in scores]
    if len(vals) < 2:
        return None
    spread = round(max(vals) - min(vals), 3)
    if spread == 0:
        ranker = ("cross_vote.py rank()" if round_no == 1 else
                  "the round-2 re-vote ranking (method_cycle.py, "
                  "delphi-cross-vote/v1 receipt)")
        return {"scores_tied": True, "score_spread": 0,
                "decided_by": f"scores tied across all candidates in "
                              f"{cls}; the order is the recorded "
                              f"ranked_outcome — {ranker} sorts by "
                              f"(-score, candidate_id), so a tie "
                              f"resolves by candidate id ascending"}
    return {"scores_tied": False, "score_spread": spread,
            "decided_by": f"weighted score order in {cls}"}


def class_producer(cls: str, ballot: dict, round_no: int,
                   evidence_sha: str | None = None) -> dict:
    """Who/what produced a class's result in a round — or, for a
    class that cast nothing, the recorded reason it could not."""
    per = (ballot.get("per_class") or {}).get(cls) or {}
    n = per.get("ballots") or 0
    if n:
        if cls == "LOCAL_BASELINE" and round_no == 1:
            weights = ballot.get("weights") or {}
            voters = [b.get("voter") for b in (ballot.get("ballots") or [])
                      if b.get("source_class") == cls]
            return {"source_class": cls,
                    "kind": "deterministic_rubric_comparator",
                    "producer": "scripts/delphi/cross_vote.py — "
                                "deterministic rubric comparator: one "
                                "ballot per panel role, each scored "
                                "from the candidate's generation "
                                "profile (evidenced ratio, unverified "
                                "count, item shape, evidence-source "
                                "spread, dependency signals)",
                    "voters": voters,
                    "weights": {"source": weights.get("source"),
                                "ledger_issue": 1489,
                                "role_weights": weights.get("role_weights")},
                    "settings": {"panel": PANEL_REF,
                                 "score_scale": SCORE_SCALE,
                                 "formula": WEIGHT_FORMULA}}
        if cls == "LOCAL_BASELINE":
            return {"source_class": cls,
                    "kind": "deterministic_rubric_comparator",
                    "producer": "scripts/delphi/method_cycle.py — "
                                "round-2 re-vote by the same rubric "
                                "comparator over the equalized "
                                "per-proposal test-results evidence set",
                    "ballots": n,
                    "evidence_set_sha256": evidence_sha,
                    "settings": {"panel": PANEL_REF,
                                 "score_scale": SCORE_SCALE}}
        return {"source_class": cls, "kind": "recorded_ballots",
                "ballots": n,
                "producer": "recorded ballot files supplied to "
                            "cross_vote.py (voter identity and, for "
                            "MODEL_PROVIDER, the full run record are "
                            "carried on each ballot)"}
    reasons = {
        "MODEL_PROVIDER": "model voting disabled (DELPHI_LLM_MAX=0); "
                          "a MODEL_PROVIDER ballot is admissible only "
                          "with a full run record (provider, model, "
                          "run_id, response_hash) and an entitlement "
                          "basis — cross_vote.py validate_ballots. "
                          "None recorded.",
        "HUMAN_COLLABORATOR": "no recorded human ballot file was "
                              "supplied to the cross-vote; none "
                              "recorded.",
    }
    return {"source_class": cls, "kind": "none_recorded", "ballots": 0,
            "reason": reasons.get(cls, "no ballots recorded")}


def ledger_payloads(comments: list[dict]) -> dict[str, dict]:
    """pass_id -> {ballot: payload, ballot_comment_id, calibration...}"""
    out: dict[str, dict] = {}
    for comment in comments:
        body = comment.get("body") or ""
        for marker, key in ((BALLOT_MARKER, "ballot"),
                            (CALIBRATION_MARKER, "calibration_feed")):
            if marker in body:
                m = re.search(r"```json\s*(\{.*?\})\s*```", body, re.S)
                if not m:
                    continue
                payload = json.loads(m.group(1))
                pass_id = payload.get("pass_id")
                if pass_id:
                    slot = out.setdefault(pass_id, {})
                    slot[key] = payload
                    slot[f"{key}_comment_id"] = comment.get("id")
    return out


def fetch_ledger_comments(repo: str, issue: int, token: str) -> list[dict]:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues/{issue}/comments?per_page=100",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def build_feed(registry_text: str, active_dir: Path, passes_dir: Path,
               ledger: dict[str, dict], ledger_verified: bool,
               generated_at: str, panel: dict | None = None) -> dict:
    entries = parse_registry(registry_text)
    oracle_entries = [e for e in entries if e.get("author") == "oracle-method"]

    passes: dict[str, dict] = {}
    if passes_dir.is_dir():
        for pass_dir in sorted(passes_dir.iterdir()):
            meta_file = pass_dir / "pass.json"
            if not meta_file.exists():
                continue
            meta = json.loads(meta_file.read_text())
            cycle_dir = pass_dir / "cycle"
            cycle = {}
            for name in ("BALLOT-round1.json", "BALLOT-round2.json",
                         "CALIBRATION.json", "CYCLE.json",
                         "EXPECTATIONS.json", "IMPLEMENTATION.json"):
                f = cycle_dir / name
                if f.exists():
                    cycle[name] = json.loads(f.read_text())
            impl = {}
            impl_dir = pass_dir / "implementation"
            if impl_dir.is_dir():
                for f in impl_dir.glob("*.json"):
                    impl[f.stem] = json.loads(f.read_text())
            evidence_doc = None
            if (pass_dir / "evidence.json").exists():
                evidence_doc = json.loads(
                    (pass_dir / "evidence.json").read_text())
            brief_doc = None
            if (pass_dir / "brief.json").exists():
                brief_doc = json.loads((pass_dir / "brief.json").read_text())
            pass_exp = None
            if (pass_dir / "expectations.json").exists():
                pass_exp = json.loads(
                    (pass_dir / "expectations.json").read_text())
            passes[meta["pass_id"]] = {"meta": meta, "cycle": cycle,
                                       "impl": impl, "evidence": evidence_doc,
                                       "brief": brief_doc,
                                       "pass_expectations": pass_exp,
                                       "dir": pass_dir}

    proposals = []
    for entry in oracle_entries:
        pid = entry["id"]
        pdir = active_dir / pid
        prov = {}
        if (pdir / "PROVENANCE.json").exists():
            prov = json.loads((pdir / "PROVENANCE.json").read_text())
        unverified = []
        description = []
        if (pdir / "MANIFEST.md").exists():
            manifest_text = (pdir / "MANIFEST.md").read_text()
            unverified = unverified_points(manifest_text)
            description = summary_bullets(manifest_text)
        work_items = []
        if (pdir / "ITEMS.md").exists():
            work_items = parse_items_md((pdir / "ITEMS.md").read_text())
        documents = {name: f"docs/proposals/active/{pid}/{fname}"
                     for name, fname in (("rfp", "RFP.md"),
                                         ("items", "ITEMS.md"),
                                         ("manifest", "MANIFEST.md"),
                                         ("provenance", "PROVENANCE.json"))
                     if (pdir / fname).exists()}
        own_brief = None
        if (pdir / "brief.json").exists():
            own_brief = json.loads((pdir / "brief.json").read_text())
        pass_id = prov.get("pass_id")
        item = {
            "id": pid,
            "title": entry.get("title"),
            "author": entry.get("author"),
            "status": entry.get("status"),
            "priority": entry.get("priority"),
            "path": entry.get("path"),
            "pass": pass_id,
            "kind": "pass-candidate" if pass_id else "single",
            "generated_at": prov.get("generated_at"),
            "generator": prov.get("generator"),
            "evidence_items": sum(s.get("items", 0)
                                  for s in prov.get("evidence_sets", [])),
            "description": description or None,
            "approach": None,
            "summary_points": None,
            "work_items": work_items or None,
            "documents": documents or None,
            "evidence_profile": None,
            "producers": None,
            "evidence_basis": None,
            "implementation_summary": None,
            "unverified_points": unverified,
            "rounds": None,
            "expectations": None,
            "implementation": None,
            "calibration": None,
            "specified_not_run": [],
            "ledger": None,
            "live": True,
        }
        if prov.get("evidence_sets"):
            doc = (passes.get(pass_id) or {}).get("evidence") if pass_id else None
            if doc is None and (pdir / "evidence.json").exists():
                # A single generation's own committed evidence set:
                # same claim/provenance shape as a pass evidence doc.
                doc = json.loads((pdir / "evidence.json").read_text())
            item["evidence_basis"] = evidence_basis(prov, doc)
        if own_brief:
            item["approach"] = {
                "executive_request": own_brief.get("executive_request"),
                "surface": own_brief.get("surface"),
                "deadline": own_brief.get("deadline"),
                "source": f"docs/proposals/active/{pid}/brief.json",
            }
            item["summary_points"] = brief_points(own_brief)
        if prov:
            item["producers"] = {"generation": {
                "kind": "oracle_method_generator",
                "producer": prov.get("generator"),
                "generated_at": prov.get("generated_at"),
                "evidence_sets": prov.get("evidence_sets") or [],
            }}
        if pass_id and pass_id in passes:
            cyc = passes[pass_id]["cycle"]
            impl_stage = (cyc.get("IMPLEMENTATION.json") or {}).get(pid) or {}
            impl_suites = (passes[pass_id]["impl"].get(pid) or {}).get("suites") or []
            raw_profiles = (cyc.get("BALLOT-round1.json") or {}).get("profiles")
            if isinstance(raw_profiles, list):
                profiles = {(p.get("candidate") or p.get("id")): p
                            for p in raw_profiles if isinstance(p, dict)}
            elif isinstance(raw_profiles, dict):
                profiles = raw_profiles
            else:
                profiles = {}
            profile = profiles.get(pid) or {}
            if profile:
                item["evidence_profile"] = profile
            pdata = passes[pass_id]
            variant = None
            for v in (pdata.get("brief") or {}).get("variants") or []:
                suf = v.get("suffix")
                if suf and pid.endswith(suf):
                    variant = v
                    break
            if variant:
                item["approach"] = {
                    "executive_request": variant.get("executive_request"),
                    "concept": variant.get("concept"),
                    "planned_suites": variant.get("test_suites"),
                    "source": f"docs/proposals/passes/{pass_id}/brief.json",
                }
                item["summary_points"] = brief_points(variant)
            candidate_ids = [c.get("id")
                             for c in pdata["meta"].get("candidates", [])]
            if impl_stage or impl_suites:
                item["implementation_summary"] = {
                    "suites": [s.get("name") for s in impl_suites],
                    "pass_rate": impl_stage.get("pass_rate"),
                    "evidenced_ratio": profile.get("evidenced_ratio"),
                    "all_suites_passed": bool(impl_suites) and all(
                        (s.get("failed") or 0) == 0 for s in impl_suites),
                }
            r1 = cyc.get("BALLOT-round1.json") or {}
            r2 = cyc.get("BALLOT-round2.json") or {}
            def scores(ballot: dict) -> dict:
                return {cls: (data.get("scores") or {}).get(pid)
                        for cls, data in (ballot.get("per_class") or {}).items()}
            item["rounds"] = {
                "round_1": {"ranking": r1.get("ranked_outcome"),
                            "rank_of_this": (r1.get("ranked_outcome") or []).index(pid) + 1
                            if pid in (r1.get("ranked_outcome") or []) else None,
                            "ballots_by_class": r1.get("ballots_by_class"),
                            "scores_by_class": scores(r1),
                            "classes_absent": r1.get("classes_absent"),
                            "ballots": ballots_for(r1, pid),
                            "ranking_basis": ranking_basis(r1, candidate_ids, 1)},
                "round_2": {"ranking": r2.get("ranked_outcome"),
                            "rank_of_this": (r2.get("ranked_outcome") or []).index(pid) + 1
                            if pid in (r2.get("ranked_outcome") or []) else None,
                            "ballots_by_class": r2.get("ballots_by_class"),
                            "scores_by_class": scores(r2),
                            "evidence_set_sha256": r2.get("evidence_set_sha256"),
                            "ballots": ballots_for(r2, pid),
                            "ranking_basis": ranking_basis(r2, candidate_ids, 2)},
            }
            exp_doc = cyc.get("EXPECTATIONS.json") or {}
            priors = exp_doc.get("expectations") or {}
            item["expectations"] = {
                source: per[pid] for source, per in priors.items()
                if isinstance(per, dict) and pid in per} or None
            item["expectations_recorded_before_implementation"] = bool(
                exp_doc.get("recorded_before_implementation"))
            impl = passes[pass_id]["impl"].get(pid)
            if impl:
                suites = impl.get("suites") or []
                item["implementation"] = {
                    "suites": [{"suite": s.get("name"),
                                "passed": s.get("passed"),
                                "failed": s.get("failed")} for s in suites],
                    "passed": sum(s.get("passed") or 0 for s in suites),
                    "failed": sum(s.get("failed") or 0 for s in suites),
                    "suites_total": len(suites),
                    "suites_passed": sum(
                        1 for s in suites
                        if (s.get("failed") or 0) == 0
                        and (s.get("passed") or 0) > 0)}
            cal = (cyc.get("CALIBRATION.json") or {}).get("candidates") or {}
            item["calibration"] = {
                source: {"rank_delta": per[pid]["rank_delta"],
                         "score_delta": per[pid]["score_delta"],
                         "within_tolerance": per[pid]["within_tolerance"],
                         "moved_on_evidence": per[pid]["moved_on_evidence"]}
                for source, per in cal.items() if isinstance(per, dict) and pid in per
            } or None
            exp_sources = []
            exp_basis = (cyc.get("EXPECTATIONS.json") or {}).get("basis")
            pass_exp = pdata.get("pass_expectations") or {}
            for source in (item["expectations"] or {}):
                if source.startswith("BRIEF:"):
                    exp_sources.append({"source": source,
                                        "kind": "brief_prior",
                                        "author": pass_exp.get("author")})
                else:
                    exp_sources.append({"source": source,
                                        "kind": "derived_from_round_1",
                                        "basis": exp_basis})
            producers = dict(item["producers"] or {})
            producers["rounds"] = {
                "round_1": {cls: class_producer(cls, r1, 1)
                            for cls in CLASSES},
                "round_2": {cls: class_producer(
                    cls, r2, 2, r2.get("evidence_set_sha256"))
                    for cls in CLASSES},
            }
            producers["expectations_sources"] = exp_sources or None
            item["producers"] = producers
            stages = (cyc.get("CYCLE.json") or {}).get("stages") or []
            item["specified_not_run"] = [
                {"item": s["stage"], "reason": s.get("detail")}
                for s in stages if s.get("status") == "specified_not_run"]
            led = ledger.get(pass_id) or {}
            ballot = led.get("ballot") or {}
            for name, reason in (ballot.get("specified_not_run") or {}).items():
                item["specified_not_run"].append({"item": name, "reason": reason})
            if led:
                item["ledger"] = {
                    "ballot_comment_id": led.get("ballot_comment_id"),
                    "calibration_comment_id": led.get("calibration_feed_comment_id"),
                    "verified": ledger_verified,
                }
        proposals.append(item)

    pass_summaries = []
    for pass_id, data in passes.items():
        r1 = data["cycle"].get("BALLOT-round1.json") or {}
        raw_n = data["meta"].get("n")
        if isinstance(raw_n, dict):
            n_val = raw_n.get("value")
            n_val = n_val if isinstance(n_val, int) else None
        elif isinstance(raw_n, int):
            n_val = raw_n
        else:
            n_val = None
        pass_summaries.append({
            "pass_id": pass_id,
            # A stated record carries its status verbatim (e.g.
            # stated_not_run); a generator pass record has none and
            # reads "recorded". The panel must never present a
            # stated pass as a run one.
            "status": data["meta"].get("status") or "recorded",
            "n": n_val,
            "candidates": [c["id"] if isinstance(c, dict) else c
                           for c in data["meta"].get("candidates", [])],
            "ranked_outcome": r1.get("ranked_outcome"),
            "record": f"docs/proposals/passes/{pass_id}/",
        })

    settings = None
    if panel:
        gen = panel.get("generation") or {}
        cyc_cfg = gen.get("cycle") or {}
        settings = {
            "panel": PANEL_REF,
            "formula": panel.get("formula"),
            "criteria": panel.get("criteria"),
            "score_scale": SCORE_SCALE,
            "weights_source": (gen.get("cross_vote") or {}).get("weights_source"),
            "seed_note": panel.get("seed_note"),
            "generation": {
                "proposals_per_pass": gen.get("proposals_per_pass"),
                "cycle_rounds": cyc_cfg.get("rounds"),
                "expectation_tolerance": cyc_cfg.get("expectation_tolerance"),
            },
        }

    return {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "generator": "scripts/delphi/oracle_panel_feed.py",
        "sources": {
            "registry": "docs/proposals/registry.yaml",
            "registry_updated_at": registry_updated_at(registry_text),
            "registry_proposals_total": len(entries),
            "oracle_method_proposals": len(oracle_entries),
            "ledger_issue": 1487,
            "ledger_verified": ledger_verified,
        },
        "settings": settings,
        "honesty_rules": [
            "Show only what the record holds: a value absent from the "
            "registry, pass records, or ledger payloads is shown as "
            "absent/null, never synthesized.",
            "Ballot classes with no ballots read as recorded "
            "(0 / listed in classes_absent) — never as implied support.",
            "UNVERIFIED points and specified_not_run stages are "
            "first-class statuses: render them, never hide them.",
            "Rehearsals are ideation drafts imagining readiness "
            "(synthetic fixtures, no real ballots, not registered) "
            "and are excluded from results.",
            "Every score states its producer (producers block): the "
            "producing class, tool, voters and weight settings. Tied "
            "scores render as tied, with the ranking basis stated — "
            "an order produced by the cross_vote.py rank() "
            "tie-break is never rendered as a score difference.",
        ],
        "proposals": proposals,
        "passes": pass_summaries,
        "excluded": [{
            "what": "Oracle Method rehearsals on synthetic fixtures",
            "label": "ideation drafts imagining readiness",
            "reason": "not registered proposals; no real ballots; "
                      "never shown as results",
        }],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Oracle Panel feed collector")
    parser.add_argument("--repo", default="timerloggedout-spec/termux-monorepo")
    parser.add_argument("--root", default=".",
                        help="repo checkout root (registry/passes/active read from here)")
    parser.add_argument("--ledger-issue", type=int, default=1487)
    parser.add_argument("--ledger-comments",
                        help="pre-fetched ledger comments JSON (else fetch via GH_TOKEN)")
    parser.add_argument("--no-ledger", action="store_true",
                        help="skip the ledger read (feed marks ledger_verified false)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    root = Path(args.root)
    registry_text = (root / "docs/proposals/registry.yaml").read_text()

    ledger: dict[str, dict] = {}
    verified = False
    if args.ledger_comments:
        comments = json.loads(Path(args.ledger_comments).read_text())
        ledger = ledger_payloads(comments)
        verified = True
    elif not args.no_ledger:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            comments = fetch_ledger_comments(args.repo, args.ledger_issue, token)
            ledger = ledger_payloads(comments)
            verified = True
        else:
            print("no token and no --ledger-comments: ledger read skipped",
                  file=sys.stderr)

    panel = None
    panel_file = root / PANEL_REF
    if panel_file.exists():
        panel = json.loads(panel_file.read_text())

    feed = build_feed(registry_text,
                      root / "docs/proposals/active",
                      root / "docs/proposals/passes",
                      ledger, verified,
                      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                      panel=panel)
    Path(args.out).write_text(json.dumps(feed, indent=2) + "\n")
    print(f"oracle-panel-feed: {len(feed['proposals'])} proposals, "
          f"{len(feed['passes'])} passes, ledger_verified={verified}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
