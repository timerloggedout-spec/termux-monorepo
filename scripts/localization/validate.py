#!/usr/bin/env python3
"""Validate PolyGlot locale catalogs, mappings, provider DOE, and provenance."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
BCP47_SHAPE = re.compile(r"^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$")
SCHEMAS = (
    "localization/schemas/locale-registry.schema.json",
    "localization/schemas/source-mapping.schema.json",
    "localization/schemas/translation-manifest.schema.json",
    "localization/schemas/experiment-record.schema.json",
    "localization/schemas/feedback.schema.json",
)


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def git_blob_hash(path: Path) -> str:
    data = path.read_bytes()
    header = b"blob " + str(len(data)).encode("ascii") + bytes([0])
    return hashlib.sha1(header + data).hexdigest()


def validate_instance(instance, schema, label: str, errors: list[str]) -> None:
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for error in sorted(
        validator.iter_errors(instance),
        key=lambda item: tuple(str(part) for part in item.absolute_path),
    ):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{label}: schema violation at {location}: {error.message}")


def validate() -> list[str]:
    errors: list[str] = []
    schema_data = {}
    for schema_path in SCHEMAS:
        try:
            schema = read(schema_path)
            jsonschema.Draft202012Validator.check_schema(schema)
            schema_data[schema_path] = schema
        except FileNotFoundError:
            errors.append(f"missing localization schema: {schema_path}")
        except jsonschema.SchemaError as exc:
            errors.append(f"invalid localization schema {schema_path}: {exc.message}")

    locales = read("localization/registry/locales.json")
    mapping = read("localization/mappings/teammate-portal.json")
    docs_mapping = read("localization/mappings/repository-docs.json")
    manifest = read("localization/manifests/teammate-portal.json")

    data_schema_pairs = (
        (locales, "localization/schemas/locale-registry.schema.json", "localization/registry/locales.json"),
        (mapping, "localization/schemas/source-mapping.schema.json", "localization/mappings/teammate-portal.json"),
        (docs_mapping, "localization/schemas/source-mapping.schema.json", "localization/mappings/repository-docs.json"),
        (manifest, "localization/schemas/translation-manifest.schema.json", "localization/manifests/teammate-portal.json"),
    )
    for instance, schema_path, label in data_schema_pairs:
        schema = schema_data.get(schema_path)
        if schema is not None:
            validate_instance(instance, schema, label, errors)

    by_id = {item["id"]: item for item in locales["locales"]}
    source_locale = locales["source_locale"]
    if source_locale not in by_id:
        errors.append("source_locale must resolve in locale registry")
    for item in by_id.values():
        language_tag = item["language_tag"]
        if not BCP47_SHAPE.fullmatch(language_tag):
            errors.append(f"{item['id']}: invalid language_tag shape {language_tag!r}")
        if item["direction"] not in {"ltr", "rtl"}:
            errors.append(f"{item['id']}: invalid direction")
        if item["fallback"] is not None and item["fallback"] not in by_id:
            errors.append(f"{item['id']}: unknown fallback {item['fallback']}")

    catalogs: dict[str, dict] = {}
    for locale in by_id:
        path = f"localization/catalogs/teammate-portal/{locale}.json"
        try:
            catalogs[locale] = read(path)
        except FileNotFoundError:
            if by_id[locale]["status"] in {"source", "priority", "active"}:
                errors.append(f"missing active catalog: {path}")

    source_keys = set(catalogs.get(source_locale, {}).get("messages", {}))
    for locale, catalog in catalogs.items():
        for key in source_keys - set(catalog.get("messages", {})):
            errors.append(f"{locale}: missing message key {key}")

    mapped_keys: set[str] = set()
    for entry in mapping["entries"]:
        key = entry["message_key"]
        mapped_keys.add(key)
        if key not in source_keys:
            errors.append(f"mapping {entry['source_id']}: unknown message key {key}")
        for catalog_path in entry.get("catalogs", []):
            if not (ROOT / catalog_path).is_file():
                errors.append(f"mapping {entry['source_id']}: missing catalog {catalog_path}")
        if entry.get("locale") not in by_id:
            errors.append(f"mapping {entry['source_id']}: unknown locale {entry.get('locale')}")
        if entry.get("fallback") not in by_id:
            errors.append(f"mapping {entry['source_id']}: unknown fallback {entry.get('fallback')}")
    for key in sorted(source_keys - mapped_keys):
        errors.append(f"source message missing mapping: {key}")

    for entry in docs_mapping["entries"]:
        if entry["locale"] not in by_id:
            errors.append(f"docs mapping {entry['source_id']}: unknown locale")
        if entry["fallback"] not in by_id:
            errors.append(f"docs mapping {entry['source_id']}: unknown fallback")
        if not (ROOT / entry["source_path"]).is_file():
            errors.append(f"docs mapping {entry['source_id']}: missing source {entry['source_path']}")
        if entry["state"] in {"approved", "published"} and not (ROOT / entry["target_path"]).is_file():
            errors.append(f"docs mapping {entry['source_id']}: approved target missing")

    source_catalog = f"localization/catalogs/teammate-portal/{source_locale}.json"
    source_path = ROOT / source_catalog
    actual_source_hash = None
    if source_path.is_file():
        actual_source_hash = f"git-blob:{git_blob_hash(source_path)}"
        recorded_revision = manifest.get("source_revision")
        if recorded_revision and recorded_revision != actual_source_hash:
            errors.append(
                f"manifest: source_revision mismatch; expected {actual_source_hash}, found {recorded_revision}"
            )
    else:
        errors.append(f"manifest: source catalog missing: {source_catalog}")

    for translation in manifest["translations"]:
        locale = translation["locale"]
        if locale not in by_id:
            errors.append(f"manifest: unknown locale {locale}")
        catalog_path = ROOT / translation["catalog"]
        if not catalog_path.is_file():
            errors.append(f"manifest: missing translation catalog {translation['catalog']}")
        if translation.get("source_catalog") and not (ROOT / translation["source_catalog"]).is_file():
            errors.append(f"manifest: missing source catalog {translation['source_catalog']}")
        freshness = translation["freshness"]
        recorded_hash = freshness["source_hash"]
        is_fresh = actual_source_hash is not None and recorded_hash == actual_source_hash
        if freshness["state"] == "fresh" and not is_fresh:
            errors.append(
                f"manifest: translation {locale} source hash mismatch; "
                f"expected {actual_source_hash}, found {recorded_hash}"
            )
        if freshness["state"] == "stale" and is_fresh:
            errors.append(f"manifest: translation {locale} is marked stale while its source hash is current")
        approved = translation["review"]["status"] == "approved"
        freshness_is_current = freshness["state"] == "fresh" and is_fresh
        if approved and not freshness_is_current:
            errors.append(f"manifest: approved translation {locale} requires a fresh state and current source hash")
        if translation["publication"] in {"approved", "published"} and not (approved and freshness_is_current):
            errors.append(f"manifest: translation {locale} publication requires approval and a current source hash")

    providers = read("localization/providers/registry.json")
    provider_ids = {provider["id"] for provider in providers["providers"]}
    doe = read("localization/doe/urdu-portal-v1/DESIGN.json")
    for provider_id in doe["factors"]["provider"]:
        if provider_id not in provider_ids:
            errors.append(f"DOE references unregistered provider: {provider_id}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: locale registry, catalogs, mappings, manifests, provider DOE, schemas, and source freshness are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
