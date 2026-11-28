#!/usr/bin/env python3
"""Validate PolyGlot locale catalogs, mappings, provider DOE, and provenance."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = (
    "localization/schemas/locale-registry.schema.json",
    "localization/schemas/source-mapping.schema.json",
    "localization/schemas/translation-manifest.schema.json",
    "localization/schemas/experiment-record.schema.json",
    "localization/schemas/feedback.schema.json",
)


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    locales = read("localization/registry/locales.json")
    by_id = {item["id"]: item for item in locales["locales"]}
    source_locale = locales["source_locale"]
    if source_locale not in by_id:
        errors.append("source_locale must resolve in locale registry")
    for item in by_id.values():
        if item["language_tag"] != item["id"] and not item["language_tag"].startswith(item["id"] + "-"):
            errors.append(f"{item['id']}: language_tag must match locale id")
        if item["direction"] not in {"ltr", "rtl"}:
            errors.append(f"{item['id']}: invalid direction")
        if item["fallback"] is not None and item["fallback"] not in by_id:
            errors.append(f"{item['id']}: unknown fallback {item['fallback']}")

    mapping = read("localization/mappings/teammate-portal.json")
    manifest = read("localization/manifests/teammate-portal.json")
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
        for path in entry["catalogs"]:
            if not (ROOT / path).is_file():
                errors.append(f"mapping {entry['source_id']}: missing catalog {path}")
    for key in sorted(source_keys - mapped_keys):
        errors.append(f"source message missing mapping: {key}")

    docs_mapping = read("localization/mappings/repository-docs.json")
    for entry in docs_mapping["entries"]:
        if entry["locale"] not in by_id:
            errors.append(f"docs mapping {entry['source_id']}: unknown locale")
        if entry["fallback"] not in by_id:
            errors.append(f"docs mapping {entry['source_id']}: unknown fallback")
        if not (ROOT / entry["source_path"]).is_file():
            errors.append(f"docs mapping {entry['source_id']}: missing source {entry['source_path']}")
        if entry["state"] in {"approved", "published"} and not (ROOT / entry["target_path"]).is_file():
            errors.append(f"docs mapping {entry['source_id']}: approved target missing")

    for translation in manifest["translations"]:
        locale = translation["locale"]
        if locale not in by_id:
            errors.append(f"manifest: unknown locale {locale}")
        if translation["catalog"] not in [f"localization/catalogs/teammate-portal/{key}.json" for key in catalogs]:
            errors.append(f"manifest: unknown catalog {translation['catalog']}")
        if translation["review"]["status"] == "approved" and translation["freshness"]["state"] != "fresh":
            errors.append(f"manifest: approved translation {locale} requires fresh source hash")
        if translation["publication"] == "published" and translation["review"]["status"] != "approved":
            errors.append(f"manifest: published translation {locale} requires approval")

    providers = read("localization/providers/registry.json")
    provider_ids = {provider["id"] for provider in providers["providers"]}
    doe = read("localization/doe/urdu-portal-v1/DESIGN.json")
    for provider_id in doe["factors"]["provider"]:
        if provider_id not in provider_ids:
            errors.append(f"DOE references unregistered provider: {provider_id}")

    for schema in SCHEMAS:
        try:
            read(schema)
        except FileNotFoundError:
            errors.append(f"missing localization schema: {schema}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: locale registry, catalogs, source mappings, docs mappings, providers, DOE, and schemas are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
