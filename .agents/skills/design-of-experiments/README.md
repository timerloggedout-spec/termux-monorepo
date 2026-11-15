# Design of Experiments — source package

Version 1.0.0. Original implementation and instructional synthesis; not a copied third-party skill. MIT license applies to this package's original material. External sources retain their own rights. No claim of expert certification or production validation.

## Install
Unpack the archive and keep the `design-of-experiments` directory intact. Put that directory in your agent host's documented skill location, or import the `.skill` archive if the host supports it. Installation paths and archive import support vary by host. `SKILL.md` is the entry point; schemas and evals are package conventions, not mandatory Agent Skills fields.

```bash
cd design-of-experiments
python -m venv .venv
# Activate the environment using your operating system's command.
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/generate_design.py --config examples/fractional.json --out experiment
python scripts/validate_design.py --csv experiment/run-sheet.csv --config examples/fractional.json --out experiment/recheck.json
python scripts/package_skill.py --out-dir ../dist
```

Requirements are minimum versions, not a fully pinned cross-platform lockfile. Generation records installed versions; create and test a deployment lockfile before operational use.

## Scope
The CLI supports continuous numeric factors only; all designs assume independent experimental units and unrestricted randomization. Supports two-level full factorials, regular fractions with explicit generators, face-centered CCD (at least two factors), and Box-Behnken (at least three factors). At most 12 total factors and 100,000 proposed runs are accepted. No D-optimal search, blocked schedule generation, mixture generator, mixed-model fitter, general power calculator, or automated interpretation of real outcomes is claimed.

The configuration's model determines the audit, not an automatic design choice. Rank-deficient designs are written for inspection, flagged `release_ready: false`, and return exit status 2. Validation schema or malformed-file errors return nonzero. `release_ready` means the implemented numerical checks pass, not approval to conduct the experiment.

## Interfaces
- Input: JSON config under schemas/design-config.schema.json.
- Output CSV: `run_id`, `std_order`, `replicate`, `point_type`, `x_<factor>` coded columns, and natural-unit `<factor>` columns. Repeated centers have replicate=0.
- Audit: schemas/audit.schema.json; no response outcomes are needed for design auditing.
- Generation provenance: config.json and manifest.json; CSV SHA-256 is recorded.
- Model terms: intercept; main effects; unique pairwise products for `two-factor`; those plus squares for `quadratic`.
- Correlations are uncentered normalized column dot products. They indicate exact proportionality or near-collinearity, not general confounding decomposition.

## Development
`schemas/frontmatter.schema.json` is a local strict schema for the documented portable fields. `scripts/check_package.py` checks frontmatter, name/directory agreement, and relative Markdown file references. Use the Agent Skills reference validator separately for independent conformance checks when available.

`tests/` contains executable numerical tests. `evals/evals.json` contains agent-level behavioral prompts, expected outcomes, and assertions. These are not automatically graded by unittest. Compare independent skill-enabled runs with a no-skill baseline, review scientific correctness, and report failures before calling the skill benchmarked.

## Packaging
`package_skill.py` first runs local integrity checks, then creates a ZIP-format `.skill` and a `.zip` with one top-level directory. It excludes caches, virtual environments, tests' temporary products, and generated experiment directories by including only documented source directories/files. It is a local packager, not Anthropic's official packager. For a target host, additionally validate using its current official tooling. The `.skill` extension alone does not ensure host compatibility.

See DIRECTORY-TREE.txt for the complete resource layout and BUILD-REPORT.json for tests actually run during delivery.
