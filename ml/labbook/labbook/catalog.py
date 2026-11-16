"""The catalog (ledger row 8).

A named catalog maps every dataset/model name -> {kind, format, location?,
reader?}. Nodes name datasets; they never touch a path or a format.
Infrastructure bindings are data, resolved per run and stamped on the run
record. Fully-qualified names are accepted everywhere, and
`labbook catalog list` exists from day one (Kedro's missing verb is our
day-one verb).
"""

import os

from . import formats, yamlmini
from .errors import LabbookError

KINDS = ("dataset", "model", "metrics", "report")


class Catalog:
    def __init__(self, entries: dict, source: str = "<memory>"):
        self.entries = entries
        self.source = source

    @classmethod
    def load(cls, path: str) -> "Catalog":
        with open(path) as f:
            raw = yamlmini.load(f.read())
        return cls.from_dict(raw or {}, source=path)

    @classmethod
    def from_dict(cls, raw: dict, source: str = "<memory>") -> "Catalog":
        entries = {}
        for name, spec in raw.items():
            if not isinstance(spec, dict):
                raise LabbookError(
                    "catalog entry is not a mapping",
                    value={name: spec},
                    expected="{kind, format, location?, reader?}",
                    fix=f"fix the entry for {name!r} in the catalog",
                )
            kind = spec.get("kind")
            fmt = spec.get("format")
            if kind not in KINDS:
                raise LabbookError(
                    "catalog entry has an unknown kind",
                    value={"asset": name, "kind": kind},
                    expected=f"one of {KINDS}",
                )
            formats.reader_path(fmt)  # raises, naming the format, if unknown
            entries[name] = {
                "kind": kind,
                "format": fmt,
                "location": spec.get("location"),
                "reader": spec.get("reader") or formats.reader_path(fmt),
            }
        return cls(entries, source=source)

    def __contains__(self, name):
        return name in self.entries

    def __getitem__(self, name):
        try:
            return self.entries[name]
        except KeyError:
            raise LabbookError(
                "asset is not in the catalog",
                value=name,
                expected=f"one of {sorted(self.entries)}",
                fix="declare the asset in catalog.yml; nodes name catalog "
                "assets only (row 8)",
            ) from None

    def list(self):
        """The day-one verb: every asset with its binding, sorted."""
        return [
            {"name": name, **self.entries[name]}
            for name in sorted(self.entries)
        ]

    def resolve_location(self, name, project_dir):
        loc = self.entries[name].get("location")
        if loc is None:
            return None
        return loc if os.path.isabs(loc) else os.path.join(project_dir, loc)
