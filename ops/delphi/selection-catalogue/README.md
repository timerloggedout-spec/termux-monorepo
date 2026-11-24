# Delphi Oracle Selection Catalogue

The catalogue contract is `selection-catalogue.json`. Each selected intake revision is stored as an immutable JSON record under:

`selection-catalogue/<selection_id>/<record_sha256>.json`

Each record carries its source issue, selected research cohort, methodology, Question Matrix configuration, reconciliation scope, panel, disposition, and `execution: false`.

Catalogue entries land through per-selection pull requests to `master`. The directory structure keeps concurrent selections isolated and preserves prior revisions. Research comparisons remain within their registered segments.
