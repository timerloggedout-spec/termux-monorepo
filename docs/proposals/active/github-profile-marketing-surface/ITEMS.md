# ITEMS — github-profile-marketing-surface

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| GPM-001 | Render a profile README from canonical partner and public-video sources | executing | Generated README reflects current docs/PARTNERS.md and PUBLIC-VIDEO-LIBRARY |
| GPM-002 | Rotate one featured active partner on a deterministic weekly cadence | executing | Same ISO week selects same partner; next week advances; inactive rows are excluded |
| GPM-003 | Generate custom static SVG profile displays | executing | Hero, highlight and referral spotlight SVGs render from validated source data |
| GPM-004 | Add scheduled and manually dispatchable refresh workflow with tests | executing | Weekly workflow validates and opens a reviewable PR only when generated output changes |
| GPM-005 | Publish the generated README and displays to the GitHub profile repository | blocked | Requires public repository timerloggedout-spec/timerloggedout-spec and cross-repository write capability |
