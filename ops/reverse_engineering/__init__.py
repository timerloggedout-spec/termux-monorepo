"""Reverse Engineering category — taxonomies and utility belts.

re-taxonomy/v1 (taxonomy.json + taxonomy.py) is the category's
polyhierarchy: categories/tools placed once, overlap as parents+tags,
toolchains as stage handoffs. The web family lives in the Foundry
sub-registry (ops/web_adapter_foundry/taxonomy.json); the APK belt in
ops/web_adapter_foundry/apk_xref.py. Doc: docs/ops/REVERSE-ENGINEERING-TAXONOMY.md.
"""
from .taxonomy import load_taxonomy, validate, node, toolchain

__all__ = ["load_taxonomy", "validate", "node", "toolchain"]
