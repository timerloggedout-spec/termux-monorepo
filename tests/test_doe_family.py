"""DoE family (#1865): structure, intake rule, and record conformance.

Pins: the feed's family members agree with the committed design
records; every committed run record conforms to the family-adopted
EXPERIMENT record schema (docs/ops/corpus/EXPERIMENT.schema.json);
proposal-only campaigns are not admitted and claim no results; the
Delphi executed_comparisons presentation stays Delphi-owned and is
never counted as a DoE campaign result.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "apps" / "help-wanted-dashboard" / "data"
CAMPAIGNS = ROOT / "experiments" / "doe"


def _doe_feed() -> dict:
    return json.loads((DATA / "doe-feed.json").read_text())


def test_family_members_match_design_records():
    feed = _doe_feed()
    fam = feed["data"]["family"]
    assert fam["issue"] == 1865
    member_ids = {m.get("member_id") or m.get("campaign_id")
                  for m in fam["members"]}
    assert "mvt-campaigns" in member_ids
    assert "design-classes" in member_ids
    # Every committed design record is a family campaign member.
    design_ids = set()
    for design_path in CAMPAIGNS.glob("*/DESIGN.json"):
        design = json.loads(design_path.read_text())
        design_ids.add(design["campaign_id"])
    campaign_ids = {c["campaign_id"] for c in feed["data"]["campaigns"]}
    assert campaign_ids == design_ids


def test_intake_rule_pilot2_not_admitted():
    feed = _doe_feed()
    pilot2 = [m for m in feed["data"]["family"]["members"]
              if m.get("issue") == 1850]
    assert pilot2 and pilot2[0]["state"] == "proposal_only_not_admitted"
    assert all(c.get("issue") != 1850 for c in feed["data"]["campaigns"])


def test_campaign_states_agree_with_records_on_disk():
    feed = _doe_feed()
    for camp in feed["data"]["campaigns"]:
        records_dir = ROOT / camp["design_record"].replace(
            "DESIGN.json", "records")
        n = len(list(records_dir.glob("*.json"))) \
            if records_dir.exists() else 0
        assert camp["runs"] == n, camp["campaign_id"]
        assert camp["state"] == ("executed" if n else
                                 "admitted_design_only")
        if n == 0:
            assert camp["results"] is None


def test_run_records_conform_to_experiment_schema():
    schema = json.loads(
        (ROOT / "docs/ops/corpus/EXPERIMENT.schema.json").read_text())
    records = sorted(CAMPAIGNS.glob("*/records/*.json"))
    for rec_path in records:
        rec = json.loads(rec_path.read_text())
        jsonschema.validate(rec, schema)
        assert rec["suite"].startswith("doe-family:")
    # The executed-campaign claim requires at least one real campaign.
    feed = _doe_feed()
    executed = [c for c in feed["data"]["campaigns"]
                if c["state"] == "executed"]
    assert bool(records) == bool(executed)


def test_taxonomy_and_terminology_discipline():
    # DOE-TAXONOMY.md is the family's design-class + terminology record.
    tax = (ROOT / "docs/ops/DOE-TAXONOMY.md").read_text()
    for cls in ("Plackett", "Foldover", "Central composite",
                "Box", "OFAT"):
        assert cls in tax, cls
    assert "multivariate-outcome" in tax.lower()
    # The two senses of "multivariate" are distinguished in the skill.
    skill = (ROOT / ".agents/skills/multivariate-doe/SKILL.md").read_text()
    assert "Multivariate-outcome analysis" in skill
    assert "not an experimental design" in skill  # ANOVA line
    # The feed's design-classes member cites the taxonomy and does not
    # classify the assignment mechanism as a design class.
    feed = _doe_feed()
    dc = [m for m in feed["data"]["family"]["members"]
          if m.get("member_id") == "design-classes"][0]
    assert "DOE-TAXONOMY.md" in dc["note"]
    assert "assignment mechanism" in dc["note"]


def test_executed_arms_carry_accuracy_spread():
    feed = _doe_feed()
    for camp in feed["data"]["campaigns"]:
        if camp["state"] == "executed":
            for arm, a in camp["results"]["arms"].items():
                assert "accuracy_sd" in a, arm


def test_delphi_record_never_counted_as_doe_result():
    feed = _doe_feed()
    ec = feed["data"]["executed_comparisons"]
    assert ec["owner_surface"] == "delphi"
    campaign_ids = {c["campaign_id"] for c in feed["data"]["campaigns"]}
    assert not (campaign_ids & set(ec["candidates"]))
    for camp in feed["data"]["campaigns"]:
        if camp["results"]:
            # DoE results are arm aggregates (routing/representation),
            # never Delphi candidate ids.
            for arm in camp["results"]["arms"]:
                assert "/" in arm, arm
