# Siglary Census Workflow Specification (Item 5)

Path to deploy by Operator/Desk: `.github/workflows/siglary-census.yml`

```yaml
name: siglary-census

on:
  push:
    branches: [master]
    paths:
      - 'skills/**'
      - '**/SKILL.md'
      - '**/*.SKILLS'
      - '**/SKILLS.md'
      - 'docs/icm/**'
      - 'CLAUDE.md'
      - '**/CLAUDE.md'
      - 'scripts/siglary/**'
  schedule:
    - cron: '15 3 * * 1'
  workflow_dispatch:

concurrency:
  group: siglary-census
  cancel-in-progress: false

permissions:
  contents: write

jobs:
  census:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Mint Swarm App token
        id: app
        uses: actions/create-github-app-token@b60ed23e06e1e229cd0384bf542ad2781a8df21e
        with:
          app-id: ${{ vars.TERMUX_FLEET_SWARM_APP_ID }}
          private-key: ${{ secrets.TERMUX_FLEET_SWARM_PRIVATE_KEY }}
      - uses: actions/checkout@v4
        with:
          token: ${{ steps.app.outputs.token }}
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Run Siglary census validator
        run: |
          python3 scripts/siglary/siglary_validate.py
      - name: Commit census outputs and compliance feed (only on change)
        run: |
          git config user.name "termux-fleet-swarm[bot]"
          git config user.email "termux-fleet-swarm[bot]@users.noreply.github.com"
          git add ops/linguist/siglary/ ops/linguist/siglary-compliance-feed.jsonl
          if git diff --cached --quiet; then
            echo "siglary census unchanged; no commit"
          else
            git commit -m "chore(siglary): run automated census and update compliance feed"
            for attempt in 1 2 3; do
              if git push origin master; then
                break
              fi
              echo "push rejected (attempt $attempt) — rebasing"
              git pull --rebase origin master
            done
          fi
```
