#!/usr/bin/env python3
"""Validate PolyGlot locale catalogs, mappings, and translation provenance."""
from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def validate() -> list[str]:
    errors = []
    locales = read("localization/registry/locales.json")
    by_id = {item["id"]: item for item in locales["locales"]}
    if locales["source_locale"] not in by_id:
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
    catalogs = {}
    for locale in by_id:
        path = f"localization/catalogs/teammate-portal/{locale}.json"
        try:
            catalogs[locale] = read(path)
        except FileNotFoundError:
            if locale == locales["source_locale"]:
                errors.append(f"missing source catalog: {path}")
    source_keys = set(catalogs.get(locales["source_locale"], {}).get("messages", {}))
    for locale, catalog in catalogs.items():
        for key in source_keys - set(catalog.get("messages", {})):
            errors.append(f"{locale}: missing message key {key}")
    for entry in mapping["entries"]:
        if entry["message_key"] not in source_keys:
            errors.append(f"mapping {entry['source_id']}: unknown message key")
        for path in entry["catalogs"]:
            if not (ROOT / path).is_file():
                errors.append(f"mapping {entry['source_id']}: missing catalog {path}")
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
    return errors

def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: locale registry, catalogs, mappings, and manifests are consistent")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
