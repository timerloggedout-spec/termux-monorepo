"""RFP admission and lane-composition contracts: schema and guardrail proof."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")
ROOT = Path(__file__).resolve().parents[1]
RFP = ROOT / "docs/ops/rfp"


def load(name):
    return json.loads((RFP / name).read_text())


def validate(schema, record):
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())


def test_competitor_admission_example_conforms():
    validate(load("COMPETITOR-ADMISSION.schema.json"),
             load_example("competitor-rfp-v13.json"))


def test_competitor_admission_requires_provenance_identity_and_owner():
    schema = load("COMPETITOR-ADMISSION.schema.json")
    record = load_example("competitor-rfp-v13.json")
    for key in ("source", "identity", "owner"):
        broken = copy.deepcopy(record)
        broken.pop(key)
        with pytest.raises(jsonschema.ValidationError):
            validate(schema, broken)


def test_admission_does_not_grant_production_authority():
    schema = load("COMPETITOR-ADMISSION.schema.json")
    record = load_example("competitor-rfp-v13.json")
    record["admission"]["production_authority"] = True
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)


def test_executing_candidate_requires_campaign_id():
    schema = load("COMPETITOR-ADMISSION.schema.json")
    record = load_example("competitor-rfp-v13.json")
    record["lifecycle"]["state"] = "executing"
    record["admission"]["decision"] = "experiment_admitted"
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)


def test_lane_composition_example_conforms():
    validate(load("LANE-COMPOSITION.schema.json"),
             load_example("lane-composition-parallel.json"))


def test_composition_requires_two_lanes_and_explicit_gates():
    schema = load("LANE-COMPOSITION.schema.json")
    record = load_example("lane-composition-parallel.json")
    record["lanes"] = record["lanes"][:1]
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)
    record = load_example("lane-composition-parallel.json")
    del record["compatibility"]["license_review"]
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)


def test_composition_cannot_authorize_production_routing():
    schema = load("LANE-COMPOSITION.schema.json")
    record = load_example("lane-composition-parallel.json")
    record["governance"]["production_routing_authorized"] = True
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)


def load_example(name):
    return json.loads((RFP / "examples" / name).read_text())


def test_advanced_composition_requires_passed_gates():
    schema = load("LANE-COMPOSITION.schema.json")
    record = load_example("lane-composition-parallel.json")
    record["governance"]["state"] = "admitted_design_only"
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)
    for key in ("schema_compatibility", "provenance_preservation",
                "security_review", "license_review", "capacity_review",
                "failure_semantics"):
        record["compatibility"][key] = "pass"
    record["compatibility"]["human_approval"] = "not_required"
    validate(schema, record)


def test_executing_composition_requires_campaign_id():
    schema = load("LANE-COMPOSITION.schema.json")
    record = load_example("lane-composition-parallel.json")
    record["governance"]["state"] = "executing"
    for key in ("schema_compatibility", "provenance_preservation",
                "security_review", "license_review", "capacity_review",
                "failure_semantics"):
        record["compatibility"][key] = "pass"
    record["compatibility"]["human_approval"] = "not_required"
    record["design"]["campaign_id"] = ""
    with pytest.raises(jsonschema.ValidationError):
        validate(schema, record)
