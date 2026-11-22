# GitHub profile marketing surface

## Objective

Treat the GitHub profile as a public discovery and conversion surface. Present verified engineering work, public demos, hackathon highlights, and one rotating partner destination in a compact profile README.

## Canonical inputs

- Partner names, offers and active referral URLs: docs/PARTNERS.md.
- Curated public Shorts and demos: docs/ops/PUBLIC-VIDEO-LIBRARY-2026-11-15.md.
- Public identity conventions: docs/ops/PROFILE-REGISTRY.md.
- Public landing and video gallery: https://timerloggedout-spec.github.io/ and https://timerloggedout-spec.github.io/videos.html.

The profile renderer consumes these sources. It does not create a parallel partner registry or video catalogue.

## Rotation model

The profile spotlight rotates weekly across the active partner rows in docs/PARTNERS.md. Selection uses the ISO year/week and the source row order, making the result deterministic and reproducible. The renderer displays one partner destination at a time and preserves a referral disclosure.

This is a presentation rotation. Existing scripts/referral/rotate.py remains the authority for rotating exhausted referral codes inside an individual programme. Existing referral-rotation and referral-pool-watch workflows retain their sensor and pool responsibilities.

Unverified offer claims are omitted from the spotlight. The partner name, category and source URL remain attributable to docs/PARTNERS.md.

## Content model

- Latest Short: selected from the canonical video library.
- Hackathon highlight: explicitly tagged by video ID in profile.json; title and URL are resolved from the canonical video library, with submission provenance cross-checked against ops/challenge/coordinator.json and docs/ops/CHALLENGE-ENTRIES-LOG.md.
- StudySprint's v0.2.0 demo (eFXyOYTpuvg) is the recorded D1 submission video; the earlier Strands SDK demo is superseded for submission purposes.
- Product/demo highlights: selected from the same video library.
- Featured projects: link to existing public project and landing surfaces.
- Custom displays: static SVGs generated from the profile data; no scripts, remote execution or live telemetry claims.

## Refresh routine

A weekly GitHub Actions schedule and workflow_dispatch both regenerate the profile projection. Relevant source changes also trigger refresh. The workflow runs focused tests and creates a reviewable PR when generated output changes.

The first phase stores the generated README and SVGs in this repository. Profile publication is enabled after the special same-name repository exists and an approved cross-repository publishing credential is available.

## Publication boundary

The authenticated GitHub account is timerloggedout-spec. A repository named timerloggedout-spec/timerloggedout-spec currently returns 404. The existing timerloggedout-spec.github.io repository is the marketing site and does not satisfy GitHub's same-name profile README convention.

The browser automation profile has no recorded GitHub sign-in. Repository creation and any browser-mediated sign-in remain an explicit owner step. The generated package remains reviewable in Termux MonoRepo meanwhile.
