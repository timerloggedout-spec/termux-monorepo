# RECON checklist

- Resolve candidate/base refs to immutable SHAs.
- Capture UTC timestamps.
- Compute merge-base, ahead/behind, and changed paths.
- Re-fetch current PR reviews, review threads, checks, and workflow runs.
- Distinguish current evidence from stale/outdated evidence.
- Classify provider quota/rate-limit/outage separately from repository failure.
- Preserve generated evidence before any rotation.
- If graph is behind/diverged or evidence is non-terminal, stop and iterate.
