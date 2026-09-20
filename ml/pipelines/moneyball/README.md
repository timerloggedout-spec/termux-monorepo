# Moneyball scorer

Ranks PRs into `promote | wait | hold | extract | observe` using transparent
weights. No model weights files, no GPU, no secrets.

Dirty mega-PRs (`changed_files > 40` + `mergeable_dirty`) land in EXTRACT.
