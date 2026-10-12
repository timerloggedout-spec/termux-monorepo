# Image asset pipeline (README / docs)

**Purpose.** Fail-closed, repeatable optimization for any image that will be
embedded in `README.md`, `docs/**`, or public Pages/Vercel surfaces.

**Why this exists.** Issue #529 ATES asset was corrupt on both Drive and GitHub
user-attachments (same md5). Agents must **validate full decode** before
embedding. Size targets keep the monorepo lean.

## Tool

```bash
python3 scripts/ops/optimize_readme_image.py INPUT -o OUTPUT \
  [--max-width 720] [--max-bytes 400000] [--format png|jpeg] [--quality 85] [--json]
```

| Exit | Meaning |
|------|---------|
| 0 | OK — output validated |
| 2 | Source missing / unreadable |
| 3 | **Source corrupt** — do not embed |
| 4 | Could not meet `--max-bytes` |

## Defaults (README attention / hero)

| Knob | Default | Rationale |
|------|---------|-----------|
| max-width | 720 | Readable on GitHub README without horizontal scroll |
| max-bytes | 400000 | Keeps clone/diff light; raise only with justification |
| format | png | Prefer jpeg when no transparency needed |

## Agent checklist (repeatable)

1. **Obtain source** (Drive, export, design tool). Prefer operator-confirmed clean file.
2. **Validate** with the script (or `python3 -c "from PIL import Image; Image.open(p).load()"`).
3. If exit **3** → stop. Comment on the tracking issue with md5 + error. Do **not** embed.
4. If OK → run optimize → commit under `docs/assets/` (never dump multi-MB binaries at repo root).
5. Point README `<img src="docs/assets/...">` at the optimized path; keep full-res on Drive if needed.
6. Cite `Implements: #529` (or relevant issue) on the PR.

## Layout

```
docs/assets/                 # committed, optimized embeds only
scripts/ops/optimize_readme_image.py
docs/ops/IMAGE-ASSET-PIPELINE.md   # this file
```

## ATES status (2026-09-15)

| Asset | Status |
|-------|--------|
| Drive `1NfDzhjnY9Bc419gIRYgnUCpJdlL30hgD` | **Corrupt** (truncated IDAT; md5 `11141c4303e5eeb596dde7d4425fb411`) |
| GH attachments `af8b1ad6…` / `c4e2b99c…` | Same bytes as Drive |
| `docs/assets/ates-attention-placeholder.svg` | **Valid** generated SVG placeholder until clean art lands |

When a clean ATES export is available:

```bash
python3 scripts/ops/optimize_readme_image.py /path/to/clean.png \
  -o docs/assets/ates-benchmarking-framework.png --max-width 720 --max-bytes 400000
# then point README <img src="docs/assets/ates-benchmarking-framework.png"> and retire the SVG placeholder
```

## Related

- #529 Visuals / README engagement
- `docs/DEPLOYMENT-LANES.md` — public surfaces
- `docs/ops/SKILLS-INVENTORY.md` — ops skills
