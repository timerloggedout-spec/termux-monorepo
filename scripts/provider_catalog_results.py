"""List-compatible poll results with non-fatal row diagnostics."""
from __future__ import annotations


class CatalogRows(list):
    def __init__(self, rows=(), diagnostics=()):
        super().__init__(rows)
        self.diagnostics = list(diagnostics)
