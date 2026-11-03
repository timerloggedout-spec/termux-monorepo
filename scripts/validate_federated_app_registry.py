#!/usr/bin/env python3
"""Deterministic validation for the federated application registry (stdlib only)."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/ops/federated-app-registry.json"
SCHEMA = ROOT / "docs/ops/federated-app-registry.schema.json"
KEY = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
REPO = re.compile(r"^[^/]+/[^/]+$")
URI = re.compile(r"^https://[^\s]+$")

def validate(data: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    for field in ("registry_version", "authority_note"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"{field} must be a non-empty string")
    for field in ("applications", "automation_identities"):
        if not isinstance(data.get(field), list):
            errors.append(f"{field} must be an array")
    if errors:
        return errors

    app_keys: set[str] = set()
    product_ids: set[str] = set()
    lane_ids: set[str] = set()
    for i, app in enumerate(data["applications"]):
        where = f"applications[{i}]"
        if not isinstance(app, dict):
            errors.append(f"{where} must be an object")
            continue
        key = app.get("app_key")
        if not isinstance(key, str) or not KEY.fullmatch(key):
            errors.append(f"{where}.app_key is invalid")
        elif key in app_keys:
            errors.append(f"duplicate app_key: {key}")
        else:
            app_keys.add(key)
        if app.get("identity_domain") != "product-application":
            errors.append(f"{where}.identity_domain must be product-application")
        product_id = app.get("product_app_id")
        if product_id is not None:
            if not isinstance(product_id, str) or not product_id.strip():
                errors.append(f"{where}.product_app_id must be null or non-empty")
            elif product_id in product_ids:
                errors.append(f"duplicate product_app_id: {product_id}")
            else:
                product_ids.add(product_id)
        repo = app.get("repository")
        if not isinstance(repo, dict):
            errors.append(f"{where}.repository must be an object")
        elif repo.get("full_name") is not None and (
            not isinstance(repo["full_name"], str) or not REPO.fullmatch(repo["full_name"])
        ):
            errors.append(f"{where}.repository.full_name must be owner/repository or null")
        for j, lane in enumerate(app.get("release_lanes", [])):
            lane_where = f"{where}.release_lanes[{j}]"
            if not isinstance(lane, dict):
                errors.append(f"{lane_where} must be an object")
                continue
            lane_id = lane.get("lane_id")
            if not isinstance(lane_id, str) or not KEY.fullmatch(lane_id):
                errors.append(f"{lane_where}.lane_id is invalid")
            elif lane_id in lane_ids:
                errors.append(f"duplicate release lane id: {lane_id}")
            else:
                lane_ids.add(lane_id)
            if lane.get("status") == "released" and not lane.get("evidence_refs"):
                errors.append(f"{lane_where}: released lane requires evidence_refs")
            if lane.get("status") == "released" and not lane.get("version_authority"):
                errors.append(f"{lane_where}: released lane requires version_authority")
            for ref in lane.get("evidence_refs", []):
                if not isinstance(ref, str) or not URI.fullmatch(ref):
                    errors.append(f"{lane_where}: evidence reference must be an https URI")
        for ref in app.get("evidence_refs", []):
            if not isinstance(ref, str) or not URI.fullmatch(ref):
                errors.append(f"{where}: evidence reference must be an https URI")

    automation_keys: set[str] = set()
    automation_ids: set[tuple[str, int]] = set()
    for i, identity in enumerate(data["automation_identities"]):
        where = f"automation_identities[{i}]"
        if not isinstance(identity, dict):
            errors.append(f"{where} must be an object")
            continue
        key, platform, numeric_id = identity.get("identity_key"), identity.get("platform"), identity.get("numeric_id")
        if not isinstance(key, str) or not key:
            errors.append(f"{where}.identity_key is required")
        elif key in automation_keys:
            errors.append(f"duplicate automation identity key: {key}")
        else:
            automation_keys.add(key)
        if platform not in {"github-app", "gitlab-app", "other"}:
            errors.append(f"{where}.platform is invalid")
        if numeric_id is not None:
            if type(numeric_id) is not int or numeric_id < 1:
                errors.append(f"{where}.numeric_id must be a positive integer or null")
            else:
                pair = (platform, numeric_id)
                if pair in automation_ids:
                    errors.append(f"duplicate automation numeric id: {pair}")
                automation_ids.add(pair)
        for ref in identity.get("evidence_refs", []):
            if not isinstance(ref, str) or not URI.fullmatch(ref):
                errors.append(f"{where}: evidence reference must be an https URI")
    return errors

def main() -> int:
    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"registry load failed: {exc}", file=sys.stderr)
        return 2
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        print("unexpected JSON Schema dialect", file=sys.stderr)
        return 2
    try:
        import jsonschema
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(instance=data, schema=schema)
    except ImportError:
        print("jsonschema dependency is required for schema validation", file=sys.stderr)
        return 2
    except jsonschema.ValidationError as exc:
        print(f"JSON Schema validation failed: {exc.message}", file=sys.stderr)
        return 1
    except jsonschema.SchemaError as exc:
        print(f"JSON Schema is invalid: {exc.message}", file=sys.stderr)
        return 2
    errors = validate(data, schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    lanes = sum(len(app.get("release_lanes", [])) for app in data["applications"])
    print(f"Federated app registry valid: {len(data['applications'])} applications, "
          f"{len(data['automation_identities'])} automation identities, {lanes} release lanes")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
