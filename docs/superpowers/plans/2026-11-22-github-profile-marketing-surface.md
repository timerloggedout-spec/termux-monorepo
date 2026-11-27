# GitHub Profile Marketing Surface — Implementation Plan

Date: 2026-11-22
Proposal: github-profile-marketing-surface
Branch: feat/github-profile-marketing-surface-20261122

## Outcome

Generate a polished GitHub profile README and custom SVG displays from existing Termux MonoRepo marketing sources. Keep weekly partner spotlight selection deterministic and source-backed. Run refresh through GitHub Actions.

## Tasks

1. Add profile.json with presentation settings, selected video IDs, featured project links, and source paths.
2. Implement a stdlib-only renderer that parses active partner rows and curated video rows.
3. Generate README.md, hero.svg, highlights.svg, and partner-spotlight.svg.
4. Add tests for source parsing, deterministic weekly rotation, unverified-offer suppression, and output generation.
5. Add a weekly/manual refresh workflow that opens a PR only when generated output changes.
6. Record the missing same-name profile repository as a publication blocker.

## Validation

- python3 -m unittest discover -s scripts/marketing/tests -p 'test_*.py' -v
- python3 scripts/marketing/render_github_profile.py --root . --output marketing/github-profile/generated
- git diff --check
- python3 scripts/ci/repo_gate.py
- python3 scripts/ci/termux_smoke.py

## Acceptance

- The README links to the YouTube channel, video gallery, Termux MonoRepo, and public landing page.
- The curated set includes a latest Short and an explicitly tagged hackathon demo.
- One active partner is featured per ISO week; unsupported offer claims are omitted.
- Three static SVG assets render with escaped text.
- Weekly refresh creates an auditable PR when output changes.
- Profile-repository publication stays blocked until the same-name public repository is provisioned.
